"""
Input redaction.

Goal: encourage the LLM to extract “general skills” rather than embedding sensitive details into prompts.
"""

from __future__ import annotations

import re
from typing import Any

_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE)
_URL_RE = re.compile(r"\bhttps?://[^\s)>\"]+\b", re.IGNORECASE)
_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_-]{24,}(?![A-Za-z0-9])")
_LONG_NUM_RE = re.compile(r"\b\d{4,}\b")


def redact_obj(obj: Any) -> Any:
    """
    Best-effort redaction for LLM-bound inputs to encourage general skills.

    - Replaces emails/URLs/likely tokens/long numbers with placeholders.
    - Recursively processes dict/list structures.
    """

    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    return obj


def redact_text(text: str) -> str:
    """Run redact text."""
    s = text or ""
    s = _EMAIL_RE.sub("<EMAIL>", s)
    s = _URL_RE.sub("<URL>", s)
    s = _TOKEN_RE.sub("<TOKEN>", s)
    s = _LONG_NUM_RE.sub("<NUM>", s)
    return s
