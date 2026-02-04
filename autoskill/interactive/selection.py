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
        if used + len(block) + 1 > max_chars:
            break
        lines.append(block)
        used += len(block) + 1
    return "\n".join(reversed(lines)).strip()


def _skill_brief(skill: Skill, *, max_prompt_chars: int) -> Dict[str, Any]:
    prompt = (skill.instructions or "").strip()
    preview = prompt[: max(0, int(max_prompt_chars))].strip() if max_prompt_chars else ""
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

        try:
            out = self.llm.complete(system=system, user=user, temperature=0.0)
        except Exception:
            return []

        try:
            obj = json_from_llm_text(out)
        except Exception:
            return []

        selected_ids = _parse_selected_ids(obj)
        if not selected_ids:
            return []

        allowed = {s.id: s for s in skills}
        selected: List[Skill] = []
        for sid in selected_ids:
            if sid in allowed:
                selected.append(allowed[sid])
        if not selected:
            return []
        return selected[: max(0, int(self.max_selected))]


def _json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)
