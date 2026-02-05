"""
Query rewriting for retrieval.

Goal:
- Rewrite the current user query into a standalone, information-dense search query using a short
  conversation history window.
- The rewritten query is then embedded and used for skill retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ..llm.base import LLM
from ..utils.json import json_from_llm_text
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
        prefix = "User: " if role == "user" else "Assistant: " if role == "assistant" else f"{role.title()}: "
        block = prefix + content
        block_units = text_units(block)
        if used + block_units > max_chars:
            break
        lines.append(block)
        used += block_units
    return "\n".join(reversed(lines)).strip()


def _clean_rewritten_query(text: str) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    if raw.startswith("```"):
        raw = raw.strip("`").strip()

    # If the model returned JSON, try to extract a query-like field.
    try:
        obj = json_from_llm_text(raw)
        if isinstance(obj, dict):
            for k in ("query", "rewritten_query", "search_query", "rewrite"):
                v = obj.get(k)
                if isinstance(v, str) and v.strip():
                    raw = v.strip()
                    break
    except Exception:
        pass

    # Remove common labels.
    for prefix in (
        "Rewritten search query:",
        "Rewritten query:",
        "Search query:",
        "Query:",
    ):
        if raw.lower().startswith(prefix.lower()):
            raw = raw[len(prefix) :].strip()

    # Collapse whitespace and strip surrounding quotes.
    raw = " ".join(raw.split())
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1].strip()
    return raw


@dataclass
class LLMQueryRewriter:
    llm: LLM
    max_history_turns: int = 6
    max_history_chars: int = 2000
    max_query_chars: int = 256

    def rewrite(
        self,
        *,
        query: str,
        messages: List[Dict[str, Any]],
    ) -> str:
        q = str(query or "").strip()
        if not q:
            return ""

        history = _format_history(
            messages,
            max_turns=int(self.max_history_turns),
            max_chars=int(self.max_history_chars),
            exclude_last_user=True,
        )

        system = (
            "You are AutoSkill's retrieval query rewriter. Your goal is to transform user input into a keyword-rich search query that targets reusable 'Skills' (workflows, templates, SOPs).\n"
            "\n"
            "### CORE STRATEGY: Abstraction & Intent\n"
            "- **Identify the 'Task Pattern':** Do not just summarize the content. Identify the *operation* (e.g., Refactor, Summarize, Audit) and the *domain* (e.g., Python, Legal Contract, UI Design).\n"
            "- **Ignore Specific Entities:** If the user asks to 'fix the bug in function calc_tax()', rewrite it as 'debug python function logic error'. Skills are generic; queries should be too.\n"
            "- **Handle Pasted Content:** Never include long pasted text. Replace it with descriptors like '<Python Code>', '<Meeting Transcript>', or '<JSON Data>'.\n"
            "- **Context Resolution:** Resolve pronouns ('it', 'that', 'the previous draft') using conversation history to make the query standalone.\n"
            "\n"
            "### LANGUAGE RULES\n"
            "- **Strict Consistency:** The query MUST be in the same language as the user's *instruction* (the verbs/intent), even if the referenced content is in another language.\n"
            "- **Example:** User says '帮我优化这段 Python 代码' (Chinese instruction, English content) -> Query must be in **Chinese** (e.g., '优化 Python 代码结构 重构建议').\n"
            "\n"
            "### KEYWORD ENHANCEMENT (For Skill Matching)\n"
            "- If the user wants a structure, append keywords like 'template' or 'format'.\n"
            "- If the user wants a check/review, append keywords like 'checklist', 'rubric', or 'validation'.\n"
            "- If the user wants to solve a problem, append 'workflow' or 'guide'.\n"
            "\n"
            "### OUTPUT FORMAT\n"
            "- Output ONLY the rewritten query text (one line). No quotes, no preamble.\n"
            "\n"
            "### EXAMPLES\n"
            "- Input: \"Make this sound more professional: <PASTED_EMAIL>\" -> \"email professional tone rewrite business communication polish\"\n"
            "- Input: \"帮我看看这个报错怎么修: <STACKTRACE>\" -> \"Python报错堆栈分析 故障排查流程 debug guide\"\n"
            "- Input: \"Generate a unit test for the function above\" -> \"generate unit test cases python test coverage template\"\n"
            "- Input: \"用那个格式整理这周的周报\" (referring to a previous 'Agile Format') -> \"Agile格式周报整理 敏捷开发汇报模板 summary template\""
        )
        if history:
            user = (
                f"Conversation context:\n{history}\n\n"
                f"Current user query:\n{q}\n\n"
                "Rewritten search query:"
            )
        else:
            user = f"Current user query:\n{q}\n\nRewritten search query:"

        try:
            out = self.llm.complete(system=system, user=user, temperature=0.0)
        except Exception:
            return q

        rewritten = _clean_rewritten_query(out)
        if not rewritten:
            return q

        rewritten = truncate_keep_head(
            rewritten,
            max_units=max(1, int(self.max_query_chars)),
            marker="",
        ).strip()
        return rewritten or q
