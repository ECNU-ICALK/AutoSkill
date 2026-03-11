"""
Shared LLM helpers for the offline document pipeline.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional

from autoskill.llm.base import LLM
from autoskill.utils.json import json_from_llm_text


def llm_complete_json(
    *,
    llm: LLM,
    system: str,
    payload: Any,
    repair_system: str = "",
    repair_payload: Any = None,
) -> Any:
    """Calls an LLM, parses JSON, and optionally runs one repair pass."""

    user = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    text = llm.complete(system=system, user=user, temperature=0.0)
    try:
        return json_from_llm_text(text)
    except Exception:
        if not str(repair_system or "").strip():
            raise
        repair_user = repair_payload if repair_payload is not None else payload
        if isinstance(repair_user, str):
            repair_user_s = repair_user.replace("__DRAFT__", str(text or "").strip()[-6000:])
        else:
            repair_user_s = json.dumps(repair_user, ensure_ascii=False)
        repaired = llm.complete(system=repair_system, user=repair_user_s, temperature=0.0)
        return json_from_llm_text(repaired)


def coerce_str_list(raw: Any) -> List[str]:
    """Normalizes list-like content into stripped strings."""

    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        out: List[str] = []
        for item in raw:
            value = str(item or "").strip()
            if value:
                out.append(value)
        return out
    value = str(raw or "").strip()
    return [value] if value else []


def clip_confidence(value: Any, *, default: float = 0.6) -> float:
    """Coerces a numeric confidence into [0.0, 1.0]."""

    try:
        numeric = float(value)
    except Exception:
        numeric = float(default)
    if numeric < 0.0:
        return 0.0
    if numeric > 1.0:
        return 1.0
    return numeric


def compact_text_list(items: Iterable[Any], *, limit: int = 8) -> List[str]:
    """Keeps a short deduplicated text list while preserving first-seen order."""

    out: List[str] = []
    seen = set()
    for item in items:
        value = str(item or "").strip()
        if not value:
            continue
        key = " ".join(value.split()).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
        if len(out) >= max(1, int(limit or 1)):
            break
    return out


def section_items_from_prompt(prompt: str, heading_hints: Iterable[str]) -> List[str]:
    """
    Best-effort fallback parser for markdown bullet/numbered sections.

    This is only used when the model omitted explicit structured fields.
    """

    text = str(prompt or "")
    if not text.strip():
        return []

    heading_keys = [str(item or "").strip().lower() for item in heading_hints if str(item or "").strip()]
    if not heading_keys:
        return []

    current_matches = False
    out: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            heading = line.lstrip("#").strip().lower()
            current_matches = any(key in heading for key in heading_keys)
            continue
        if not current_matches:
            continue
        cleaned = line
        if cleaned[:2] in {"- ", "* "}:
            cleaned = cleaned[2:].strip()
        else:
            dot = cleaned.find(". ")
            if dot > 0 and cleaned[:dot].isdigit():
                cleaned = cleaned[dot + 2 :].strip()
        if cleaned:
            out.append(cleaned)
    return compact_text_list(out, limit=12)


def maybe_json_dict(obj: Any) -> Dict[str, Any]:
    """Returns a dict-like payload or an empty dict."""

    return dict(obj) if isinstance(obj, dict) else {}
