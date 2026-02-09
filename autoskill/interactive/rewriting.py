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
    """Builds bounded history text for query rewriting prompts."""

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
    """Normalizes raw LLM output into a single-line retrieval query."""

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
        """
        Rewrites current query into a retrieval-oriented query string.

        On any provider/parsing failure, returns the original query.
        """

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
            "You are AutoSkill's retrieval query rewriter.\n"
            "Task: rewrite the current user query into ONE concise search query for skill retrieval.\n"
            "\n"
            "### DECIDE CONVERSATION STATE FIRST (internally)\n"
            "- State A (continuation/refinement): current turn updates the same task.\n"
            "- State B (topic switch): current turn starts a different task.\n"
            "- If unsure, default to State A and keep the current task anchor.\n"
            "\n"
            "### PRIMARY OBJECTIVE: topic-anchored, constraint-aware rewrite\n"
            "- Build a standalone query that preserves task identity.\n"
            "- In State A, keep the existing task/topic anchor from recent history and add new constraints.\n"
            "- In State B, replace the anchor with the new task/topic.\n"
            "- If current turn is mostly constraints (format/style/quality) and lacks a task noun, inherit the anchor from history.\n"
            "- Resolve references like 'it/that/this/the above' using recent history.\n"
            "\n"
            "### TOPIC ANCHOR SPEC (CRITICAL)\n"
            "- The rewritten query must include an explicit topic anchor noun phrase, not only formatting/process words.\n"
            "- Topic anchor should describe the current work item using: <domain/object> + <deliverable form> + <operation intent>.\n"
            "- If conversation is continuing, preserve the same topic anchor core and append only new constraints.\n"
            "- If current turn is constraint-only, prepend the inherited topic anchor before constraints.\n"
            "- Do not collapse topic anchor into generic labels like 'document', 'content', 'workflow', or 'formatting'.\n"
            "\n"
            "### WHAT TO KEEP\n"
            "- Keep: core task/topic + operation + durable constraints from current and relevant recent turns.\n"
            "- Keep constraints that change skill choice: output format, banned structures, depth/detail level, tone, audience, quality requirements.\n"
            "- Keep domain signals only when they help retrieval.\n"
            "\n"
            "### WHAT TO AVOID\n"
            "- Do NOT replace the topic with generic process words.\n"
            "- Do NOT output a query made only of format/style words without a topic anchor.\n"
            "- Do NOT output vague retrieval jargon like 'workflow/template/guide/checklist/rubric/format conversion' unless user intent explicitly requires them.\n"
            "- Do NOT include long pasted content; summarize as a short descriptor.\n"
            "- Do NOT include one-off entities (names/org IDs/URLs/exact dates) unless essential to task identity.\n"
            "- Do NOT overfit to the latest sentence and drop the ongoing task anchor in State A.\n"
            "\n"
            "### LANGUAGE RULE\n"
            "- Use the same language as the user's instruction intent.\n"
            "\n"
            "### QUALITY BAR\n"
            "- One line only, concise but specific.\n"
            "- Prefer pattern: <topic anchor (domain/object + deliverable)> + <operation> + <key constraints>.\n"
            "- Keep only the most retrieval-relevant constraints (about 2-6 items), deduplicated.\n"
            "- Avoid over-abstracting into tooling/process terms.\n"
            "\n"
            "### EXAMPLES\n"
            "- History: 'Write a government report on LLM self-evolution' + follow-up constraints.\n"
            "  Current: 'Do not use tables, use Word format.'\n"
            "  Output: '政府报告 大模型自进化 不使用表格 Word格式'\n"
            "- Current starts new topic: 'Now draft a公众号推文版本'.\n"
            "  Output: '公众号文章撰写 观点表达 结构清晰'\n"
            "\n"
            "Output ONLY the rewritten query text (one line). No quotes, no preamble."
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
