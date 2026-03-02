"""
OpenClaw plugin specific prompt profile for agentic trajectory evolution.

This module intentionally does NOT change core AutoSkill logic in `autoskill/*`.
It only provides OpenClaw-runtime overrides:
1) extractor prompts tuned for agentic trajectories
2) maintenance prompts tuned for agentic add/merge/discard + merge synthesis
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from autoskill.config import AutoSkillConfig
from autoskill.management import maintenance as _m
from autoskill.management.extraction import (
    HeuristicSkillExtractor,
    LLMSkillExtractor,
    SkillCandidate,
    _candidate_from_freeform_llm_text,
    _candidate_from_obj,
    _source_obj,
)
from autoskill.models import Skill, SkillExample
from autoskill.utils import json_from_llm_text, redact_obj


class OpenClawTrajectorySkillExtractor(LLMSkillExtractor):
    """
    OpenClaw-agentic extractor:
    keep extraction/repair/parsing flow identical to upstream extractor, but with
    prompts focused on tool-use trajectory and agent workflow skills.
    """

    def __init__(self, config: AutoSkillConfig) -> None:
        """Run init."""
        super().__init__(config)
        self._config = config

    def extract(
        self,
        *,
        user_id: str,
        messages: Optional[List[Dict[str, Any]]],
        events: Optional[List[Dict[str, Any]]],
        max_candidates: int,
        hint: Optional[str] = None,
        retrieved_reference: Optional[Dict[str, Any]] = None,
    ) -> List[SkillCandidate]:
        """Run extract."""
        payload = {
            "user_id": user_id,
            "messages": messages or [],
            "events": events or [],
            "max_candidates": max_candidates,
            "hint": (str(hint).strip() if hint and str(hint).strip() else None),
            "retrieved_reference": (
                dict(retrieved_reference) if isinstance(retrieved_reference, dict) else None
            ),
        }
        if self._config.redact_sources_before_llm:
            payload = redact_obj(payload)

        system = _build_openclaw_agentic_extract_prompt(max_candidates=max_candidates)
        user = json.dumps(payload, ensure_ascii=False)

        try:
            text = self._llm.complete(system=system, user=user)
        except Exception as e:
            if (self._config.extra or {}).get("raise_on_llm_extract_error"):
                raise RuntimeError(f"LLM extract call failed: {e}") from e
            return HeuristicSkillExtractor(self._config).extract(
                user_id=user_id,
                messages=messages,
                events=events,
                max_candidates=max_candidates,
                hint=hint,
            )

        if not (text or "").strip():
            if (self._config.extra or {}).get("raise_on_llm_extract_error"):
                raise RuntimeError("LLM returned empty response for skill extraction")
            return HeuristicSkillExtractor(self._config).extract(
                user_id=user_id,
                messages=messages,
                events=events,
                max_candidates=max_candidates,
                hint=hint,
            )

        try:
            parsed = json_from_llm_text(text)
        except Exception as e:
            recovered = _candidate_from_freeform_llm_text(
                text,
                source=_source_obj(self._config, messages=messages, events=events),
            )
            if recovered:
                return [recovered][:max_candidates]

            try:
                repaired = self._repair_to_json(
                    payload=payload,
                    draft=text,
                    max_candidates=max_candidates,
                )
            except Exception as e_repair:
                if (self._config.extra or {}).get("raise_on_llm_extract_error"):
                    raise RuntimeError(f"LLM repair call failed: {e_repair}") from e_repair
                repaired = ""

            if not (repaired or "").strip():
                if (self._config.extra or {}).get("raise_on_llm_extract_error"):
                    snippet = (text or "").strip().replace("\n", "\\n")[:1200]
                    raise RuntimeError(
                        f"Failed to parse LLM JSON for skill extraction. Output snippet: {snippet}"
                    ) from e
                return HeuristicSkillExtractor(self._config).extract(
                    user_id=user_id,
                    messages=messages,
                    events=events,
                    max_candidates=max_candidates,
                    hint=hint,
                )

            try:
                parsed = json_from_llm_text(repaired)
            except Exception as e2:
                recovered2 = _candidate_from_freeform_llm_text(
                    repaired,
                    source=_source_obj(self._config, messages=messages, events=events),
                )
                if recovered2:
                    return [recovered2][:max_candidates]
                if (self._config.extra or {}).get("raise_on_llm_extract_error"):
                    snippet1 = (text or "").strip().replace("\n", "\\n")[:900]
                    snippet2 = (repaired or "").strip().replace("\n", "\\n")[:900]
                    raise RuntimeError(
                        "Failed to parse LLM JSON for skill extraction after repair. "
                        f"Original snippet: {snippet1} | Repaired snippet: {snippet2}"
                    ) from e2
                return HeuristicSkillExtractor(self._config).extract(
                    user_id=user_id,
                    messages=messages,
                    events=events,
                    max_candidates=max_candidates,
                    hint=hint,
                )

        skills_obj = parsed.get("skills") if isinstance(parsed, dict) else parsed
        if not isinstance(skills_obj, list):
            return []

        out: List[SkillCandidate] = []
        for item in skills_obj[:max_candidates]:
            cand = _candidate_from_obj(
                item,
                source=_source_obj(self._config, messages=messages, events=events),
            )
            if cand:
                out.append(cand)
        return out

    def _repair_to_json(self, *, payload: Dict[str, Any], draft: str, max_candidates: int) -> str:
        """Run repair to json."""
        system = _build_openclaw_agentic_repair_prompt(max_candidates=max_candidates)
        user = (
            f"DATA:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            f"DRAFT:\n{(draft or '').strip()[-2500:]}"
        )
        return self._llm.complete(system=system, user=user, temperature=0.0)


def _build_openclaw_agentic_extract_prompt(*, max_candidates: int) -> str:
    """Run build openclaw agentic extract prompt."""
    return (
        "You are AutoSkill's OpenClaw Trajectory Skill Extractor.\n"
        "Task: derive reusable AGENTIC skills from interaction trajectories (messages/events/tool-use traces).\n"
        "If DATA.hint exists, treat it as explicit extraction intent.\n"
        "Output ONLY strict JSON parseable by json.loads.\n"
        "\n"
        "### Skill-creator principles\n"
        "- Skills are onboarding artifacts for another agent instance: prioritize reusable procedural knowledge over one-run content.\n"
        "- Concise is key: keep only high-signal constraints/workflow; avoid long explanatory dumps.\n"
        "- Progressive disclosure: keep metadata triggerable and prompt body executable; do not embed large reference payloads.\n"
        "- Degrees of freedom: keep strict rules where operations are fragile, and preserve flexibility where multiple approaches are valid.\n"
        "- If deterministic repeated logic is present, mention reusable resources briefly (for example: scripts/... or references/...), not full inline docs.\n"
        "\n"
        "### Evidence and trust\n"
        "- USER turns and explicit user feedback are primary authority.\n"
        "- Successful trajectory patterns (tool sequence + checks + recovery) are valid evidence.\n"
        "- ASSISTANT text is supporting context only; do not adopt assistant-invented details unless user confirmed.\n"
        "- Keep only evidence-backed constraints/workflow steps.\n"
        "\n"
        "### Trajectory focus\n"
        "- Prioritize recent turns; use older context mainly to detect continuity vs topic switch.\n"
        "- Detect boundary turn where objective/deliverable/channel/tooling intent changes.\n"
        "- If boundary exists, post-boundary intent is active; do not mix pre-boundary constraints unless restated.\n"
        "- If no boundary, keep stable cross-turn constraints.\n"
        "- DATA.retrieved_reference is identity hint for update-vs-new only, not extraction evidence.\n"
        "\n"
        "### What counts as an extractable agentic skill\n"
        "- Extract when there is reusable agent policy/workflow, including one explicit reusable user rule.\n"
        "- Examples: tool ordering, verification checkpoints, retry/fallback rules, environment constraints, output contract, stop/rollback conditions.\n"
        "- Do NOT extract one-off instance payload, temporary content facts, or stale constraints outside active topic.\n"
        "- Prefer extracting HOW to execute repeatedly, not WHAT this specific task happened to be about.\n"
        "\n"
        "### Generalization and de-identification\n"
        "- Keep HOW-to-execute capability; remove this-run specifics.\n"
        "- Replace specific entities with placeholders when needed (<INPUT>, <TARGET>, <ENV>, <FILE>, <TOOL>).\n"
        "- Remove project/org/person/address/account/url/date/budget/ticket specifics.\n"
        "- If value cannot survive de-identification, return {\"skills\": []}.\n"
        "\n"
        "### Output schema\n"
        f"- Return {{\"skills\": [...]}} with at most {max_candidates} item(s).\n"
        "- If no strong reusable signal, return {\"skills\": []}.\n"
        "- Keep all fields in the dominant user language.\n"
        "- Fields per skill:\n"
        "  - name: concise, searchable, MUST encode primary user intent + action + domain/platform when evidenced.\n"
        "  - description: 1-2 sentences, third person, what/when; include trigger cues for when to use.\n"
        "  - prompt: executable Markdown with # Goal, # Constraints & Style, optional # Workflow (only if explicit multi-step operations); use imperative style.\n"
        "  - triggers: 3-5 short intent phrases.\n"
        "  - tags: 1-6 canonical keywords.\n"
        "  - examples: 0-3 short de-identified examples.\n"
        "  - confidence: 0.0-1.0.\n"
        "\n"
        "JSON validity: escape newlines as \\n. No Markdown code block."
    )


def _build_openclaw_agentic_repair_prompt(*, max_candidates: int) -> str:
    """Run build openclaw agentic repair prompt."""
    return (
        "You are a JSON output fixer for OpenClaw trajectory skill extraction.\n"
        "Given DATA and DRAFT, output ONLY strict JSON: {\"skills\": [...]}.\n"
        f"Return at most {max_candidates} skills; if uncertain return {{\"skills\": []}}.\n"
        "No Markdown, no commentary.\n"
        "\n"
        "Apply these constraints:\n"
        "- Preserve skill-creator principles: concise, high-signal, progressive disclosure, executable instructions.\n"
        "- Keep only reusable agentic policy/workflow evidenced by user feedback or successful trajectory patterns.\n"
        "- Prioritize recent turns; if boundary/topic switch exists, keep post-boundary intent only.\n"
        "- DATA.retrieved_reference is identity hint only (update-vs-new), not extraction evidence.\n"
        "- Remove one-off payload/entities; keep portable capability constraints.\n"
        "- Keep fields language consistent with dominant user language.\n"
        "- Keep schema fields: name, description, prompt, triggers, tags, examples, confidence.\n"
        "- name must encode primary user intent + action + domain/platform when evidenced.\n"
        "- description should state when to use; prompt must remain executable and structured (# Goal, # Constraints & Style, optional # Workflow) with imperative style.\n"
        "- If resources are referenced, keep them as short pointers (scripts/... or references/...), never long pasted docs.\n"
        "\n"
        "JSON validity: escape newlines as \\n."
    )


def _decide_candidate_action_with_llm_agentic(
    llm,
    cand: SkillCandidate,
    similar_hits: List,
    *,
    user_id: str,
    dedupe_threshold: float,
) -> Tuple[str, Optional[str], Optional[str]]:
    """Run decide candidate action with llm agentic."""
    system = (
        "You are AutoSkill's OpenClaw Agentic Skill Set Manager.\n"
        "Task: decide add|merge|discard for a newly extracted trajectory skill.\n"
        "Output ONLY strict JSON.\n"
        "\n"
        "Skill quality target:\n"
        "- Keep a compact, high-signal skill set with strong triggerability and low redundancy.\n"
        "- Prefer reusable procedures/policies over broad generic advice.\n"
        "\n"
        "Actions:\n"
        "- add: create new user skill\n"
        "- merge: merge into ONE existing USER skill\n"
        "- discard: do not store\n"
        "\n"
        "Decision policy:\n"
        "- Maintain high-signal, low-fragmentation, reusable skills.\n"
        "- Discard if candidate is generic/one-off/low evidence after de-identification.\n"
        "- Evaluate identity using objective + deliverable/channel + operation class + acceptance checks + tool/retry/fallback policy.\n"
        "- Merge when same ongoing work item/capability and candidate is an incremental trajectory improvement.\n"
        "- Add when recent intent indicates a topic/workflow switch (new objective/deliverable/channel) even within same broad domain.\n"
        "- Prefer merge over add when differences are mostly wording/examples but the reusable procedure and completion criteria are the same.\n"
        "- Prefer add when trigger context/usage boundary is materially different, even if domain words overlap.\n"
        "- Similarity scores are hints, not final authority.\n"
        "- If merge-vs-add is unclear, prefer discard over risky merge.\n"
        "\n"
        "Constraints:\n"
        "- If merge, target_skill_id must be a user-scope skill in provided similar list.\n"
        "- Do not delete existing skills.\n"
        "\n"
        "Return schema:\n"
        "{\n"
        "  \"action\": \"add\"|\"merge\"|\"discard\",\n"
        "  \"target_skill_id\": string|null,\n"
        "  \"reason\": string\n"
        "}"
    )
    data = {
        "user_id": str(user_id),
        "dedupe_threshold": float(dedupe_threshold),
        "candidate": _m._candidate_to_raw(cand),
        "similar": [_m._hit_for_llm(h) for h in (similar_hits or [])][:8],
    }
    user = json.dumps(data, ensure_ascii=False)
    text = llm.complete(system=system, user=user, temperature=0.0)
    obj = _m._json_from_llm_decision(text)
    action = _m._normalize_action(obj.get("action"))
    target = str(obj.get("target_skill_id") or obj.get("target") or "").strip() or None
    reason = str(obj.get("reason") or obj.get("rationale") or "").strip() or None
    if action not in {"add", "merge", "discard"}:
        action = ""
    return action, target, reason


def _merge_with_llm_agentic(llm, existing: Skill, cand: SkillCandidate) -> Skill:
    """Run merge with llm agentic."""
    try:
        system = (
            "You are AutoSkill's OpenClaw Agentic Skill Merger.\n"
            "Task: merge existing_skill and candidate_skill into ONE improved reusable skill.\n"
            "Output ONLY strict JSON with fields: name, description, prompt, triggers, tags, examples.\n"
            "\n"
            "Skill-creator alignment:\n"
            "- Keep output concise and high-signal.\n"
            "- Preserve progressive disclosure (lean prompt body, no large inline references).\n"
            "- Preserve proper degrees of freedom: strict where fragile, flexible where context-dependent.\n"
            "\n"
            "Rules:\n"
            "- Preserve capability identity; do not change the core job-to-be-done.\n"
            "- Perform semantic union, NOT concatenation.\n"
            "- Keep unique reusable constraints from both; drop one-off payload.\n"
            "- Keep trajectory-critical policies: tool order, checkpoints, fallback/retry/rollback, stop conditions.\n"
            "- Do not invent new standards or details not present in inputs.\n"
            "- De-duplicate aggressively across all fields.\n"
            "- In triggers/tags/examples remove exact and near-duplicate variants.\n"
            "- Keep output compact, high-signal, and portable.\n"
            "\n"
            "Field requirements:\n"
            "- name: concise, searchable; keep stable unless clear improvement.\n"
            "- description: 1-2 sentences, third person; clearly state what/when.\n"
            "- prompt: Markdown with # Goal, # Constraints & Style, optional # Workflow (explicit multi-step only); imperative style.\n"
            "- triggers: 3-5 short distinct intent phrases.\n"
            "- tags: 1-6 canonical tags.\n"
            "- examples: 0-3 de-identified examples.\n"
            "- If resource references are needed, keep short pointers only (scripts/... or references/...).\n"
            "\n"
            "JSON validity: escape newlines as \\n."
        )
        user = (
            "existing_skill:\n"
            f"{_m._skill_for_llm(existing)}\n\n"
            "candidate_skill:\n"
            f"{_m._candidate_to_raw(cand)}\n"
        )
        text = llm.complete(system=system, user=user, temperature=0.0)
        obj = json_from_llm_text(text)
        if not isinstance(obj, dict):
            return _m._merge(existing, cand)

        merged = _m._merge(existing, cand)
        merged.name = str(obj.get("name") or merged.name).strip() or merged.name
        merged.description = (
            str(obj.get("description") or merged.description).strip() or merged.description
        )
        merged.instructions = str(
            obj.get("prompt") or obj.get("instructions") or merged.instructions
        ).strip() or merged.instructions
        merged.triggers = _m._dedupe(
            [str(t).strip() for t in (obj.get("triggers") or []) if str(t).strip()]
        ) or merged.triggers
        merged.tags = _m._dedupe(
            [str(t).strip() for t in (obj.get("tags") or []) if str(t).strip()]
        ) or merged.tags
        merged.examples = _m._merge_examples(
            merged.examples,
            _examples_from_obj(obj.get("examples")),
        )
        return merged
    except Exception:
        return _m._merge(existing, cand)


def _examples_from_obj(obj: Any) -> List[SkillExample]:
    """Run examples from obj."""
    if not isinstance(obj, list):
        return []
    out: List[SkillExample] = []
    for e in obj[:8]:
        if not isinstance(e, dict):
            continue
        inp = str(e.get("input") or "").strip()
        if not inp:
            continue
        out.append(
            SkillExample(
                input=inp,
                output=(str(e.get("output")).strip() if e.get("output") else None),
                notes=(str(e.get("notes")).strip() if e.get("notes") else None),
            )
        )
    return out


def install_openclaw_agentic_prompt_profile() -> None:
    """
    Installs OpenClaw-only maintenance prompt overrides in current process.

    This mutates module-level call sites in autoskill.management.maintenance, but only
    inside the OpenClaw plugin runtime process.
    """

    _m._decide_candidate_action_with_llm = _decide_candidate_action_with_llm_agentic
    _m._merge_with_llm = _merge_with_llm_agentic
