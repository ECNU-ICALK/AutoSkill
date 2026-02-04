"""
A “fault-tolerant” JSON parser for LLM outputs.

In practice, many models may:
- wrap JSON in Markdown fences (```json ... ```)
- add commentary/thoughts before or after the JSON
- output multiple JSON fragments

This module does best-effort extraction: it tries to find the JSON object/array that looks most like
`{\"skills\": ...}` and returns it.
"""

from __future__ import annotations

import json
import re
from typing import Any

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)
_SKILLS_START_RE = re.compile(r'\{\s*"skills"\s*:', re.IGNORECASE)


def json_from_llm_text(text: str) -> Any:
    """
    Best-effort JSON extraction for LLM outputs.
    - Strips Markdown code fences
    - Tries direct json.loads
    - Falls back to extracting the first JSON array/object substring
    """

    cleaned = _FENCE_RE.sub("", (text or "").strip())
    if not cleaned:
        raise ValueError("empty LLM output")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    window = cleaned[-20_000:] if len(cleaned) > 20_000 else cleaned
    offset = len(cleaned) - len(window)

    decoder = json.JSONDecoder()
    candidates = []

    for m in _SKILLS_START_RE.finditer(window):
        candidates.append(offset + m.start())

    for i, ch in enumerate(window):
        if ch in "[{":
            candidates.append(offset + i)

    seen = set()
    unique: list[int] = []
    for idx in candidates:
        if idx in seen:
            continue
        seen.add(idx)
        unique.append(idx)

    best_obj: Any = None
    best_score = -1

    for idx in reversed(unique):
        try:
            obj, _end = decoder.raw_decode(cleaned, idx)
        except json.JSONDecodeError:
            continue
        score = _score_json_candidate(obj)
        if score > best_score:
            best_score = score
            best_obj = obj
            if best_score >= 12:
                return best_obj

    if best_score >= 0:
        return best_obj
    raise ValueError("failed to parse JSON from LLM output")


def _score_json_candidate(obj: Any) -> int:
    if isinstance(obj, dict):
        skills = obj.get("skills")
        if isinstance(skills, list):
            score = 10 + min(len(skills), 10)
            if skills and isinstance(skills[0], dict):
                keys = set(skills[0].keys())
                want = {"name", "description", "prompt"}
                score += len(keys & want)
            return score
        return 3
    if isinstance(obj, list):
        return 5 + min(len(obj), 10)
    return 1
