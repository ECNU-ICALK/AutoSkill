"""
Identity helpers for stable skill-level deduplication keys.

This module intentionally keeps the key compact and language-agnostic:
- normalize to NFKC + lowercase
- strip punctuation noise
- collapse whitespace
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

META_IDENTITY_DESC_NORM = "identity_desc_norm"
META_IDENTITY_DESC_HASH = "identity_desc_hash"

_WS_RE = re.compile(r"\s+", re.UNICODE)
_NOISE_RE = re.compile(r"[^\w\u4e00-\u9fff]+", re.UNICODE)


def normalize_identity_text(text: str) -> str:
    s = unicodedata.normalize("NFKC", str(text or ""))
    s = s.strip().lower()
    if not s:
        return ""
    s = _NOISE_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s[:1024]


def identity_desc_norm_from_fields(*, description: str, name: str) -> str:
    base = str(description or "").strip() or str(name or "").strip()
    return normalize_identity_text(base)


def identity_hash_from_norm(norm: str) -> str:
    key = str(norm or "").strip()
    if not key:
        return ""
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]
