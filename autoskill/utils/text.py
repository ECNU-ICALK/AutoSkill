"""
Lightweight text utilities: keyword extraction.

Mainly used to generate tags for heuristic extraction and provide a searchable default set when tags are missing.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import List

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[^\W\d_]+")
_STOPWORDS = {
    "the",
    "and",
    "or",
    "to",
    "a",
    "an",
    "of",
    "in",
    "on",
    "for",
    "with",
    "is",
    "are",
    "i",
    "you",
    "we",
    "user",
    "assistant",
    "system",
}


def keywords(text: str, *, limit: int = 3) -> List[str]:
    tokens = [t.lower() for t in _TOKEN_RE.findall(text or "") if t.strip()]
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
    if not tokens:
        return []
    counts = Counter(tokens)
    return [t for t, _ in counts.most_common(limit)]
