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
    ) -> List[SkillCandidate]:
        payload = {
            "user_id": user_id,
            "messages": messages or [],
            "events": events or [],
            "max_candidates": max_candidates,
            "hint": (str(hint).strip() if hint and str(hint).strip() else None),
        }
        if self._config.redact_sources_before_llm:
            # Encourage general skills by removing accounts/URLs/dates/etc before calling the LLM.
            payload = redact_obj(payload)

        system = (
            "You are AutoSkill's Skill Extractor.\n"
            "Task: Extract reusable, executable Skills from the provided messages/events.\n"
            "If DATA.hint is provided, treat it as an explicit user request for what to extract.\n"
            "\n"
            "### EVIDENCE PRIORITY (CRITICAL)\n"
            "- Prioritize USER messages as the primary evidence for extraction.\n"
            "- Treat ASSISTANT messages as contextual artifacts, not authoritative requirements.\n"
            "- Do NOT extract a rule/constraint if it appears only in assistant output and is never confirmed, requested, corrected, or reinforced by the user.\n"
            "- If user and assistant content conflict, follow user intent.\n"
            "- If evidence is ambiguous, output {\"skills\": []}.\n"
            "\n"
            "### CRITICAL FILTER: WHEN TO EXTRACT\n"
            "To avoid noise, you must distinguish between 'Standard LLM Capabilities' (DO NOT EXTRACT) and 'Specialized Skills' (EXTRACT).\n"
            "\n"
            "1. DO NOT EXTRACT (Output {\"skills\": []}) if:\n"
            "   - The user asked for a standard task (e.g., 'Write a poem', 'Translate this', 'Fix this bug') AND accepted the result without modification.\n"
            "   - The interaction is simple Q&A or a one-shot generic request.\n"
            "   - The logic is trivial or purely based on the model's training data (Common Knowledge).\n"
            "   - The only apparent 'requirements' come from assistant wording, not user-stated intent/feedback.\n"
            "\n"
            "2. EXTRACT ONLY IF:\n"
            "   - **User Intervention:** The user corrected the output, provided a specific example, defined a style, or enforced a constraint (e.g., 'No, use JSON format', 'Make it more sarcastic'). Extract the *Preference/Constraint*.\n"
            "   - **User Positive Requirements:** The user explicitly stated what the output MUST include (target outcome, required sections, required tone, required checks, required quality bar). Extract these as *must-do requirements*.\n"
            "   - **Policy-Level Revision Feedback (HIGH PRIORITY):** If the user revises prior output by changing generation policy (detail depth, specificity, completeness, evidence density, terminology level, tone, audience fit, structure strictness), treat it as reusable preference/constraint and extract.\n"
            "   - **Complex Workflow:** The task involves a multi-step logic chain, specific reasoning order, or a defined SOP (Standard Operating Procedure), even if the user didn't correct it. (e.g., 'First analyze X, then extract Y, finally format as Z'). Extract the *Process*.\n"
            "   - **Explicit Template:** The user provided a specific schema, data structure, or output template to follow.\n"
            "   - **Decision Boundary:** If feedback changes WHAT facts/content to include for only this instance, usually do not extract. If feedback changes HOW outputs should be generated across similar tasks, extract.\n"
            "\n"
            "### EXTRACTION STRATEGY: CONSTRAINTS OVER CONTENT\n"
            "**CRITICAL:** Focus on the 'HOW', not the 'WHAT'.\n"
            "- **Discard Content:** Do not capture the specific topic being discussed (e.g., 'Government Report on Agriculture').\n"
            "- **Capture Requirements:** Capture both (a) what MUST be done and included, and (b) what MUST NOT be done.\n"
            "- **Capture Constraints:** Capture the RULES applied to that topic (e.g., 'Direct language', 'No hallucinations', 'Word format', 'Concrete points').\n"
            "- **User-Origin Preference:** Prefer constraints directly stated by the user; include assistant-proposed constraints only when user explicitly accepts or reiterates them.\n"
            "- **Abstraction:** Turn specific feedback into general rules. \n"
            "  - User: 'Don't make this report too thin, hit the problem directly.' -> Skill Rule: 'Ensure density of information; avoid fluff; address core issues directly.'\n"
            "  - User: 'Use standard Word format.' -> Skill Rule: 'Output must be compatible with standard .docx formatting conventions.'\n"
            "\n"
            "### ANTI-HALLUCINATION / NO INVENTION (CRITICAL)\n"
            "- **Strict Adherence:** You must ONLY extract logic, constraints, and preferences that explicitly appear in or are directly derived from the conversation.\n"
            "- **User-Evidence Rule:** Candidate skill requirements should be traceable to user turns (requests, corrections, approvals, objections), not just assistant outputs.\n"
            "- **Feedback Capture Rule:** When user feedback modifies generation policy, preserve it as portable rules (both must-do and must-not-do) instead of treating it as one-off wording edits.\n"
            "- **NO Phantom Workflows:** \n"
            "  - If the user ONLY provided constraints (e.g., 'No hallucinations', 'Word format', 'Sharp insights'), **DO NOT invent a 'Step-by-Step Workflow'** (e.g., do NOT make up 'Step 1: Analyze topic, Step 2: Draft content...').\n"
            "  - ONLY include a Workflow if the user explicitly described a sequence of actions (e.g., 'First do A, then do B').\n"
            "- **Do Not Invent Details:** \n"
            "  - If the user says 'Word format', do NOT invent 'GB/T 9704–2012' or 'indent 2 chars'. Just write 'Ensure compatibility with Microsoft Word formatting'.\n"
            "  - If the user says 'Government Report', do NOT invent specific regulations unless the user mentioned them.\n"
            "\n"
            "### ANTI-HALLUCINATION: THE 'STRUCTURE VS. WORKFLOW' RULE\n"
            "You must distinguish between the **Structure of the Output** and the **Workflow of the Agent**.\n"
            "\n"
            "1. **Document Structure is NOT a Workflow:**\n"
            "   - If the user says: 'The report needs an Intro, then a Body, then a Conclusion.'\n"
            "   - **CORRECT:** Put this in `# Constraints & Style` as an 'Output Template'.\n"
            "   - **WRONG:** Do NOT create a Workflow like 'Step 1: Write Intro. Step 2: Write Body...'. This is content structuring, not agent logic.\n"
            "\n"
            "2. **Agent Workflow requires Action Sequences:**\n"
            "   - Only extract a `# Workflow` if the user asks the *AI* to perform a multi-stage operation.\n"
            "   - **Valid Workflow Example:** 'First translate the text, then check for grammar errors, and finally format it as JSON.' (Distinct operations).\n"
            "   - **Invalid Workflow Example:** 'Write a story with a beginning, middle, and end.' (This is just Structure -> Constraints).\n"
            "\n"
            "### REQUIREMENTS\n"
            "- Output ONLY strict JSON that can be parsed by json.loads.\n"
            "- Output schema: {\"skills\": [...]}. Return at most {max_candidates} skills.\n"
            "- **Language Consistency (CRITICAL):** All fields (name, description, prompt, triggers, tags, examples) MUST be written in the **same language as the user's conversational instructions/intent**.\n"
            "  - Example: User says '帮我优化代码' -> All fields are Chinese.\n"
            "  - Example: User says 'Review this doc' -> All fields are English.\n"
            "- Generalize and de-identify: Replace specific names, orgs, URLs, dates with placeholders <PROJECT>, <ENV>, <TOOL>.\n"
            "\n"
            "### FIELD DEFINITIONS\n"
            "- name: Concise, specific, kebab-case (e.g., 'report-writing-style-guide', '政府报告撰写'). Use terminology from the user's domain.\n"
            "- description: The **Primary Retrieval Trigger**. 1-2 sentences in third person. Clearly state WHAT the skill does and WHEN to use it (Context).\n"
            "- prompt: The executable logic. \n"
            "  - **Structure:** Use Markdown. \n"
            "    1. **# Goal** (Required)\n"
            "    2. **# Constraints & Style** (Required: Capture specific user rules, including both must-do requirements and must-not-do constraints)\n"
            "    3. **# Workflow** (**OPTIONAL**: Include this section **ONLY IF** the user explicitly defined a multi-step process. If the user only gave constraints, **OMIT THIS SECTION completely**.)\n"
            "       - **INCLUDE IF:** The user explicitly ordered distinct **operations** (e.g., 'Search -> Analyze -> Write').\n"
            "       - **OMIT IF:** The user only described the document's sections or tone. **If the 'steps' are just 'Write Section A, then Section B', move them to Constraints.**\n"
            "  - **Content Strategy:** Capture the *User's Specific Requirements*. Do NOT add generic industry standards unless requested.\n"
            "  - **Positive Requirements:** Explicitly include user must-do requirements (e.g., 'Include risk section', 'Use concise official tone', 'Provide concrete acceptance checks').\n"
            "  - **Negative Constraints:** Explicitly list what NOT to do based on user feedback (e.g., 'Do not use metaphors').\n"
            "  - **Resources:** If the logic implies using a reusable script or a large reference doc, write instruction to 'Execute script: scripts/...' or 'Read reference: references/...'.\n"
            "- triggers: 3-5 short, concrete phrases representing user intent (e.g., 'Format this as a weekly report', 'Check for compliance').\n"
            "- tags: 1-6 keywords for categorization.\n"
            "- examples: 0-3 short, de-identified input demonstrating the skill's effect.\n"
            "- confidence: Number between 0.0 and 1.0. (Lower confidence if the skill is borderline generic).\n"
            "\n"
            "### SKILL EXTRACTION MINDSET\n"
            "- Ask: \"Is this logic specific to THIS user/business, or can any AI do it?\" -> If it's specific, extract it.\n"
            "- Ask: \"Is this a complex sequence of steps that is hard to prompt manually?\" -> If yes, extract it.\n"
            "- Ask: \"Did the user revise the previous answer by changing generation policy (quality/detail/style/audience/structure), not just one-off facts?\" -> If yes, extract those rules as a skill.\n"
            "- Otherwise, output {\"skills\": []}.\n"
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
            "- Skills are onboarding guides (SKILL.md): keep only reusable, non-obvious procedure/preferences.\n"
            "- name: concise and specific; prefer kebab-case for English.\n"
            "- description: 1-2 sentences, third person; include WHEN to use.\n"
            "- prompt: ALWAYS English; imperative/infinitive form; numbered steps + checks + output format; no conversation references.\n"
            "- prompt must capture BOTH user must-do requirements and must-not-do constraints.\n"
            "- prioritize constraints evidenced by user messages; do not introduce assistant-only constraints unless user-confirmed.\n"
            "- If DATA includes revision feedback that changes generation policy (quality/detail/style/audience/structure), retain those rules in the prompt.\n"
            "- prompt may include a short \"Bundled resources (optional)\" section suggesting scripts/references/assets; do not paste large content.\n"
            "- Language: name/description/triggers/tags/examples match dominant input language; prompt is ALWAYS English.\n"
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
