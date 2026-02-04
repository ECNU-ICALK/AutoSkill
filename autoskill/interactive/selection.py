"""
Skill selection for context injection.

Retrieval can surface potentially relevant Skills, but not every retrieved Skill should be injected into
the assistant's context. This module provides an LLM-based selector that decides (per turn) whether
Skills should be used and which ones to include.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ..llm.base import LLM
from ..models import Skill
from ..utils.json import json_from_llm_text
from ..utils.text import keywords
from ..utils.units import text_units, truncate_keep_head


def _format_history(
    messages: List[Dict[str, Any]],
    *,
    max_turns: int,
    max_chars: int,
    exclude_last_user: bool,
) -> str:
    max_msgs = max(0, int(max_turns)) * 2
    window = messages[-max_msgs:] if max_msgs else messages
    if exclude_last_user and window:
        last = window[-1]
        if str(last.get("role") or "").strip().lower() == "user":
            window = window[:-1]

    lines: List[str] = []
    used = 0
    for m in reversed(window):
        role = str(m.get("role") or "").strip().lower()
        content = str(m.get("content") or "").strip()
        if not content:
            continue
        prefix = (
            "User: "
            if role == "user"
            else "Assistant: "
            if role == "assistant"
            else f"{role.title()}: "
        )
        block = prefix + content
        block_units = text_units(block)
        if used + block_units > max_chars:
            break
        lines.append(block)
        used += block_units
    return "\n".join(reversed(lines)).strip()


def _skill_brief(skill: Skill, *, max_prompt_chars: int) -> Dict[str, Any]:
    prompt = (skill.instructions or "").strip()
    preview = (
        truncate_keep_head(prompt, max_units=max(0, int(max_prompt_chars)), marker="").strip()
        if max_prompt_chars
        else ""
    )
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "tags": list((skill.tags or [])[:8]),
        "triggers": list((skill.triggers or [])[:8]),
        "prompt_preview": preview,
        "owner": skill.user_id,
    }


def _parse_selected_ids(obj: Any) -> List[str]:
    if isinstance(obj, dict):
        ids = obj.get("selected_skill_ids") or obj.get("skill_ids") or obj.get("ids") or []
        if isinstance(ids, list):
            out: List[str] = []
            for x in ids:
                s = str(x or "").strip()
                if s:
                    out.append(s)
            return out
        if isinstance(ids, str) and ids.strip():
            return [ids.strip()]
        use = obj.get("use_skills")
        if isinstance(use, bool) and not use:
            return []
    if isinstance(obj, list):
        out2: List[str] = []
        for x in obj:
            s = str(x or "").strip()
            if s:
                out2.append(s)
        return out2
    if isinstance(obj, str) and obj.strip():
        return [obj.strip()]
    return []

def _fallback_select_by_overlap(query: str, skills: List[Skill]) -> List[Skill]:
    """
    Conservative fallback when the selector LLM fails to return parseable JSON.

    - If there is only one candidate, select it.
    - Otherwise, select the single skill with the highest keyword overlap with the query.
    """

    if not skills:
        return []
    if len(skills) == 1:
        return skills[:1]

    q_tokens = {t.lower() for t in keywords(query or "", limit=24) if t}
    if not q_tokens:
        return []

    best: Skill | None = None
    best_overlap = 0
    for s in skills:
        text = "\n".join(
            [
                str(s.name or ""),
                str(s.description or ""),
                " ".join(s.tags or []),
                "\n".join(s.triggers or []),
            ]
        )
        s_tokens = {t.lower() for t in keywords(text, limit=48) if t}
        overlap = len(q_tokens & s_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best = s

    if best is None or best_overlap <= 0:
        return []
    return [best]


def _clean_selector_output(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
    for prefix in ("JSON:", "Output:", "Response:"):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix) :].strip()
    return raw


@dataclass
class LLMSkillSelector:
    """
    Uses an LLM to decide which retrieved Skills (if any) should be injected into the assistant context.
    """

    llm: LLM
    max_history_turns: int = 6
    max_history_chars: int = 2000
    max_prompt_preview_chars: int = 240
    max_selected: int = 3

    def select(
        self,
        *,
        query: str,
        messages: List[Dict[str, Any]],
        skills: List[Skill],
    ) -> List[Skill]:
        q = str(query or "").strip()
        if not q or not skills:
            return []

        history = _format_history(
            messages,
            max_turns=int(self.max_history_turns),
            max_chars=int(self.max_history_chars),
            exclude_last_user=True,
        )

        candidates = [_skill_brief(s, max_prompt_chars=int(self.max_prompt_preview_chars)) for s in skills]
        data = {
            "query": q,
            "history": history,
            "candidates": candidates,
            "max_selected": int(self.max_selected),
        }

        system = (
            "You are AutoSkill's skill selector for retrieval augmentation.\n"
            "Task: decide which of the retrieved Skills should be injected into the assistant's context to answer the current query.\n"
            "Be conservative: select only Skills that are clearly relevant and will materially help.\n"
            "It is OK to select none.\n"
            "\n"
            "Selection rules:\n"
            "- Only select from the provided skill IDs.\n"
            "- Prefer user skills over library skills when equally relevant.\n"
            "- Do not select generic or unrelated skills.\n"
            "- Select at most max_selected.\n"
            "\n"
            "Output ONLY strict JSON (no Markdown, no commentary):\n"
            "{\"use_skills\": true|false, \"selected_skill_ids\": [\"...\"], \"reason\": \"...\"}\n"
            "Set use_skills=true only if selected_skill_ids is non-empty.\n"
        )
        user = f"{__name__}.DATA:\n{_json_dumps(data)}"

        out = ""
        try:
            out = self.llm.complete(system=system, user=user, temperature=0.0)
        except Exception:
            out = ""
        obj: Any = None
        try:
            cleaned = _clean_selector_output(out)
            if cleaned:
                obj = json_from_llm_text(cleaned)
        except Exception:
            obj = None

        # Some providers may return empty output or non-JSON reasoning. Retry once with a repair prompt.
        if obj is None:
            repair_system = (
                "You are a JSON output fixer.\n"
                "Task: return ONLY strict JSON for skill selection; no Markdown, no commentary, no extra text.\n"
                "Schema:\n"
                "{\"use_skills\": true|false, \"selected_skill_ids\": [\"...\"], \"reason\": \"...\"}\n"
                "Rules:\n"
                "- Only select from the provided candidate IDs.\n"
                "- Select none if no candidate is clearly relevant.\n"
                "- Set use_skills=true only if selected_skill_ids is non-empty.\n"
            )
            draft = (out or "").strip()
            if len(draft) > 3000:
                draft = draft[-3000:]
            repair_user = f"DATA:\n{_json_dumps(data)}\n\nDRAFT:\n{draft}"
            try:
                out2 = self.llm.complete(system=repair_system, user=repair_user, temperature=0.0)
            except Exception:
                out2 = ""
            try:
                cleaned2 = _clean_selector_output(out2)
                if cleaned2:
                    obj = json_from_llm_text(cleaned2)
            except Exception:
                obj = None

        if obj is None:
            return _fallback_select_by_overlap(q, skills)[: max(0, int(self.max_selected))]

        selected_ids = _parse_selected_ids(obj)
        if not selected_ids:
            return _fallback_select_by_overlap(q, skills)[: max(0, int(self.max_selected))]

        allowed = {s.id: s for s in skills}
        selected: List[Skill] = []
        for sid in selected_ids:
            if sid in allowed:
                selected.append(allowed[sid])
        if not selected:
            return _fallback_select_by_overlap(q, skills)[: max(0, int(self.max_selected))]
        return selected[: max(0, int(self.max_selected))]


def _json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)
