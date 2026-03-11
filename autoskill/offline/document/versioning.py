"""
LLM-driven registry/version registration stage for the skill-first offline document pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import uuid
from typing import Any, Dict, List, Optional, Sequence, Set

from autoskill import AutoSkill
from autoskill.llm.base import LLM
from autoskill.llm.factory import build_llm
from autoskill.utils.time import now_iso

from .common import StageLogger, emit_stage_log
from .compiler import _build_structured_prompt, _coerce_examples, skill_spec_to_candidate
from .llm_utils import (
    coerce_str_list,
    compact_text_list,
    llm_complete_json,
    maybe_json_dict,
)
from .models import (
    DocumentRecord,
    SkillLifecycle,
    SkillSpec,
    SupportRecord,
    SupportRelation,
    VersionState,
)
from .prompt_runtime import activate_offline_prompt_runtime
from .registry import DocumentRegistry

_ACTIVE_STORE_STATES = {
    VersionState.CANDIDATE,
    VersionState.DRAFT,
    VersionState.EVALUATING,
    VersionState.ACTIVE,
    VersionState.WATCHLIST,
}


def _bump_patch(version: str) -> str:
    """Bumps a semantic version patch number."""

    parts = [p for p in str(version or "").split(".") if p.strip().isdigit()]
    if len(parts) != 3:
        return "0.1.1"
    major, minor, patch = (int(parts[0]), int(parts[1]), int(parts[2]))
    return f"{major}.{minor}.{patch + 1}"


def _plain_skill(skill: Any) -> Dict[str, Any]:
    """Serializes one persisted AutoSkill store record into a compact dict."""

    return {
        "id": str(getattr(skill, "id", "") or ""),
        "name": str(getattr(skill, "name", "") or ""),
        "description": str(getattr(skill, "description", "") or ""),
        "version": str(getattr(skill, "version", "") or ""),
        "status": str(getattr(getattr(skill, "status", None), "value", getattr(skill, "status", "")) or ""),
    }


def _copy_skill(
    skill: SkillSpec,
    *,
    skill_id: Optional[str] = None,
    version: Optional[str] = None,
    status: Optional[VersionState] = None,
    support_ids: Optional[List[str]] = None,
    metadata_update: Optional[Dict[str, Any]] = None,
) -> SkillSpec:
    """Creates a skill copy with updated identity/version/status fields."""

    payload = skill.to_dict()
    if skill_id is not None:
        payload["skill_id"] = str(skill_id or "").strip()
    if version is not None:
        payload["version"] = str(version or "0.1.0")
    if status is not None:
        payload["status"] = status.value
    if support_ids is not None:
        payload["support_ids"] = list(support_ids or [])
    md = dict(payload.get("metadata") or {})
    if metadata_update:
        md.update(dict(metadata_update or {}))
    payload["metadata"] = md
    return SkillSpec.from_dict(payload)


def _copy_support(
    support: SupportRecord,
    *,
    skill_id: str,
    relation_type: Optional[SupportRelation] = None,
    metadata_update: Optional[Dict[str, Any]] = None,
) -> SupportRecord:
    """Creates a support copy rebound to one canonical skill id."""

    payload = support.to_dict()
    payload["skill_id"] = str(skill_id or "").strip()
    if relation_type is not None:
        payload["relation_type"] = relation_type.value
    md = dict(payload.get("metadata") or {})
    if metadata_update:
        md.update(dict(metadata_update or {}))
    payload["metadata"] = md
    return SupportRecord.from_dict(payload)


def _same_asset_layer(left: SkillSpec, right: SkillSpec) -> bool:
    """Checks whether two skills live at the same asset type and granularity."""

    return (
        str(left.asset_type or "").strip() == str(right.asset_type or "").strip()
        and str(left.granularity or "").strip() == str(right.granularity or "").strip()
    )


def _granularity_rank(value: str) -> int:
    """Maps granularity labels into a stable coarse-to-fine rank."""

    raw = str(value or "").strip().lower()
    if raw == "macro":
        return 0
    if raw == "micro":
        return 2
    return 1


def _doc_ids_from_support_ids(support_ids: Sequence[str], support_by_id: Dict[str, SupportRecord]) -> List[str]:
    """Collects source document ids for one support reference set."""

    seen = set()
    out: List[str] = []
    for support_id in support_ids or []:
        support = support_by_id.get(str(support_id or "").strip())
        if support is None:
            continue
        doc_id = str(support.doc_id or "").strip()
        if not doc_id or doc_id in seen:
            continue
        seen.add(doc_id)
        out.append(doc_id)
    return out


def _conflicting_support_ids(support_ids: Sequence[str], support_by_id: Dict[str, SupportRecord]) -> List[str]:
    """Collects support ids explicitly marked as conflicts."""

    out: List[str] = []
    seen = set()
    for support_id in support_ids or []:
        support = support_by_id.get(str(support_id or "").strip())
        if support is None or support.relation_type != SupportRelation.CONFLICT:
            continue
        if support.support_id in seen:
            continue
        seen.add(support.support_id)
        out.append(support.support_id)
    return out


def _support_lookup(
    registry: DocumentRegistry,
    support_records: Sequence[SupportRecord],
) -> Dict[str, SupportRecord]:
    """Builds a combined support index from registry state and the current batch."""

    out = {support.support_id: support for support in registry.list_supports()}
    for support in support_records or []:
        out[support.support_id] = support
    return out


@dataclass
class ChangeDecision:
    """Decision returned by LLM-backed skill change classification."""

    action: str
    skill: SkillSpec
    matched_skill_ids: List[str] = field(default_factory=list)
    reason: str = ""
    split_parent_id: str = ""


@dataclass
class VersionRegistrationResult:
    """Output of the registry/version registration stage."""

    documents: List[DocumentRecord] = field(default_factory=list)
    support_records: List[SupportRecord] = field(default_factory=list)
    skill_specs: List[SkillSpec] = field(default_factory=list)
    lifecycles: List[SkillLifecycle] = field(default_factory=list)
    change_logs: List[Dict[str, Any]] = field(default_factory=list)
    version_history: List[Dict[str, Any]] = field(default_factory=list)
    provenance_links: List[Dict[str, Any]] = field(default_factory=list)
    upserted_store_skills: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    dry_run: bool = False


class VersionManager:
    """LLM-backed version and lifecycle manager for document builds."""

    def __init__(
        self,
        *,
        registry: DocumentRegistry,
        llm: LLM,
        logger: StageLogger = None,
    ) -> None:
        self.registry = registry
        self.llm = llm
        self.logger = logger

    def _skill_for_llm(self, skill: SkillSpec, *, support_by_id: Dict[str, SupportRecord]) -> Dict[str, Any]:
        return {
            "skill_id": skill.skill_id,
            "name": skill.name,
            "description": skill.description,
            "prompt": skill.skill_body,
            "asset_type": skill.asset_type,
            "granularity": skill.granularity,
            "objective": skill.objective,
            "domain": skill.domain,
            "task_family": skill.task_family,
            "method_family": skill.method_family,
            "stage": skill.stage,
            "applicable_signals": list(skill.applicable_signals or []),
            "contraindications": list(skill.contraindications or []),
            "intervention_moves": list(skill.intervention_moves or []),
            "triggers": list(skill.triggers or []),
            "workflow_steps": list(skill.workflow_steps or []),
            "constraints": list(skill.constraints or []),
            "cautions": list(skill.cautions or []),
            "output_contract": list(skill.output_contract or []),
            "examples": [
                {
                    "input": str(example.input or ""),
                    "output": str(example.output or ""),
                    "notes": str(example.notes or ""),
                }
                for example in list(skill.examples or [])
            ],
            "tags": list(skill.tags or []),
            "support_ids": list(skill.support_ids or []),
            "support_excerpt_summaries": [
                {
                    "support_id": support.support_id,
                    "relation_type": support.relation_type.value,
                    "section": support.section,
                    "excerpt": support.excerpt,
                }
                for support_id in list(skill.support_ids or [])
                for support in [support_by_id.get(str(support_id or "").strip())]
                if support is not None
            ],
            "version": skill.version,
            "status": skill.status.value,
            "metadata": dict(skill.metadata or {}),
        }

    def _resolved_skill(self, raw: Any, *, fallback: SkillSpec) -> SkillSpec:
        item = maybe_json_dict(raw)
        if not item:
            return fallback
        prompt = str(item.get("prompt") or item.get("skill_body") or fallback.skill_body).strip()
        intervention_moves = compact_text_list(coerce_str_list(item.get("intervention_moves")), limit=12) or list(
            fallback.intervention_moves or []
        )
        workflow_steps = compact_text_list(coerce_str_list(item.get("workflow_steps")), limit=12) or list(fallback.workflow_steps or [])
        constraints = compact_text_list(coerce_str_list(item.get("constraints")), limit=12) or list(fallback.constraints or [])
        cautions = compact_text_list(coerce_str_list(item.get("cautions")), limit=12) or list(fallback.cautions or [])
        applicable_signals = compact_text_list(coerce_str_list(item.get("applicable_signals")), limit=12) or list(
            fallback.applicable_signals or []
        )
        contraindications = compact_text_list(coerce_str_list(item.get("contraindications")), limit=12) or list(
            fallback.contraindications or []
        )
        output_contract = compact_text_list(coerce_str_list(item.get("output_contract")), limit=12) or list(
            fallback.output_contract or []
        )
        examples = _coerce_examples(item.get("examples")) or list(fallback.examples or [])
        if not prompt or (not workflow_steps and not intervention_moves and not constraints and not cautions):
            return fallback
        objective = str(item.get("objective") or fallback.objective or fallback.description).strip()
        structured_prompt = _build_structured_prompt(
            prompt=prompt,
            objective=objective,
            applicable_signals=applicable_signals,
            contraindications=contraindications,
            intervention_moves=intervention_moves,
            workflow_steps=workflow_steps,
            constraints=constraints,
            cautions=cautions,
            output_contract=output_contract,
            examples=examples,
        )
        return SkillSpec(
            skill_id=fallback.skill_id,
            name=str(item.get("name") or fallback.name).strip(),
            description=str(item.get("description") or fallback.description).strip(),
            skill_body=structured_prompt,
            asset_type=str(item.get("asset_type") or fallback.asset_type).strip(),
            granularity=str(item.get("granularity") or fallback.granularity).strip(),
            objective=objective,
            domain=str(item.get("domain") or fallback.domain).strip(),
            task_family=str(item.get("task_family") or fallback.task_family).strip(),
            method_family=str(item.get("method_family") or fallback.method_family).strip(),
            stage=str(item.get("stage") or fallback.stage).strip(),
            applicable_signals=applicable_signals,
            contraindications=contraindications,
            intervention_moves=intervention_moves,
            triggers=compact_text_list(coerce_str_list(item.get("triggers")), limit=5) or list(fallback.triggers or []),
            workflow_steps=workflow_steps,
            constraints=constraints,
            cautions=cautions,
            output_contract=output_contract,
            examples=examples,
            tags=compact_text_list(coerce_str_list(item.get("tags")), limit=6) or list(fallback.tags or []),
            support_ids=compact_text_list(coerce_str_list(item.get("support_ids")), limit=64)
            or list(fallback.support_ids or []),
            metadata={
                **dict(fallback.metadata or {}),
                "files": maybe_json_dict(item.get("files")) or maybe_json_dict((fallback.metadata or {}).get("files")),
                "resources": maybe_json_dict(item.get("resources")) or maybe_json_dict((fallback.metadata or {}).get("resources")),
                "llm_reason": str(item.get("reason") or "").strip(),
            },
            version=fallback.version,
            status=fallback.status,
        )

    def classify_change(
        self,
        skill: SkillSpec,
        *,
        peer_skills: Sequence[SkillSpec],
        existing_skills: Sequence[SkillSpec],
        support_by_id: Dict[str, SupportRecord],
    ) -> ChangeDecision:
        """Uses an LLM to classify how one candidate should affect registry state."""

        payload = {
            "candidate_skill": self._skill_for_llm(skill, support_by_id=support_by_id),
            "peer_candidates": [
                self._skill_for_llm(peer, support_by_id=support_by_id)
                for peer in list(peer_skills or [])
                if peer.skill_id != skill.skill_id
            ][:8],
            "existing_skills": [
                self._skill_for_llm(existing, support_by_id=support_by_id)
                for existing in list(existing_skills or [])
            ][:12],
        }
        system = (
            "You are AutoSkill's Document Skill Version Manager.\n"
            "Task: decide how one candidate document skill should update the registry.\n"
            "Output ONLY strict JSON parseable by json.loads.\n"
            "Actions:\n"
            "- create: a new distinct capability\n"
            "- strengthen: same capability, mostly stronger evidence or minor additive guidance\n"
            "- revise: same capability, materially updated instructions or constraints\n"
            "- merge: candidate should merge into one or more existing skills and may deprecate overlapping older skills\n"
            "- split: candidate is one child workflow split out from an older broader parent skill\n"
            "- unchanged: candidate does not materially change the existing skill\n"
            "- discard: do not persist candidate\n"
            "Rules:\n"
            "- Decide from semantic capability identity, not lexical similarity.\n"
            "- Do not merge, strengthen, revise, or mark unchanged across different asset_type or granularity.\n"
            "- Treat macro_protocol, session_skill, micro_skill, safety_rule, and knowledge_reference as different asset layers unless there is an explicit split relationship.\n"
            "- Use peer_candidates to detect split cases where multiple narrower candidates replace one broad existing skill.\n"
            "- Use support conflict evidence to avoid preserving outdated or unsafe guidance.\n"
            "- If action is strengthen/revise/unchanged/split, target_skill_ids should contain exactly one existing skill id.\n"
            "- If action is merge, target_skill_ids may contain one or more existing skill ids.\n"
            "- Provide resolved_skill when action is strengthen/revise/merge/unchanged and when rewriting the candidate makes the result clearer.\n"
            "Return schema:\n"
            "{\n"
            '  "action": "create"|"strengthen"|"revise"|"merge"|"split"|"unchanged"|"discard",\n'
            '  "target_skill_ids": ["..."],\n'
            '  "reason": "short reason",\n'
            '  "resolved_skill": {optional canonical skill payload}\n'
            "}\n"
        )
        repair_system = (
            "You are a JSON output fixer for document skill version decisions.\n"
            "Given DATA and DRAFT, output ONLY strict JSON with fields action, target_skill_ids, reason, resolved_skill.\n"
        )
        repaired_payload = (
            f"DATA:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            "DRAFT:\n__DRAFT__"
        )
        parsed = llm_complete_json(
            llm=self.llm,
            system=system,
            payload=payload,
            repair_system=repair_system,
            repair_payload=repaired_payload,
        )
        obj = maybe_json_dict(parsed)
        action = str(obj.get("action") or "").strip().lower()
        if action not in {"create", "strengthen", "revise", "merge", "split", "unchanged", "discard"}:
            action = "create"
        matched = compact_text_list(coerce_str_list(obj.get("target_skill_ids")), limit=8)
        resolved = self._resolved_skill(obj.get("resolved_skill"), fallback=skill)
        reason = str(obj.get("reason") or "").strip() or action
        existing_by_id = {existing.skill_id: existing for existing in list(existing_skills or [])}
        matched_existing = [existing_by_id[skill_id] for skill_id in matched if skill_id in existing_by_id]
        if action in {"strengthen", "revise", "merge", "unchanged"} and matched_existing:
            if any(not _same_asset_layer(resolved, existing) for existing in matched_existing):
                action = "create"
                matched = []
                reason = "create (cross-layer merge blocked)"
        if action == "split" and matched_existing:
            parent = matched_existing[0]
            if _granularity_rank(resolved.granularity) <= _granularity_rank(parent.granularity):
                action = "create"
                matched = []
                reason = "create (split requires narrower child)"
        return ChangeDecision(
            action=action,
            skill=resolved,
            matched_skill_ids=matched,
            reason=reason,
            split_parent_id=(matched[0] if action == "split" and matched else ""),
        )

    def create_new_version(self, *, current_version: str, action: str) -> str:
        """Creates the next version string for one lifecycle action."""

        action_s = str(action or "").strip().lower()
        if action_s in {"", "create"}:
            return str(current_version or "").strip() or "0.1.0"
        if action_s == "unchanged":
            return str(current_version or "").strip() or "0.1.0"
        return _bump_patch(str(current_version or "").strip() or "0.1.0")

    def update_lifecycle(
        self,
        *,
        skill_id: str,
        current_state: Optional[VersionState],
        action: str,
        target_state: VersionState,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SkillLifecycle:
        """Creates one lifecycle transition consistent with the requested action."""

        action_s = str(action or "").strip().lower()
        if action_s == "deprecate":
            next_state = (
                target_state
                if target_state in {VersionState.WATCHLIST, VersionState.DEPRECATED, VersionState.RETIRED}
                else VersionState.DEPRECATED
            )
        else:
            next_state = target_state
        from_state = current_state if current_state is not None and current_state != next_state else None
        return SkillLifecycle(
            lifecycle_id=str(uuid.uuid4()),
            skill_id=str(skill_id or "").strip(),
            from_state=from_state,
            to_state=next_state,
            reason=action_s or "update",
            metadata=dict(metadata or {}),
        )

    def mark_deprecated(
        self,
        *,
        skill: SkillSpec,
        reason: str,
        state: VersionState = VersionState.DEPRECATED,
        related_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Marks one skill as deprecated/watchlist/retired."""

        related = list(related_ids or [])
        next_version = self.create_new_version(current_version=skill.version, action="deprecate")
        updated_skill = _copy_skill(
            skill,
            version=next_version,
            status=state,
            metadata_update={
                "change_action": "deprecate",
                "deprecation_reason": str(reason or "").strip(),
                "related_skill_ids": related,
            },
        )
        provenance = {
            "entity_type": "skill",
            "entity_id": updated_skill.skill_id,
            "doc_ids": [],
            "support_added": [],
            "support_conflicts": [],
            "related_entity_ids": related,
        }
        lifecycle = self.update_lifecycle(
            skill_id=updated_skill.skill_id,
            current_state=skill.status,
            action="deprecate",
            target_state=state,
            metadata={"reason": str(reason or "").strip(), "related_entity_ids": related},
        )
        change_log = self._change_payload(
            entity_type="skill",
            entity_id=updated_skill.skill_id,
            action="deprecate",
            from_version=skill.version,
            to_version=updated_skill.version,
            from_state=skill.status.value,
            to_state=updated_skill.status.value,
            summary=str(reason or "").strip(),
            provenance=provenance,
            related_entity_ids=related,
        )
        history = self._history_payload(
            entity_type="skill",
            entity_id=updated_skill.skill_id,
            version=updated_skill.version,
            action="deprecate",
            status=updated_skill.status,
            related_entity_ids=related,
        )
        return {
            "skill": updated_skill,
            "lifecycle": lifecycle,
            "change_log": change_log,
            "version_history": history,
            "provenance_links": provenance,
        }

    def merge_skills(
        self,
        *,
        decision: ChangeDecision,
        skill: SkillSpec,
        existing_skills_by_id: Dict[str, SkillSpec],
        target_state: VersionState,
    ) -> Dict[str, Any]:
        """Merges multiple existing skills into one updated primary skill."""

        matched_ids = [skill_id for skill_id in decision.matched_skill_ids if skill_id in existing_skills_by_id]
        primary_existing = existing_skills_by_id[matched_ids[0]]
        secondary_existing = [existing_skills_by_id[skill_id] for skill_id in matched_ids[1:]]
        next_version = self.create_new_version(current_version=primary_existing.version, action="merge")
        merged_skill = _copy_skill(
            skill,
            skill_id=primary_existing.skill_id,
            version=next_version,
            status=target_state,
            support_ids=list(primary_existing.support_ids or []) + list(skill.support_ids or []),
            metadata_update={
                "change_action": "merge",
                "merged_from_skill_ids": [existing.skill_id for existing in secondary_existing],
                "llm_reason": decision.reason,
            },
        )
        deprecated_secondary = [
            self.mark_deprecated(
                skill=secondary,
                reason="merged_into_other_skill",
                state=VersionState.DEPRECATED,
                related_ids=[primary_existing.skill_id],
            )
            for secondary in secondary_existing
        ]
        return {
            "primary_skill": merged_skill,
            "secondary": deprecated_secondary,
        }

    def split_skill(
        self,
        *,
        parent_skill: SkillSpec,
        child_skills: Sequence[SkillSpec],
        target_state: VersionState,
    ) -> Dict[str, Any]:
        """Splits one existing skill into multiple more focused skills."""

        updated_children: List[SkillSpec] = []
        lifecycles: List[SkillLifecycle] = []
        change_logs: List[Dict[str, Any]] = []
        version_history: List[Dict[str, Any]] = []
        provenance_links: List[Dict[str, Any]] = []

        for child in list(child_skills or []):
            updated_child = _copy_skill(
                child,
                version="0.1.0",
                status=target_state,
                metadata_update={
                    "change_action": "split",
                    "split_from_skill_id": parent_skill.skill_id,
                },
            )
            updated_children.append(updated_child)
            lifecycles.append(
                self.update_lifecycle(
                    skill_id=updated_child.skill_id,
                    current_state=None,
                    action="split",
                    target_state=target_state,
                    metadata={"split_from_skill_id": parent_skill.skill_id},
                )
            )
            provenance = {
                "entity_type": "skill",
                "entity_id": updated_child.skill_id,
                "doc_ids": [],
                "support_added": list(updated_child.support_ids or []),
                "support_conflicts": [],
                "related_entity_ids": [parent_skill.skill_id],
            }
            provenance_links.append(provenance)
            version_history.append(
                self._history_payload(
                    entity_type="skill",
                    entity_id=updated_child.skill_id,
                    version=updated_child.version,
                    action="split",
                    status=updated_child.status,
                    related_entity_ids=[parent_skill.skill_id],
                )
            )
            change_logs.append(
                self._change_payload(
                    entity_type="skill",
                    entity_id=updated_child.skill_id,
                    action="split",
                    from_version="",
                    to_version=updated_child.version,
                    from_state="",
                    to_state=updated_child.status.value,
                    summary="split_from_existing_skill",
                    provenance=provenance,
                    related_entity_ids=[parent_skill.skill_id],
                )
            )

        deprecated_parent = self.mark_deprecated(
            skill=parent_skill,
            reason="split_into_more_specific_skills",
            state=VersionState.DEPRECATED,
            related_ids=[child.skill_id for child in updated_children],
        )
        return {
            "children": updated_children,
            "deprecated_parent": deprecated_parent,
            "lifecycles": lifecycles,
            "change_logs": change_logs,
            "version_history": version_history,
            "provenance_links": provenance_links,
        }

    def _change_payload(
        self,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        from_version: str,
        to_version: str,
        from_state: str,
        to_state: str,
        summary: str,
        provenance: Dict[str, Any],
        related_entity_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Builds one normalized change log payload."""

        return {
            "change_id": str(uuid.uuid4()),
            "entity_type": str(entity_type or "").strip(),
            "entity_id": str(entity_id or "").strip(),
            "action": str(action or "").strip(),
            "changed_at": now_iso(),
            "from_version": str(from_version or "").strip(),
            "to_version": str(to_version or "").strip(),
            "from_state": str(from_state or "").strip(),
            "to_state": str(to_state or "").strip(),
            "summary": str(summary or "").strip(),
            "related_entity_ids": list(related_entity_ids or []),
            "provenance": dict(provenance or {}),
        }

    def _history_payload(
        self,
        *,
        entity_type: str,
        entity_id: str,
        version: str,
        action: str,
        status: VersionState,
        related_entity_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Builds one normalized version history entry."""

        return {
            "entity_type": str(entity_type or "").strip(),
            "entity_id": str(entity_id or "").strip(),
            "version": str(version or "").strip(),
            "action": str(action or "").strip(),
            "changed_at": now_iso(),
            "status": status.value,
            "related_entity_ids": list(related_entity_ids or []),
        }

    def _conflict_review(
        self,
        *,
        existing_skill: SkillSpec,
        incoming_skills: Sequence[SkillSpec],
        support_by_id: Dict[str, SupportRecord],
    ) -> Dict[str, str]:
        """Asks the LLM whether incoming conflicting evidence should downgrade an existing skill."""

        payload = {
            "existing_skill": self._skill_for_llm(existing_skill, support_by_id=support_by_id),
            "incoming_skills": [
                self._skill_for_llm(skill, support_by_id=support_by_id)
                for skill in list(incoming_skills or [])
            ][:8],
        }
        system = (
            "You are AutoSkill's Document Conflict Judge.\n"
            "Task: decide whether new incoming document skills/support should keep, watchlist, or deprecate an existing skill.\n"
            "Output ONLY strict JSON parseable by json.loads.\n"
            "Use watchlist when conflict signals are meaningful but not strong enough for deprecation.\n"
            "Use deprecate when newer evidence materially contradicts or replaces the older skill's guidance.\n"
            "Return schema: {\"action\": \"keep\"|\"watchlist\"|\"deprecate\", \"reason\": \"short reason\"}\n"
        )
        repair_system = (
            "You are a JSON output fixer for document conflict review.\n"
            "Given DATA and DRAFT, output ONLY strict JSON with fields action and reason.\n"
        )
        repaired_payload = (
            f"DATA:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            "DRAFT:\n__DRAFT__"
        )
        parsed = llm_complete_json(
            llm=self.llm,
            system=system,
            payload=payload,
            repair_system=repair_system,
            repair_payload=repaired_payload,
        )
        obj = maybe_json_dict(parsed)
        action = str(obj.get("action") or "").strip().lower()
        if action not in {"keep", "watchlist", "deprecate"}:
            action = "keep"
        return {"action": action, "reason": str(obj.get("reason") or "").strip() or action}

    def reconcile(
        self,
        *,
        skills: Sequence[SkillSpec],
        support_records: Sequence[SupportRecord],
        target_state: VersionState,
    ) -> VersionRegistrationResult:
        """Reconciles one compiled batch against registry state."""

        result = VersionRegistrationResult(support_records=[], dry_run=False)
        support_by_id = _support_lookup(self.registry, support_records)
        existing_skills = list(self.registry.list_skills())
        existing_skills_by_id = {skill.skill_id: skill for skill in existing_skills}

        decisions = [
            self.classify_change(
                skill,
                peer_skills=skills,
                existing_skills=existing_skills,
                support_by_id=support_by_id,
            )
            for skill in list(skills or [])
        ]

        processed_split_parents: Set[str] = set()
        consumed_existing_ids: Set[str] = set()
        consumed_new_ids: Set[str] = set()
        incoming_support_by_id = {support.support_id: support for support in list(support_records or [])}

        for decision in [item for item in decisions if item.action == "merge" and item.matched_skill_ids]:
            new_skill = decision.skill
            application = self.merge_skills(
                decision=decision,
                skill=new_skill,
                existing_skills_by_id=existing_skills_by_id,
                target_state=target_state,
            )
            merged_skill = application["primary_skill"]
            bound_supports = [
                _copy_support(support, skill_id=merged_skill.skill_id)
                for support in list(incoming_support_by_id.values())
                if support.support_id in set(new_skill.support_ids or [])
            ]
            merged_skill = _copy_skill(
                merged_skill,
                support_ids=list(dict.fromkeys(list(merged_skill.support_ids or []) + [support.support_id for support in bound_supports])),
                metadata_update={"llm_reason": decision.reason},
            )
            provenance = {
                "entity_type": "skill",
                "entity_id": merged_skill.skill_id,
                "doc_ids": _doc_ids_from_support_ids(merged_skill.support_ids, support_by_id),
                "support_added": [support.support_id for support in bound_supports],
                "support_conflicts": _conflicting_support_ids(merged_skill.support_ids, support_by_id),
                "related_entity_ids": decision.matched_skill_ids,
            }
            result.skill_specs.append(merged_skill)
            result.support_records.extend(bound_supports)
            result.lifecycles.append(
                self.update_lifecycle(
                    skill_id=merged_skill.skill_id,
                    current_state=existing_skills_by_id[merged_skill.skill_id].status,
                    action="merge",
                    target_state=target_state,
                    metadata={"merged_from_skill_ids": decision.matched_skill_ids, "llm_reason": decision.reason},
                )
            )
            result.provenance_links.append(provenance)
            result.change_logs.append(
                self._change_payload(
                    entity_type="skill",
                    entity_id=merged_skill.skill_id,
                    action="merge",
                    from_version=existing_skills_by_id[merged_skill.skill_id].version,
                    to_version=merged_skill.version,
                    from_state=existing_skills_by_id[merged_skill.skill_id].status.value,
                    to_state=merged_skill.status.value,
                    summary=decision.reason,
                    provenance=provenance,
                    related_entity_ids=decision.matched_skill_ids,
                )
            )
            result.version_history.append(
                self._history_payload(
                    entity_type="skill",
                    entity_id=merged_skill.skill_id,
                    version=merged_skill.version,
                    action="merge",
                    status=merged_skill.status,
                    related_entity_ids=decision.matched_skill_ids,
                )
            )
            for secondary in list(application["secondary"] or []):
                result.skill_specs.append(secondary["skill"])
                result.lifecycles.append(secondary["lifecycle"])
                result.change_logs.append(secondary["change_log"])
                result.version_history.append(secondary["version_history"])
                result.provenance_links.append(secondary["provenance_links"])
            consumed_new_ids.add(new_skill.skill_id)
            consumed_existing_ids.update(decision.matched_skill_ids)
            emit_stage_log(self.logger, f"[register_versions] merge skill={merged_skill.skill_id} from={decision.matched_skill_ids}")

        split_groups: Dict[str, List[ChangeDecision]] = {}
        for decision in decisions:
            if decision.action != "split" or not decision.matched_skill_ids:
                continue
            split_groups.setdefault(decision.matched_skill_ids[0], []).append(decision)

        for parent_id, bucket in split_groups.items():
            if parent_id in processed_split_parents:
                continue
            parent = existing_skills_by_id.get(parent_id)
            if parent is None:
                continue
            application = self.split_skill(
                parent_skill=parent,
                child_skills=[item.skill for item in bucket],
                target_state=target_state,
            )
            processed_split_parents.add(parent_id)
            consumed_existing_ids.add(parent_id)
            for item in bucket:
                consumed_new_ids.add(item.skill.skill_id)
                bound_supports = [
                    _copy_support(support, skill_id=item.skill.skill_id)
                    for support in list(incoming_support_by_id.values())
                    if support.support_id in set(item.skill.support_ids or [])
                ]
                result.support_records.extend(bound_supports)
            result.skill_specs.extend(list(application["children"] or []))
            result.skill_specs.append(application["deprecated_parent"]["skill"])
            result.lifecycles.extend(list(application["lifecycles"] or []))
            result.lifecycles.append(application["deprecated_parent"]["lifecycle"])
            result.change_logs.extend(list(application["change_logs"] or []))
            result.change_logs.append(application["deprecated_parent"]["change_log"])
            result.version_history.extend(list(application["version_history"] or []))
            result.version_history.append(application["deprecated_parent"]["version_history"])
            result.provenance_links.extend(list(application["provenance_links"] or []))
            result.provenance_links.append(application["deprecated_parent"]["provenance_links"])
            emit_stage_log(self.logger, f"[register_versions] split skill={parent_id} into={len(bucket)}")

        for decision in decisions:
            if decision.skill.skill_id in consumed_new_ids or decision.action == "discard":
                continue
            if decision.action not in {"create", "strengthen", "revise", "unchanged"}:
                continue

            new_skill = decision.skill
            incoming_supports = [
                support
                for support in list(incoming_support_by_id.values())
                if support.support_id in set(new_skill.support_ids or [])
            ]

            if decision.action == "create" or not decision.matched_skill_ids:
                updated_skill = _copy_skill(
                    new_skill,
                    version=self.create_new_version(current_version=new_skill.version, action="create"),
                    status=target_state,
                    metadata_update={"change_action": "create", "llm_reason": decision.reason},
                )
                bound_supports = [_copy_support(support, skill_id=updated_skill.skill_id) for support in incoming_supports]
                updated_skill = _copy_skill(updated_skill, support_ids=[support.support_id for support in bound_supports])
                provenance = {
                    "entity_type": "skill",
                    "entity_id": updated_skill.skill_id,
                    "doc_ids": _doc_ids_from_support_ids(updated_skill.support_ids, support_by_id),
                    "support_added": list(updated_skill.support_ids or []),
                    "support_conflicts": _conflicting_support_ids(updated_skill.support_ids, support_by_id),
                    "related_entity_ids": [],
                }
                result.skill_specs.append(updated_skill)
                result.support_records.extend(bound_supports)
                result.lifecycles.append(
                    self.update_lifecycle(
                        skill_id=updated_skill.skill_id,
                        current_state=None,
                        action="create",
                        target_state=target_state,
                        metadata={"doc_ids": provenance["doc_ids"], "llm_reason": decision.reason},
                    )
                )
                result.change_logs.append(
                    self._change_payload(
                        entity_type="skill",
                        entity_id=updated_skill.skill_id,
                        action="create",
                        from_version="",
                        to_version=updated_skill.version,
                        from_state="",
                        to_state=updated_skill.status.value,
                        summary=decision.reason,
                        provenance=provenance,
                    )
                )
                result.version_history.append(
                    self._history_payload(
                        entity_type="skill",
                        entity_id=updated_skill.skill_id,
                        version=updated_skill.version,
                        action="create",
                        status=updated_skill.status,
                    )
                )
                result.provenance_links.append(provenance)
                emit_stage_log(self.logger, f"[register_versions] create skill={updated_skill.skill_id}")
                continue

            existing_skill = existing_skills_by_id.get(decision.matched_skill_ids[0])
            if existing_skill is None:
                result.errors.append({"skill_id": new_skill.skill_id, "error": "matched skill missing from registry"})
                continue
            current_version = existing_skill.version
            next_version = self.create_new_version(current_version=current_version, action=decision.action)
            if decision.action == "unchanged":
                next_version = current_version
            bound_supports = [_copy_support(support, skill_id=existing_skill.skill_id) for support in incoming_supports]
            merged_support_ids = list(dict.fromkeys(list(existing_skill.support_ids or []) + [support.support_id for support in bound_supports]))
            updated_skill = _copy_skill(
                new_skill,
                skill_id=existing_skill.skill_id,
                version=next_version,
                status=(existing_skill.status if decision.action == "unchanged" else target_state),
                support_ids=merged_support_ids,
                metadata_update={
                    "change_action": decision.action,
                    "previous_skill_id": existing_skill.skill_id,
                    "llm_reason": decision.reason,
                },
            )
            provenance = {
                "entity_type": "skill",
                "entity_id": updated_skill.skill_id,
                "doc_ids": _doc_ids_from_support_ids(updated_skill.support_ids, support_by_id),
                "support_added": [support.support_id for support in bound_supports],
                "support_conflicts": _conflicting_support_ids(updated_skill.support_ids, support_by_id),
                "related_entity_ids": [existing_skill.skill_id],
            }
            result.skill_specs.append(updated_skill)
            result.support_records.extend(bound_supports)
            consumed_existing_ids.add(existing_skill.skill_id)
            if decision.action != "unchanged":
                result.lifecycles.append(
                    self.update_lifecycle(
                        skill_id=updated_skill.skill_id,
                        current_state=existing_skill.status,
                        action=decision.action,
                        target_state=target_state,
                        metadata={**provenance, "llm_reason": decision.reason},
                    )
                )
                result.change_logs.append(
                    self._change_payload(
                        entity_type="skill",
                        entity_id=updated_skill.skill_id,
                        action=decision.action,
                        from_version=existing_skill.version,
                        to_version=updated_skill.version,
                        from_state=existing_skill.status.value,
                        to_state=updated_skill.status.value,
                        summary=decision.reason,
                        provenance=provenance,
                        related_entity_ids=[existing_skill.skill_id],
                    )
                )
                result.version_history.append(
                    self._history_payload(
                        entity_type="skill",
                        entity_id=updated_skill.skill_id,
                        version=updated_skill.version,
                        action=decision.action,
                        status=updated_skill.status,
                        related_entity_ids=[existing_skill.skill_id],
                    )
                )
                result.provenance_links.append(provenance)
                emit_stage_log(self.logger, f"[register_versions] {decision.action} skill={updated_skill.skill_id}")

        incoming_related = [decision.skill for decision in decisions if decision.action != "discard"]
        if any(support.relation_type == SupportRelation.CONFLICT for support in support_records or []):
            for existing_skill in existing_skills:
                if existing_skill.skill_id in consumed_existing_ids:
                    continue
                if existing_skill.status in {VersionState.DEPRECATED, VersionState.RETIRED}:
                    continue
                review = self._conflict_review(
                    existing_skill=existing_skill,
                    incoming_skills=incoming_related,
                    support_by_id=support_by_id,
                )
                if review["action"] == "keep":
                    continue
                deprecated_state = (
                    VersionState.WATCHLIST if review["action"] == "watchlist" else VersionState.DEPRECATED
                )
                deprecated = self.mark_deprecated(
                    skill=existing_skill,
                    reason=review["reason"],
                    state=deprecated_state,
                    related_ids=[skill.skill_id for skill in incoming_related],
                )
                result.skill_specs.append(deprecated["skill"])
                result.lifecycles.append(deprecated["lifecycle"])
                result.change_logs.append(deprecated["change_log"])
                result.version_history.append(deprecated["version_history"])
                result.provenance_links.append(deprecated["provenance_links"])
                consumed_existing_ids.add(existing_skill.skill_id)
                emit_stage_log(self.logger, f"[register_versions] deprecate skill={existing_skill.skill_id}")

        deduped_skills: Dict[str, SkillSpec] = {}
        for skill in result.skill_specs:
            deduped_skills[f"{skill.skill_id}:{skill.status.value}"] = skill
        result.skill_specs = list(deduped_skills.values())

        deduped_supports: Dict[str, SupportRecord] = {}
        for support in result.support_records:
            deduped_supports[support.support_id] = support
        result.support_records = list(deduped_supports.values())
        return result


def register_versions(
    *,
    registry: DocumentRegistry,
    documents: Sequence[DocumentRecord],
    support_records: Sequence[SupportRecord],
    skill_specs: Sequence[SkillSpec],
    sdk: Optional[AutoSkill] = None,
    llm: Optional[LLM] = None,
    user_id: str = "u1",
    metadata: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
    target_state: VersionState = VersionState.ACTIVE,
    logger: StageLogger = None,
) -> VersionRegistrationResult:
    """
    Registers a compiled batch into the document registry and optionally the skill store.
    """

    effective_state = VersionState.DRAFT if dry_run else target_state
    llm_impl = llm or build_llm(dict(getattr(getattr(sdk, "config", None), "llm", {}) or {"provider": "mock"}))
    manager = VersionManager(registry=registry, llm=llm_impl, logger=logger)
    reconciled = manager.reconcile(
        skills=skill_specs,
        support_records=support_records,
        target_state=effective_state,
    )
    reconciled.documents = list(documents or [])
    reconciled.dry_run = bool(dry_run)

    if not dry_run:
        for document in documents or []:
            registry.upsert_document(document)
        for support in reconciled.support_records:
            registry.upsert_support(support)
        seen_skills: Set[str] = set()
        for skill in reconciled.skill_specs:
            key = f"{skill.skill_id}:{skill.status.value}"
            if key in seen_skills:
                continue
            registry.upsert_skill(skill)
            seen_skills.add(key)
        for lifecycle in reconciled.lifecycles:
            registry.append_lifecycle(lifecycle)
        for payload in reconciled.change_logs:
            registry.append_change_log(str(payload.get("change_id") or str(uuid.uuid4())), payload)
        for entry in reconciled.version_history:
            registry.append_version_history(
                entity_type=str(entry.get("entity_type") or ""),
                entity_id=str(entry.get("entity_id") or ""),
                entry=entry,
            )
        for payload in reconciled.provenance_links:
            registry.upsert_provenance_links(
                entity_type=str(payload.get("entity_type") or ""),
                entity_id=str(payload.get("entity_id") or ""),
                payload=payload,
            )

    if sdk is not None and reconciled.skill_specs:
        candidates = [
            skill_spec_to_candidate(spec)
            for spec in reconciled.skill_specs
            if spec.status in _ACTIVE_STORE_STATES
        ]
        md = dict(metadata or {})
        md.setdefault("channel", "offline_extract_from_doc")
        md.setdefault("source_type", "document")
        md["document_registry_root"] = registry.root_dir
        if candidates:
            if not dry_run:
                try:
                    with activate_offline_prompt_runtime(sdk=sdk, channel="offline_extract_from_doc"):
                        updated = sdk.maintainer.apply(
                            candidates,
                            user_id=str(user_id or "").strip() or "u1",
                            metadata=md,
                        )
                    reconciled.upserted_store_skills = [_plain_skill(skill) for skill in (updated or [])]
                    emit_stage_log(logger, f"[register_versions] store_upserts={len(reconciled.upserted_store_skills)}")
                except Exception as e:
                    reconciled.errors.append({"stage": "store_upsert", "error": str(e)})
                    emit_stage_log(logger, f"[register_versions] store upsert error: {e}")
            else:
                emit_stage_log(logger, f"[register_versions] dry-run store_upserts={len(candidates)}")

    return reconciled
