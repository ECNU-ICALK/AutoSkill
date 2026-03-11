"""
LLM-driven skill normalization and compilation stage for the offline document pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import uuid
from typing import Dict, List, Optional, Protocol

from autoskill.llm.base import LLM
from autoskill.llm.factory import build_llm
from autoskill.models import SkillExample
from autoskill.management.extraction import SkillCandidate

from .common import StageLogger, dedupe_strings, emit_stage_log, normalize_text
from .llm_utils import (
    clip_confidence,
    coerce_str_list,
    compact_text_list,
    llm_complete_json,
    maybe_json_dict,
    section_items_from_prompt,
)
from .models import SkillDraft, SkillSpec, SupportRecord, VersionState


def _identity_key_for_skill(
    *,
    asset_type: str,
    granularity: str,
    objective: str,
    domain: str,
    task_family: str,
    method_family: str,
    stage: str,
    name: str,
) -> str:
    """Builds a stable identity key for one compiled skill."""

    return "|".join(
        [
            normalize_text(asset_type, lower=True),
            normalize_text(granularity, lower=True),
            normalize_text(objective, lower=True),
            normalize_text(domain, lower=True),
            normalize_text(task_family, lower=True),
            normalize_text(method_family, lower=True),
            normalize_text(stage, lower=True),
            normalize_text(name, lower=True),
        ]
    )


def _fallback_prompt(item: Dict[str, object], draft_prompt: str) -> str:
    """Returns a canonical prompt/body for one compiled skill."""

    prompt = str(item.get("prompt") or item.get("skill_body") or "").strip()
    return prompt or str(draft_prompt or "").strip()


def _fallback_section_list(item: Dict[str, object], prompt: str, field_name: str, heading_hints: List[str]) -> List[str]:
    """Builds list-like fields with prompt fallback."""

    explicit = compact_text_list(coerce_str_list(item.get(field_name)), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(prompt, heading_hints)


def _coerce_examples(raw: object) -> List[SkillExample]:
    """Normalizes example objects into SkillExample payloads."""

    if raw is None:
        return []
    items = list(raw) if isinstance(raw, list) else [raw]
    out: List[SkillExample] = []
    for item in items[:3]:
        if isinstance(item, SkillExample):
            if str(item.input or "").strip():
                out.append(item)
            continue
        if not isinstance(item, dict):
            continue
        input_text = str(item.get("input") or item.get("client") or item.get("scenario") or "").strip()
        output_text = str(item.get("output") or item.get("therapist") or "").strip()
        notes_text = str(item.get("notes") or "").strip()
        if not input_text or not output_text:
            continue
        out.append(SkillExample(input=input_text, output=output_text, notes=notes_text or None))
    return out


def _render_list_section(title: str, items: List[str]) -> List[str]:
    """Renders one markdown list section when items are present."""

    values = dedupe_strings([str(item or "").strip() for item in items if str(item or "").strip()])
    if not values:
        return []
    lines = [f"## {title}", ""]
    lines.extend([f"- {value}" for value in values])
    lines.append("")
    return lines


def _render_examples_section(examples: List[SkillExample]) -> List[str]:
    """Renders short therapist-response examples into the instruction body."""

    if not examples:
        return []
    lines = ["## Example Therapist Responses", ""]
    for idx, example in enumerate(examples[:3], start=1):
        lines.append(f"### Example {idx}")
        lines.append("")
        lines.append(f"- Client/Input: {str(example.input or '').strip()}")
        lines.append(f"- Therapist/Output: {str(example.output or '').strip()}")
        if str(example.notes or "").strip():
            lines.append(f"- Notes: {str(example.notes or '').strip()}")
        lines.append("")
    return lines


def _build_structured_prompt(
    *,
    prompt: str,
    objective: str,
    applicable_signals: List[str],
    contraindications: List[str],
    intervention_moves: List[str],
    workflow_steps: List[str],
    constraints: List[str],
    cautions: List[str],
    output_contract: List[str],
    examples: List[SkillExample],
) -> str:
    """Builds one execution-ready prompt body from structured skill fields."""

    lines: List[str] = [str(prompt or "").strip()]
    if objective.strip():
        lines.extend(["", "## Objective", "", objective.strip()])
    lines.extend(_render_list_section("Applicable Signals", applicable_signals))
    lines.extend(_render_list_section("Contraindications", contraindications))
    lines.extend(_render_list_section("Intervention Moves", intervention_moves))
    lines.extend(_render_list_section("Workflow Steps", workflow_steps))
    lines.extend(_render_list_section("Constraints", constraints))
    lines.extend(_render_list_section("Cautions", cautions))
    lines.extend(_render_list_section("Output Contract", output_contract))
    lines.extend(_render_examples_section(examples))
    body = "\n".join(lines).strip()
    return body or str(prompt or "").strip()


@dataclass
class SkillCompilationResult:
    """Output of the skill compilation stage."""

    skill_drafts: List[SkillDraft] = field(default_factory=list)
    support_records: List[SupportRecord] = field(default_factory=list)
    skill_specs: List[SkillSpec] = field(default_factory=list)
    candidates: List[SkillCandidate] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    compiler_name: str = "llm"


class SkillCompiler(Protocol):
    """Pluggable draft-to-skill compiler interface."""

    def compile(
        self,
        *,
        skill_drafts: List[SkillDraft],
        support_records: List[SupportRecord],
        target_state: VersionState,
        logger: StageLogger,
    ) -> SkillCompilationResult:
        """Compiles drafts into canonical skills and helper store candidates."""


class LLMSkillCompiler:
    """Model-driven draft-to-skill compiler."""

    def __init__(
        self,
        *,
        llm: Optional[LLM] = None,
        llm_config: Optional[Dict[str, object]] = None,
    ) -> None:
        self._llm = llm or build_llm(dict(llm_config or {"provider": "mock"}))

    def _compile_group(
        self,
        *,
        drafts: List[SkillDraft],
        supports: List[SupportRecord],
        target_state: VersionState,
    ) -> List[SkillSpec]:
        support_by_id = {support.support_id: support for support in supports}
        payload = {
            "drafts": [
                {
                    "draft_id": draft.draft_id,
                    "doc_id": draft.doc_id,
                    "name": draft.name,
                    "description": draft.description,
                    "asset_type": draft.asset_type,
                    "granularity": draft.granularity,
                    "objective": draft.objective,
                    "domain": draft.domain,
                    "task_family": draft.task_family,
                    "method_family": draft.method_family,
                    "stage": draft.stage,
                    "applicable_signals": list(draft.applicable_signals or []),
                    "contraindications": list(draft.contraindications or []),
                    "intervention_moves": list(draft.intervention_moves or []),
                    "workflow_steps": list(draft.workflow_steps or []),
                    "triggers": list(draft.triggers or []),
                    "constraints": list(draft.constraints or []),
                    "cautions": list(draft.cautions or []),
                    "output_contract": list(draft.output_contract or []),
                    "examples": [
                        {
                            "input": str(example.input or ""),
                            "output": str(example.output or ""),
                            "notes": str(example.notes or ""),
                        }
                        for example in list(draft.examples or [])
                    ],
                    "risk_class": draft.risk_class,
                    "confidence": draft.confidence,
                    "support_ids": list(draft.support_ids or []),
                    "metadata": dict(draft.metadata or {}),
                }
                for draft in drafts
            ],
            "supports": [
                {
                    "support_id": support.support_id,
                    "doc_id": support.doc_id,
                    "section": support.section,
                    "excerpt": support.excerpt,
                    "relation_type": support.relation_type.value,
                    "confidence": support.confidence,
                }
                for support in supports
            ],
            "target_state": target_state.value,
        }
        system = (
            "You are AutoSkill's Document Skill Compiler.\n"
            "Task: consolidate support-backed document counseling assets into canonical reusable skills.\n"
            "Output ONLY strict JSON parseable by json.loads.\n"
            "Merge drafts only when they express the same reusable capability after de-duplication and abstraction.\n"
            "Never merge drafts across different asset_type or granularity.\n"
            "Keep distinct skills separate when objective, method, stage, or deliverable differs materially.\n"
            "Preserve multi-granularity outputs: macro_protocol, session_skill, micro_skill, safety_rule, knowledge_reference.\n"
            "Each output skill should stay single-goal, with one primary objective, one primary stage, and one primary method family.\n"
            "Every output skill must reference support_ids grounded in the provided drafts/supports.\n"
            "Return JSON as {\"skills\": [...]}.\n"
            "Fields per skill:\n"
            "- name, description, prompt\n"
            "- asset_type, granularity, objective\n"
            "- domain, task_family, method_family, stage\n"
            "- applicable_signals, intervention_moves, contraindications\n"
            "- triggers, workflow_steps, constraints, cautions, output_contract, examples, tags\n"
            "- confidence, risk_class\n"
            "- support_ids: array of support ids backing this canonical skill\n"
            "- source_draft_ids: array of source draft ids merged into this skill\n"
            "- optional resources/files with safe relative paths only\n"
            "Do not add facts unsupported by the provided drafts/supports.\n"
        )
        repair_system = (
            "You are a JSON output fixer for document skill compilation.\n"
            "Given DATA and DRAFT, output ONLY strict JSON: {\"skills\": [...]}.\n"
            "Keep fields: name, description, prompt, asset_type, granularity, objective, domain, task_family, method_family, stage, applicable_signals, intervention_moves, contraindications, triggers, workflow_steps, constraints, cautions, output_contract, examples, tags, confidence, risk_class, support_ids, source_draft_ids, optional resources/files.\n"
            "Do not add unsupported content.\n"
        )
        repaired_payload = (
            f"DATA:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            "DRAFT:\n__DRAFT__"
        )
        parsed = llm_complete_json(
            llm=self._llm,
            system=system,
            payload=payload,
            repair_system=repair_system,
            repair_payload=repaired_payload,
        )
        obj = maybe_json_dict(parsed)
        raw_skills = obj.get("skills") if isinstance(obj.get("skills"), list) else parsed
        if not isinstance(raw_skills, list):
            return []

        out: List[SkillSpec] = []
        for raw_item in raw_skills:
            item = maybe_json_dict(raw_item)
            name = str(item.get("name") or "").strip()
            description = str(item.get("description") or "").strip()
            prompt = _fallback_prompt(item, "")
            if not name or not description or not prompt:
                continue
            asset_type = str(item.get("asset_type") or "").strip() or "session_skill"
            granularity = str(item.get("granularity") or "").strip() or "session"
            objective = str(item.get("objective") or description).strip()
            intervention_moves = _fallback_section_list(
                item,
                prompt,
                "intervention_moves",
                ["intervention moves", "micro skills", "techniques", "干预动作", "微技能"],
            )
            workflow_steps = _fallback_section_list(
                item,
                prompt,
                "workflow_steps",
                ["workflow", "core workflow", "步骤", "流程"],
            )
            constraints = _fallback_section_list(
                item,
                prompt,
                "constraints",
                ["constraints", "rules", "规则", "约束"],
            )
            cautions = _fallback_section_list(
                item,
                prompt,
                "cautions",
                ["cautions", "anti-patterns", "风险", "注意"],
            )
            if not workflow_steps and not intervention_moves and not constraints and not cautions:
                continue
            source_draft_ids = compact_text_list(coerce_str_list(item.get("source_draft_ids")), limit=32)
            support_ids = compact_text_list(coerce_str_list(item.get("support_ids")), limit=64)
            if not support_ids and source_draft_ids:
                for draft in drafts:
                    if draft.draft_id in source_draft_ids:
                        support_ids.extend(list(draft.support_ids or []))
                support_ids = compact_text_list(support_ids, limit=64)
            if not support_ids:
                for draft in drafts:
                    support_ids.extend(list(draft.support_ids or []))
                support_ids = compact_text_list(support_ids, limit=64)
            if not support_ids:
                continue
            tags = compact_text_list(coerce_str_list(item.get("tags")), limit=6)
            examples = _coerce_examples(item.get("examples"))
            if not examples and source_draft_ids:
                for draft in drafts:
                    if draft.draft_id in source_draft_ids:
                        examples.extend(list(draft.examples or []))
                examples = examples[:3]
            output_contract = _fallback_section_list(
                item,
                prompt,
                "output_contract",
                ["output", "output format", "输出", "交付"],
            )
            structured_prompt = _build_structured_prompt(
                prompt=prompt,
                objective=objective,
                applicable_signals=compact_text_list(coerce_str_list(item.get("applicable_signals")), limit=12),
                contraindications=compact_text_list(coerce_str_list(item.get("contraindications")), limit=12),
                intervention_moves=intervention_moves,
                workflow_steps=workflow_steps,
                constraints=constraints,
                cautions=cautions,
                output_contract=output_contract,
                examples=examples,
            )
            spec = SkillSpec(
                skill_id=str(uuid.uuid4()),
                name=name,
                description=description,
                skill_body=structured_prompt,
                asset_type=asset_type,
                granularity=granularity,
                objective=objective,
                domain=str(item.get("domain") or "").strip(),
                task_family=str(item.get("task_family") or "").strip(),
                method_family=str(item.get("method_family") or "").strip(),
                stage=str(item.get("stage") or "").strip(),
                applicable_signals=compact_text_list(coerce_str_list(item.get("applicable_signals")), limit=12),
                contraindications=compact_text_list(coerce_str_list(item.get("contraindications")), limit=12),
                intervention_moves=intervention_moves,
                triggers=compact_text_list(coerce_str_list(item.get("triggers")), limit=5),
                workflow_steps=workflow_steps,
                constraints=constraints,
                cautions=cautions,
                output_contract=output_contract,
                examples=examples,
                tags=tags,
                support_ids=support_ids,
                metadata={
                    "risk_class": str(item.get("risk_class") or "").strip() or "low",
                    "source_draft_ids": source_draft_ids,
                    "support_summary": {
                        "support": len(
                            [sid for sid in support_ids if support_by_id.get(sid) and support_by_id[sid].relation_type.value == "support"]
                        ),
                        "constraint": len(
                            [sid for sid in support_ids if support_by_id.get(sid) and support_by_id[sid].relation_type.value == "constraint"]
                        ),
                        "conflict": len(
                            [sid for sid in support_ids if support_by_id.get(sid) and support_by_id[sid].relation_type.value == "conflict"]
                        ),
                        "case_variant": len(
                            [sid for sid in support_ids if support_by_id.get(sid) and support_by_id[sid].relation_type.value == "case_variant"]
                        ),
                    },
                    "files": maybe_json_dict(item.get("files")),
                    "resources": maybe_json_dict(item.get("resources")),
                    "confidence": clip_confidence(item.get("confidence"), default=0.75),
                },
                version="0.1.0",
                status=target_state,
            )
            identity_key = _identity_key_for_skill(
                asset_type=spec.asset_type,
                granularity=spec.granularity,
                objective=spec.objective,
                domain=spec.domain,
                task_family=spec.task_family,
                method_family=spec.method_family,
                stage=spec.stage,
                name=spec.name,
            )
            spec.skill_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill-skill:{identity_key}"))
            spec.metadata["identity_key"] = identity_key
            out.append(spec)
        return out

    def compile(
        self,
        *,
        skill_drafts: List[SkillDraft],
        support_records: List[SupportRecord],
        target_state: VersionState,
        logger: StageLogger,
    ) -> SkillCompilationResult:
        result = SkillCompilationResult(
            skill_drafts=list(skill_drafts or []),
            support_records=list(support_records or []),
            compiler_name="llm",
        )
        grouped: Dict[str, List[SkillDraft]] = {}
        for draft in skill_drafts or []:
            grouped.setdefault(str(draft.doc_id or "").strip() or "document", []).append(draft)

        supports_by_doc: Dict[str, List[SupportRecord]] = {}
        for support in support_records or []:
            supports_by_doc.setdefault(str(support.doc_id or "").strip() or "document", []).append(support)

        for doc_id, drafts in grouped.items():
            try:
                compiled_specs = self._compile_group(
                    drafts=drafts,
                    supports=supports_by_doc.get(doc_id, []),
                    target_state=target_state,
                )
                result.skill_specs.extend(compiled_specs)
                for spec in compiled_specs:
                    result.candidates.append(skill_spec_to_candidate(spec))
                    emit_stage_log(logger, f"[compile_skills] doc={doc_id} skill={spec.skill_id}")
            except Exception as e:
                result.errors.append({"doc_id": doc_id, "error": str(e)})
                emit_stage_log(logger, f"[compile_skills] error doc={doc_id}: {e}")
        return result


HeuristicSkillCompiler = LLMSkillCompiler


def skill_spec_to_candidate(spec: SkillSpec) -> SkillCandidate:
    """Converts one SkillSpec into the store-facing SkillCandidate format."""

    files = maybe_json_dict((spec.metadata or {}).get("files"))
    return SkillCandidate(
        name=str(spec.name or "").strip(),
        description=str(spec.description or "").strip(),
        instructions=str(spec.skill_body or "").strip(),
        triggers=[str(x).strip() for x in list(spec.triggers or []) if str(x).strip()],
        tags=[str(x).strip() for x in list(spec.tags or []) if str(x).strip()],
        examples=list(spec.examples or []),
        files={str(path): str(content) for path, content in files.items()},
        confidence=clip_confidence((spec.metadata or {}).get("confidence"), default=0.8),
        source={
            "source_type": "document_skill",
            "skill_spec_id": spec.skill_id,
            "asset_type": spec.asset_type,
            "granularity": spec.granularity,
            "objective": spec.objective,
            "support_ids": list(spec.support_ids or []),
            "domain": spec.domain,
            "task_family": spec.task_family,
            "method_family": spec.method_family,
            "stage": spec.stage,
            "applicable_signals": list(spec.applicable_signals or []),
            "contraindications": list(spec.contraindications or []),
            "intervention_moves": list(spec.intervention_moves or []),
            "workflow_steps": list(spec.workflow_steps or []),
            "constraints": list(spec.constraints or []),
            "cautions": list(spec.cautions or []),
            "output_contract": list(spec.output_contract or []),
            "examples": [
                {
                    "input": str(example.input or ""),
                    "output": str(example.output or ""),
                    "notes": str(example.notes or ""),
                }
                for example in list(spec.examples or [])
            ],
            "version": spec.version,
            "status": spec.status.value,
            "resources": maybe_json_dict((spec.metadata or {}).get("resources")),
        },
    )


def build_skill_compiler(
    kind: str = "llm",
    *,
    llm: Optional[LLM] = None,
    llm_config: Optional[Dict[str, object]] = None,
) -> SkillCompiler:
    """Builds a concrete draft-to-skill compiler implementation."""

    name = str(kind or "").strip().lower() or "llm"
    if name in {"llm", "heuristic", "stub", "rule-based", "rule_based"}:
        return LLMSkillCompiler(llm=llm, llm_config=llm_config)
    raise ValueError(f"unsupported skill compiler: {kind}")


def compile_skills(
    *,
    skill_drafts: List[SkillDraft],
    support_records: List[SupportRecord],
    compiler: SkillCompiler | None = None,
    target_state: VersionState = VersionState.DRAFT,
    logger: StageLogger = None,
) -> SkillCompilationResult:
    """Public functional wrapper for the skill compilation stage."""

    impl = compiler or LLMSkillCompiler()
    return impl.compile(
        skill_drafts=list(skill_drafts or []),
        support_records=list(support_records or []),
        target_state=target_state,
        logger=logger,
    )
