"""
Extraction timing signals for interactive chat.

This module intentionally contains only lightweight heuristics used to decide WHEN to attempt skill
extraction (e.g., at topic boundaries or checkpoints). The extractor itself decides whether a Skill
should be produced by returning an empty list when there is not enough reusable signal.
"""

from __future__ import annotations

import re
from ..utils.text import keywords

_ACK_PREFIXES = (
    "thanks",
    "thank you",
    "thx",
    "ty",
    "ok",
    "okay",
    "got it",
    "understood",
    "sounds good",
    "great",
    "cool",
    "nice",
    "perfect",
)

_REVISION_HINTS = (
    "rewrite",
    "rephrase",
    "revise",
    "edit",
    "modify",
    "change",
    "make it",
    "shorter",
    "longer",
    "simpler",
    "more formal",
    "more casual",
    "more concise",
    "improve",
    "polish",
)

_ASCII_WORD_RE = re.compile(r"[a-z0-9]+")


def _ascii_words(text_lower: str) -> set[str]:
    """Run ascii words."""
    return {m.group(0) for m in _ASCII_WORD_RE.finditer(text_lower or "")}


def _looks_like_ack(text: str) -> bool:
    """Run looks like ack."""
    s = (text or "").strip().lower()
    if not s:
        return False
    if len(s) <= 40 and any(s.startswith(p) for p in _ACK_PREFIXES):
        return True
    return False


def heuristic_is_ack_feedback(text: str) -> bool:
    """
    Returns True when the user's message looks like a short acknowledgement/closure.

    This is used as a weak topic-boundary signal for extraction timing.
    """

    return _looks_like_ack(text)


def heuristic_topic_changed(latest_user: str, latest_assistant: str, user_feedback: str) -> bool:
    """
    Best-effort topic change detector.

    Returns True when the user feedback likely starts a new (unrelated) topic rather than continuing the
    previous topic. This is intentionally conservative and should be treated as a weak signal.
    """

    fb = (user_feedback or "").strip()
    if not fb:
        return False

    if _looks_like_ack(fb):
        return False

    fb_low = fb.lower()
    fb_words = _ascii_words(fb_low)
    if any(h in fb_low for h in _REVISION_HINTS) and (fb_words & {"it", "this", "that", "above"}):
        return False

    prev_text = f"{(latest_user or '').strip()}\n{(latest_assistant or '').strip()}".strip()
    prev_kws = set(keywords(prev_text, limit=10))
    fb_kws = set(keywords(fb, limit=10))
    if not prev_kws or not fb_kws:
        return False

    overlap = len(prev_kws & fb_kws) / float(max(1, min(len(prev_kws), len(fb_kws))))
    if overlap >= 0.25:
        return False

    if any(h in fb_low for h in ("by the way", "new topic", "another question", "separate question", "unrelated")):
        return True

    has_followup_ref = bool(fb_words & {"it", "this", "that", "above", "previous", "earlier", "regarding"})
    has_followup_ref = has_followup_ref or any(p in fb_low for p in ("the above", "about that"))
    if overlap <= 0.10 and len(fb) >= 40 and not has_followup_ref:
        return True

    return False
