"""
Skill extraction.

This layer converts raw inputs (messages/events) into SkillCandidate objects:
- `HeuristicSkillExtractor`: offline heuristic extraction (builds a generic SOP when no LLM is available)
- `LLMSkillExtractor`: calls an LLM to produce structured JSON, with parsing/repair/fallback

LLM extraction fallbacks (strong -> weak):
1) parse JSON directly
2) recover key fields from non-JSON semi-structured text (common in “reasoning” outputs)
3) ask the model to repair the draft into strict JSON
4) fall back to heuristic extraction (so ingest won't fail due to unstable LLM outputs)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from ..config import AutoSkillConfig
from ..llm.base import LLM
from ..llm.factory import build_llm
from ..models import SkillExample
from ..utils.json import json_from_llm_text
from ..utils.redact import redact_obj
from ..utils.text import keywords

_ACK_LINES = {
    "thanks",
    "thank you",
    "thx",
    "ty",
    "ok",
    "okay",
    "got it",
    "understood",
    "acknowledged",
    "noted",
}

def _normalize_ack_line(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"^[^\w]+", "", s).strip()
    s = re.sub(r"[^\w]+$", "", s).strip()
    return s


_ACK_KEYS = {_normalize_ack_line(s) for s in _ACK_LINES}

def _sanitize_step_for_prompt(step: str, idx: int) -> str:
    s = str(step or "").strip()
    if not s:
        return f"<STEP_{idx}>"
    return s


@dataclass
class SkillCandidate:
    name: str
    description: str
    instructions: str
    triggers: List[str]
    tags: List[str]
    examples: List[SkillExample]
    confidence: float = 0.6
    source: Optional[Dict[str, Any]] = None


class SkillExtractor(Protocol):
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
        ...


def build_default_extractor(config: AutoSkillConfig) -> SkillExtractor:
    # Default: provider=mock uses heuristic extraction (offline); other providers use LLM-based extraction.
    provider = (config.llm.get("provider") or "mock").lower()
    if provider == "mock":
        return HeuristicSkillExtractor(config)
    return LLMSkillExtractor(config)


class HeuristicSkillExtractor:
    def __init__(self, config: AutoSkillConfig) -> None:
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
        text = _flatten_sources(messages=messages, events=events)
        if hint and str(hint).strip():
            text = f"{text}\n\nHint:\n{str(hint).strip()}\n"
        if not text.strip():
            return []

        kws = keywords(text, limit=3)
        name = _heuristic_name(text, kws)
        description = (
            f"General SOP for common requests related to {', '.join(kws)}."
            if kws
            else "General SOP for common requests."
        )
        instructions = _heuristic_instructions(text)

        candidate = SkillCandidate(
            name=name,
            description=description,
            instructions=instructions,
            triggers=[
                "Use when the user asks for a process or checklist.",
                "Use when you want to reuse a previously mentioned method/SOP.",
            ],
            tags=kws,
            examples=[
                SkillExample(
                    input="Break this into best-practice, executable steps.",
                    output=None,
                )
            ],
            confidence=0.4,
            source=_source_obj(self._config, messages=messages, events=events),
        )
        return [candidate][:max_candidates]


class LLMSkillExtractor:
    def __init__(self, config: AutoSkillConfig, *, llm: Optional[LLM] = None) -> None:
        self._config = config
        self._llm = llm or build_llm(config.llm)

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
            # Encourage general skills by removing accounts/URLs/dates/etc before calling the LLM.
            payload = redact_obj(payload)

        system = (
            "You are AutoSkill's Skill Extractor.\n"
            "Task: Extract reusable, executable Skills from messages/events.\n"
            "If DATA.hint exists, treat it as an explicit extraction request.\n"
            "Quality-first: extract when reusable signal is reasonably clear, and skip only clearly weak or one-off candidates.\n"
            "\n"
            "### 1) EVIDENCE AND PROVENANCE (CRITICAL)\n"
            "- USER turns are the source of truth; ASSISTANT turns are supporting context only.\n"
            "- Do not extract requirements that appear only in assistant output unless user requested/confirmed/corrected/reinforced them.\n"
            "- If user and assistant conflict, follow user intent.\n"
            "- Weak acknowledgements ('ok', 'continue', 'sounds good') do not validate all assistant details.\n"
            "- Every major requirement must be traceable to user evidence (instruction/correction/rejection/restated rule).\n"
            "- Drop details with unclear user origin.\n"
            "- Reject assistant-invented specifics (checklists, thresholds, role maps, policy labels/taxonomies, detailed expansions) unless user explicitly requested/approved them; keep user-stated hard limits and mandatory steps as valid constraints.\n"
            "- If evidence is ambiguous or mostly assistant-authored, output {\"skills\": []}.\n"
            "\n"
            "### 2) RECENCY, TOPIC COHERENCE, AND RETRIEVED REFERENCE (CRITICAL)\n"
            "- Prioritize recent user rounds; use older context mainly to judge continuity vs topic switch.\n"
            "- Use the latest few user turns (about last 3-6 user messages) to detect intent/topic/task shifts.\n"
            "- Infer current work item = objective + deliverable/channel + operation class.\n"
            "- Boundary rule: detect the first recent user turn that introduces a new objective/deliverable/channel/task (including new audience) as the boundary turn.\n"
            "- If a boundary turn exists, treat it as topic switch: recent post-boundary intent is authoritative; use pre-boundary context only for switch judgment, and carry pre-boundary constraints only when restated after boundary.\n"
            "- If no boundary turn is detected, continue using broader context for continuity and stable constraints.\n"
            "- If multiple work items appear, keep only the latest active one.\n"
            "- Never mix constraints from different work items.\n"
            "- DATA.retrieved_reference is only identity context (update-like wording vs distinct-capability wording), never extraction evidence.\n"
            "- DATA.retrieved_reference.triggers (if present) are intent hints for identity matching only; do not treat them as new evidence.\n"
            "- If retrieved_reference is null/None, treat as no selected prior skill.\n"
            "- If extraction gates fail, output {\"skills\": []} regardless of similarity.\n"
            "- SAME capability requires alignment on objective + deliverable/channel + operation class + acceptance criteria.\n"
            "- If these dimensions materially differ in recent turns, treat as distinct capability.\n"
            "- On ambiguity, prefer distinct-capability wording over forced update wording.\n"
            "\n"
            "### 3) WHEN TO EXTRACT\n"
            "- DO NOT EXTRACT (return {\"skills\": []}) for one-shot/generic tasks with no user policy constraints, trivial common-knowledge logic, assistant-only requirements, or stale requirements not reflected in recent turns.\n"
            "- EXTRACT when user provides reusable constraints/policies, including:\n"
            "  - low threshold: one explicit, reusable user constraint can be sufficient (no repeated examples required);\n"
            "  - corrections/interventions or explicit must-do requirements;\n"
            "  - implementation/output policy (language/runtime/tooling, allowed/disallowed tech, code-vs-explanation ratio, comment density, output format/layout constraints such as document type or table usage, hard safety bounds, mandatory SOP steps, conciseness vs completeness);\n"
            "  - single-turn explicit policy change (one clear instruction is sufficient);\n"
            "  - revision feedback that changes generation policy (detail, specificity, completeness, evidence density, terminology level, tone, audience fit, structure strictness);\n"
            "  - explicit multi-step AI operation sequence (workflow/SOP);\n"
            "  - explicit schema/template requirements.\n"
            "- Decision boundary: content-only change (WHAT for this instance) usually does not extract; policy/process change (HOW across similar tasks) does extract.\n"
            "- Do not under-trigger on common task types: writing/rewrite/coding can still yield reusable skills when durable policy constraints are present.\n"
            "\n"
            "### 4) CONSTRAINTS OVER CONTENT + CAPABILITY/PAYLOAD + DE-IDENTIFICATION (CRITICAL)\n"
            "- Focus on HOW, not this-instance WHAT.\n"
            "- Capture both must-do requirements and must-not-do constraints.\n"
            "- Abstract specific feedback into reusable rules.\n"
            "- Prefer user-originated constraints; include assistant-proposed constraints only if user accepted/reiterated.\n"
            "- Keep capability invariants: transformation/workflow/constraints/output contract/quality checks/validation rules, including user-specified hard limits and required procedural steps.\n"
            "- Drop payload: topic facts, domain claims, project/research details, and long runtime content.\n"
            "- In name/description/# Goal, describe capability class, not current subject matter.\n"
            "- If runtime content is needed, use placeholders (for example: <SOURCE_CONTENT>, <TARGET_TOPIC>, <KEY_POINTS>).\n"
            "- Remove case-specific entities (org/team/person/address/project/product/repo/branch/ticket/account IDs, URLs/emails/phones/keys, exact dates/budgets/contracts, client references).\n"
            "- If de-identification removes core value or leaves generic advice, output {\"skills\": []}.\n"
            "- Reuse test: if the prompt cannot transfer to a similar different topic, output {\"skills\": []}.\n"
            "\n"
            "### 5) NO INVENTION + WORKFLOW RULE (CRITICAL)\n"
            "- Extract only logic directly supported by conversation evidence.\n"
            "- If user only gives constraints, do not invent step-by-step workflow.\n"
            "- Include # Workflow only when user explicitly specifies multi-stage AI operations.\n"
            "- Document structure/tone/sections belong in # Constraints & Style, not # Workflow.\n"
            "- Do not invent unrequested standards, thresholds, regulations, or technical specs.\n"
            "\n"
            "### 6) OUTPUT REQUIREMENTS AND FINAL CHECKS\n"
            "- Output ONLY strict JSON parseable by json.loads.\n"
            "- Schema: {\"skills\": [...]} with at most {max_candidates} items.\n"
            "- Language consistency: all fields (name, description, prompt, triggers, tags, examples) must match user instruction language.\n"
            "  - Example: Chinese input -> all fields in Chinese (for example: \"政府报告撰写规范\"); English input -> all fields  in English (for example: \"government-report-writing-policy\").\n"
            "- Generalize/de-identify aggressively; keep durable reusable procedures/constraints only.\n"
            "- Final checks before output:\n"
            "  - no case-specific proper nouns/one-off business facts in name/description/prompt/triggers/examples;\n"
            "  - name/description/# Goal describe capability invariants, not topical payload;\n"
            "  - major prompt constraints are user-evidenced;\n"
            "  - major constraints belong to one recent coherent work item;\n"
            "  - if retrieved_reference exists but recent intent differs in objective/deliverable/channel/audience, keep distinct capability.\n"
            "\n"
            "### 7) FIELD DEFINITIONS\n"
            "- name: concise and searchable; MUST explicitly encode primary user intent (what the user wants to accomplish), and include task/action plus topic/domain; include platform/channel context when user-evidenced (for example, WeChat Official Account, Xiaohongshu, Weibo/Sina, Douyin, Twitter/X, or other platforms); kebab-case for English; use reusable labels and avoid one-off entities.\n"
            "- description: 1-2 sentences, third person; state WHAT capability and WHEN to use; include domain/platform scope when it changes usage; avoid instance facts.\n"
            "- prompt: executable logic in Markdown with:\n"
            "  1) # Goal (required)\n"
            "  2) # Constraints & Style (required; include must-do and must-not-do)\n"
            "  3) # Workflow (optional; only for explicit multi-stage AI operations)\n"
            "- # Goal: transformation objective + output contract only; do not embed long topical payload.\n"
            "- Content strategy: keep user-specific requirements; do not add unrequested generic standards.\n"
            "- Resources: if needed, reference reusable assets as 'Execute script: scripts/...' or 'Read reference: references/...'.\n"
            "- triggers: 3-5 short intent phrases; include platform/channel intent when relevant; dedupe near-duplicate paraphrases.\n"
            "- tags: 1-6 keywords; include canonical domain/platform tags when user-evidenced; remove redundant synonyms.\n"
            "- examples: 0-3 short de-identified inputs.\n"
            "- confidence: 0.0-1.0 (lower for borderline-generic skills).\n"
            "\n"
            "### 8) MINDSET QUICK CHECKS\n"
            "- Is this reusable user/business-specific logic, not generic baseline ability?\n"
            "- Is there reusable method/policy/process that is hard to re-prompt every time?\n"
            "- A single explicit reusable policy constraint can be enough; do not require multiple examples.\n"
            "- Did user feedback revise generation policy (not just one-off facts)?\n"
            "- If not, output {\"skills\": []}.\n"
            "\n"
            "JSON validity: Escape newlines as \\n. No Markdown code blocks."
        )

        user = (
            f"{json.dumps(payload, ensure_ascii=False)}"
        )
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
            # Do not break ingest: fall back to heuristic extraction when the LLM is unstable.
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
            # Some models ignore JSON-only constraints and output analysis; try a best-effort recovery.
            recovered = _candidate_from_freeform_llm_text(
                text,
                source=_source_obj(self._config, messages=messages, events=events),
            )
            if recovered:
                return [recovered][:max_candidates]
            try:
                repaired = self._repair_to_json(
                    payload=payload, draft=text, max_candidates=max_candidates
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
                # Do not break ingest: if repair fails, fall back to heuristic extraction.
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
                # Even the repair attempt may return non-JSON; try recovery once more.
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
                # Final fallback: heuristic extraction.
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
        system = (
            "You are a JSON output fixer.\n"
            "Given DATA (and optionally DRAFT), output ONLY strict JSON: {\"skills\": [...]}.\n"
            "No Markdown, no commentary, no extra text.\n"
            f"Return at most {max_candidates} skills; if extraction fails output {{\"skills\": []}}.\n"
            "Apply the same constraints:\n"
            "- [A] Role and evidence scope\n"
            "- Skills are SKILL.md onboarding guides: keep only reusable, non-obvious procedure/preferences.\n"
            "- DATA.retrieved_reference is auxiliary identity context (update-vs-new), not extraction evidence.\n"
            "- DATA.retrieved_reference.triggers (if present) are intent hints for identity matching only; not new evidence.\n"
            "- If DATA.retrieved_reference is null/None, treat as no selected prior skill; do not force update wording.\n"
            "- If user evidence is insufficient, return {\"skills\": []} even when retrieved_reference is similar.\n"
            "- Prioritize user-evidenced constraints; do not add assistant-only constraints unless user-confirmed.\n"
            "- A single explicit reusable user policy can be sufficient extraction signal; do not require repeated examples.\n"
            "- Weak acknowledgements ('ok', 'continue', etc.) are not evidence for assistant details.\n"
            "- Remove assistant-authored expansions (invented thresholds, role matrices, policy taxonomy) unless user explicitly requested/confirmed; keep user-provided hard limits and mandatory steps.\n"
            "- [B] Recency and capability identity\n"
            "- Prioritize recent turns; use older turns mainly for continuity/topic-switch judgment.\n"
            "- Use the latest few user turns (about last 3-6 user messages) to detect intent/topic/task shifts.\n"
            "- SAME capability requires alignment on objective + deliverable/channel + operation class + acceptance criteria.\n"
            "- If recent turns differ from retrieved_reference in objective/deliverable/channel/audience, keep distinct-capability wording.\n"
            "- Boundary rule: detect the first recent user turn that introduces a new objective/deliverable/channel/task (including new audience) as the boundary turn.\n"
            "- If a boundary turn exists, keep only post-boundary constraints for the active topic and do not inherit pre-boundary constraints unless restated.\n"
            "- If no boundary turn is detected, keep broader-context continuity and reuse still-active constraints.\n"
            "- [C] Content construction and field intent\n"
            "- name: concise and searchable; MUST explicitly encode primary user intent (what the user wants to accomplish), and include task/action plus topic/domain; include platform/channel context when user-evidenced (for example, WeChat Official Account, Xiaohongshu, Weibo/Sina, Douyin, Twitter/X, or other platforms); kebab-case for English; use reusable labels and avoid one-off entities.\n"
            "- description: 1-2 sentences, third person; include WHEN to use; include domain/platform scope when relevant; avoid instance-specific facts.\n"
            "- prompt: ALWAYS English; imperative/infinitive; numbered steps + checks + output format; no conversation references.\n"
            "- Capability-vs-payload: keep reusable method/constraints; drop this-instance topical payload.\n"
            "- In # Goal, keep transformation objective/output contract only; no long topic-specific content.\n"
            "- If runtime content is needed, use placeholders (for example: <SOURCE_CONTENT>, <TARGET_TOPIC>, <KEY_POINTS>).\n"
            "- prompt must include both must-do requirements and must-not-do constraints.\n"
            "- Keep revision feedback that changes generation policy (quality/detail/style/audience/structure).\n"
            "- Keep reusable implementation/output policies (language/tooling, allowed/disallowed tech, code-vs-explanation ratio, comment density, strict output form, format/layout constraints, hard safety bounds, mandatory SOP steps).\n"
            "- triggers/tags: preserve user-evidenced domain/platform intent with canonical labels; dedupe near-duplicates; never include account-specific names.\n"
            "- prompt may include short \"Bundled resources (optional)\" suggestions (scripts/references/assets), not large pasted content.\n"
            "- [D] De-identification and portability\n"
            "- Remove case-specific entities (org/team/person, addresses, project/product/repo, ticket/account IDs, URLs/emails/phones, exact dates/budgets/contracts).\n"
            "- Keep only portable capability constraints; if generic after de-identification, return {\"skills\": []}.\n"
            "- [E] Output language and JSON validity\n"
            "- Language: name/description/prompt/triggers/tags/examples match dominant input language.\n"
            "- Language example: Chinese input -> all fields Chinese (for example: \"代码注释风格约束\"); English input -> all fields English (for example: \"code-comment-style-constraints\").\n"
            "- JSON validity: escape newlines inside strings as \\n.\n"
        )
        user = (
            f"DATA:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            f"DRAFT:\n{(draft or '').strip()[-2500:]}"
        )
        return self._llm.complete(system=system, user=user, temperature=0.0)


def _candidate_from_freeform_llm_text(
    text: str, *, source: Optional[Dict[str, Any]]
) -> Optional[SkillCandidate]:
    """
    Best-effort recovery when the LLM ignores the JSON-only constraint and outputs
    semi-structured analysis (common with some reasoning models).
    """

    raw = (text or "").strip()
    if not raw:
        return None

    cleaned = raw.replace("**", "").replace("*", "").replace("`", "")
    lines = [re.sub(r"^\s*[*\-•]\s*", "", ln).strip() for ln in cleaned.splitlines()]
    lines = [ln for ln in lines if ln]

    sections = {
        "name": _find_section_index(lines, ["name"]),
        "description": _find_section_index(lines, ["description"]),
        "prompt": _find_section_index(lines, ["prompt", "instructions"]),
        "triggers": _find_section_index(lines, ["triggers"]),
        "tags": _find_section_index(lines, ["tags"]),
        "examples": _find_section_index(lines, ["examples"]),
    }

    def slice_until(idx: Optional[int], stop_keys: List[str]) -> List[str]:
        if idx is None:
            return []
        start = idx + 1
        end = len(lines)
        for j in range(start, len(lines)):
            low = lines[j].lower()
            if any(k in low for k in stop_keys):
                end = j
                break
        return lines[start:end]

    stop_any = [
        "description",
        "prompt",
        "instructions",
        "triggers",
        "tags",
        "examples",
    ]

    name_block = slice_until(sections["name"], stop_any)
    name = _pick_choice_or_value(name_block, primary_keys=["name"])

    desc_block = slice_until(sections["description"], stop_any)
    description = _pick_choice_or_value(desc_block, primary_keys=["description"])

    prompt_block = slice_until(
        sections["prompt"],
        ["triggers", "tags", "examples"],
    )
    prompt_lines = _drop_leading_markers(
        prompt_block,
        markers=["draft", "prompt", "instructions"],
    )
    instructions = "\n".join(prompt_lines).strip()

    trig_block = slice_until(
        sections["triggers"], ["tags", "examples"]
    )
    triggers = _extract_bullets(trig_block)[:7]

    tags_block = slice_until(sections["tags"], ["examples"])
    tags = _extract_bullets(tags_block)[:6]

    confidence = 0.6
    m = re.search(r"confidence\s*[:：]\s*([01](?:\.\d+)?)", cleaned, re.IGNORECASE)
    if m:
        try:
            confidence = float(m.group(1))
        except ValueError:
            confidence = 0.6

    if not name:
        stop_idx = sections.get("prompt")
        search = lines[:stop_idx] if isinstance(stop_idx, int) else lines[: min(len(lines), 40)]
        ignore = {
            "description",
            "prompt",
            "instructions",
            "triggers",
            "tags",
            "examples",
            "confidence",
            "analysis",
            "draft",
            "data",
            "task",
            "role",
        }
        for ln in search:
            m2 = re.match(r"^\s*([^:：]{1,40})\s*[:：]\s*(.+)$", ln)
            if not m2:
                continue
            key = (m2.group(1) or "").strip().lower()
            value = (m2.group(2) or "").strip()
            if not value or key in ignore:
                continue
            if len(value) <= 80:
                name = value
                break

    if not name:
        for ln in lines[: min(len(lines), 40)]:
            low = ln.lower()
            if any(k in low for k in ["analysis", "draft", "data", "task", "role"]):
                continue
            if 3 <= len(ln) <= 80:
                name = ln.strip()
                break

    if not name or not instructions:
        return None

    if not triggers:
        triggers = [
            "Use when the user asks for this process/method.",
            "Use when you need to break a request into executable steps.",
            "Use when you must include checks and rollback/fallback plans.",
        ]

    if not tags:
        tags = keywords(f"{name}\n{description}\n{instructions}", limit=4)

    return SkillCandidate(
        name=name.strip()[:80],
        description=(description or name).strip()[:300],
        instructions=instructions.strip(),
        triggers=[t.strip() for t in triggers if t and t.strip()],
        tags=[t.strip() for t in tags if t and t.strip()],
        examples=[],
        confidence=max(0.0, min(1.0, float(confidence))),
        source=source,
    )


def _find_section_index(lines: List[str], needles: List[str]) -> Optional[int]:
    for i, ln in enumerate(lines):
        low = ln.lower()
        for n in needles:
            n_low = n.lower()
            if not n_low:
                continue
            if re.search(rf"(?:^|\s){re.escape(n_low)}\s*[:：]", low):
                return i
        if any(n.lower() in low for n in needles):
            # Fallback: substring match, but avoid meta lines like "fields: name, description, ..."
            if any(re.search(rf"\b{re.escape(n.lower())}\b\s*,", low) for n in needles if n.isascii()):
                continue
            return i
    return None


def _pick_choice_or_value(block: List[str], *, primary_keys: List[str]) -> str:
    if not block:
        return ""
    choices = []
    for ln in block:
        m = re.search(r"(?:choice|selected|selection)\s*[:：]\s*(.+)$", ln, re.IGNORECASE)
        if m:
            v = m.group(1).strip()
            if v:
                choices.append(v)
    if choices:
        return choices[-1]
    for ln in block:
        for k in primary_keys:
            m = re.search(rf"(?:{re.escape(k)})\s*[:：]\s*(.+)$", ln, re.IGNORECASE)
            if m:
                v = m.group(1).strip()
                if v:
                    return v
    for ln in block:
        if any(
            x in ln.lower()
            for x in [
                "draft",
                "choice",
                "analysis",
            ]
        ):
            continue
        if len(ln) <= 1:
            continue
        return ln.strip()
    return ""


def _extract_bullets(block: List[str]) -> List[str]:
    out: List[str] = []
    for ln in block or []:
        s = re.sub(r"^\s*[*\-•]\s*", "", ln).strip()
        s = s.strip("：: ").strip()
        if not s:
            continue
        if any(
            s.lower().startswith(p)
            for p in ["tags", "triggers", "examples", "description"]
        ):
            continue
        out.append(s)
    return out


def _drop_leading_markers(lines: List[str], *, markers: List[str]) -> List[str]:
    if not lines:
        return []
    start = 0
    for i, ln in enumerate(lines):
        low = ln.lower()
        if any(m.lower() in low for m in markers) and (":" in low or "：" in low):
            start = i + 1
            continue
        break
    trimmed = [ln.strip() for ln in lines[start:] if ln.strip()]
    return trimmed


def _candidate_from_obj(obj: Any, *, source: Optional[Dict[str, Any]]) -> Optional[SkillCandidate]:
    if not isinstance(obj, dict):
        return None
    name = str(obj.get("name") or "").strip()
    description = str(obj.get("description") or "").strip()
    instructions = str(obj.get("prompt") or obj.get("instructions") or "").strip()
    if not name or not instructions:
        return None

    triggers = [str(t).strip() for t in (obj.get("triggers") or []) if str(t).strip()]
    tags = [str(t).strip() for t in (obj.get("tags") or []) if str(t).strip()]
    examples_in = obj.get("examples") or []
    examples: List[SkillExample] = []
    if isinstance(examples_in, list):
        for e in examples_in[:6]:
            if not isinstance(e, dict):
                continue
            inp = str(e.get("input") or "").strip()
            if not inp:
                continue
            examples.append(
                SkillExample(
                    input=inp,
                    output=(str(e.get("output")).strip() if e.get("output") else None),
                    notes=(str(e.get("notes")).strip() if e.get("notes") else None),
                )
            )
    conf_raw = obj.get("confidence")
    try:
        confidence = float(conf_raw) if conf_raw is not None else 0.6
    except (TypeError, ValueError):
        confidence = 0.6

    return SkillCandidate(
        name=name,
        description=description or name,
        instructions=instructions,
        triggers=triggers,
        tags=tags,
        examples=examples,
        confidence=max(0.0, min(1.0, confidence)),
        source=source,
    )


def _flatten_sources(
    *, messages: Optional[List[Dict[str, Any]]], events: Optional[List[Dict[str, Any]]]
) -> str:
    chunks: List[str] = []
    for m in messages or []:
        role = str(m.get("role") or "").strip().lower()
        content = m.get("content") or ""
        if not content:
            continue
        c = str(content)
        if role == "assistant":
            c2 = c.strip()
            if c2.startswith("Offline mode:") or c2.startswith("(LLM error:"):
                continue
        chunks.append(c)
    for e in events or []:
        chunks.append(json.dumps(e, ensure_ascii=False))
    return "\n".join(chunks)


def _heuristic_instructions(text: str) -> str:
    steps = _extract_steps(text)
    if len(steps) >= 2:
        lines: List[str] = []
        lines.append(
            "Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):"
        )
        had_placeholders = False
        for i, s in enumerate(steps[:10], start=1):
            safe = _sanitize_step_for_prompt(s, i)
            had_placeholders = had_placeholders or safe.startswith("<STEP_")
            lines.append(f"{i}) {safe}")
        lines.append("")
        lines.append("For each step, include: action, checks, and failure rollback/fallback plan.")
        lines.append(
            "Output format: for each step number, provide status/result and what to do next."
        )
        if had_placeholders:
            lines.append("If any step is a placeholder (e.g., <STEP_1>), ask the user to clarify it.")
        return "\n".join(lines).strip()

    return "\n".join(
        [
            "Follow these steps (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):",
            "1) Define the goal and acceptance criteria",
            "2) List key prerequisites/constraints",
            "3) Provide executable steps (with checks and rollback)",
            "4) Produce the final result and next actions",
            "",
            "Output format: numbered steps with result and next action.",
        ]
    ).strip()


def _heuristic_name(text: str, kws: List[str]) -> str:
    low = (text or "").lower()
    if any(x in low for x in ["release", "deploy", "deployment", "go-live", "rollout"]):
        return "Standard release process"
    if any(x in low for x in ["postmortem", "retrospective", "incident review"]):
        return "Run a postmortem and produce action items"
    return " / ".join(kws) if kws else "General process skill"


def _extract_steps(text: str) -> List[str]:
    t = (text or "").strip()
    if not t:
        return []

    for sep in ("：", ":"):
        if sep in t:
            t = t.split(sep, 1)[1].strip()
            break

    arrow_splits = re.split(r"\s*(?:->|→|⇒|=>|➡|➜)\s*", t)
    arrow_splits = [s for s in arrow_splits if s and s.strip()]
    if len(arrow_splits) >= 2:
        steps: List[str] = []
        for s in arrow_splits:
            for part in str(s).splitlines():
                cleaned = part.strip()
                cleaned = re.sub(r"^[^\w]+", "", cleaned).strip()
                cleaned = re.sub(r"[^\w]+$", "", cleaned).strip()
                if not cleaned:
                    continue
                if _normalize_ack_line(cleaned) in _ACK_KEYS:
                    continue
                steps.append(cleaned)
        if len(steps) >= 2:
            return steps

    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    numbered = []
    for ln in lines:
        ln2 = re.sub(r"^\s*(?:[-*•]|\d+\s*[\.\)\-:])\s*", "", ln).strip()
        # Ignore low-information acknowledgement lines.
        if _normalize_ack_line(ln2) in _ACK_KEYS:
            continue
        if len(ln2) <= 2:
            continue
        if ln2:
            numbered.append(ln2)
    return numbered[:10]


def _source_obj(
    config: AutoSkillConfig,
    *,
    messages: Optional[List[Dict[str, Any]]],
    events: Optional[List[Dict[str, Any]]],
) -> Optional[Dict[str, Any]]:
    if not config.store_sources:
        return None
    return {"messages": messages or [], "events": events or []}
