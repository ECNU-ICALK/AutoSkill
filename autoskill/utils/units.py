"""
Mixed-language text sizing utilities.

AutoSkill uses several "max_*_chars" settings to bound prompt sizes and avoid provider request limits.
In practice, counting raw Python string characters can be misleading across languages.

This module defines a lightweight, provider-agnostic size metric:
- Chinese/CJK ideographs are counted by character (1 ideograph == 1 unit).
- English/ASCII text is counted by word (1 ASCII word == 1 unit).

Punctuation and whitespace do not consume units.
"""

from __future__ import annotations

from typing import Optional, Tuple

_CJK_RANGES: Tuple[Tuple[int, int], ...] = (
    (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
    (0x2A700, 0x2B73F),  # Extension C
    (0x2B740, 0x2B81F),  # Extension D
    (0x2B820, 0x2CEAF),  # Extension E
    (0x2CEB0, 0x2EBEF),  # Extension F
    (0x30000, 0x3134F),  # Extension G
)


def _is_cjk_ideograph(ch: str) -> bool:
    if not ch:
        return False
    code = ord(ch)
    for start, end in _CJK_RANGES:
        if start <= code <= end:
            return True
    return False


def _is_ascii_alnum(ch: str) -> bool:
    return bool(ch) and ch.isascii() and ch.isalnum()


def _is_ascii_word_char(ch: str) -> bool:
    if not ch or not ch.isascii():
        return False
    if ch.isalnum():
        return True
    return ch in {"'", "-", "_"}


def text_units(text: str) -> int:
    """
    Returns the number of "units" in text.

    Units definition:
    - each CJK ideograph counts as 1 unit
    - each ASCII word counts as 1 unit (a contiguous run starting with [A-Za-z0-9])
    """

    s = str(text or "")
    if not s:
        return 0

    units = 0
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if _is_cjk_ideograph(ch):
            units += 1
            i += 1
            continue

        if _is_ascii_alnum(ch):
            units += 1
            i += 1
            while i < n and _is_ascii_word_char(s[i]):
                i += 1
            continue

        i += 1

    return units


def _clip_head_no_marker(text: str, *, max_units: int) -> str:
    s = str(text or "")
    limit = int(max_units or 0)
    if limit <= 0 or not s:
        return ""

    units = 0
    end = 0
    have_unit = False
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if _is_cjk_ideograph(ch):
            if units + 1 > limit:
                break
            units += 1
            have_unit = True
            i += 1
            end = i
            continue

        if _is_ascii_alnum(ch):
            if units + 1 > limit:
                break
            units += 1
            have_unit = True
            i += 1
            while i < n and _is_ascii_word_char(s[i]):
                i += 1
            end = i
            continue

        i += 1
        if have_unit:
            end = i

    return s[:end]


def _clip_tail_no_marker(text: str, *, max_units: int) -> str:
    s = str(text or "")
    limit = int(max_units or 0)
    if limit <= 0 or not s:
        return ""

    units = 0
    start = len(s)
    have_unit = False
    i = len(s)
    while i > 0:
        ch = s[i - 1]
        if _is_cjk_ideograph(ch):
            if units + 1 > limit:
                break
            units += 1
            have_unit = True
            i -= 1
            start = i
            continue

        if _is_ascii_alnum(ch):
            if units + 1 > limit:
                break
            units += 1
            have_unit = True
            j = i - 1
            while j > 0 and _is_ascii_word_char(s[j - 1]):
                j -= 1
            i = j
            start = i
            continue

        i -= 1
        if have_unit:
            start = i

    return s[start:]


def truncate_keep_head(
    text: str,
    *,
    max_units: int,
    marker: str = "\n...[truncated]...\n",
) -> str:
    s = str(text or "")
    limit = int(max_units or 0)
    if limit <= 0 or not s:
        return ""
    if text_units(s) <= limit:
        return s

    m = str(marker or "")
    m_units = text_units(m)
    if not m or limit <= m_units:
        return _clip_head_no_marker(s, max_units=limit)

    head = _clip_head_no_marker(s, max_units=limit - m_units)
    return head + m


def truncate_keep_tail(
    text: str,
    *,
    max_units: int,
    marker: str = "\n...[truncated]...\n",
) -> str:
    s = str(text or "")
    limit = int(max_units or 0)
    if limit <= 0 or not s:
        return ""
    if text_units(s) <= limit:
        return s

    m = str(marker or "")
    m_units = text_units(m)
    if not m or limit <= m_units:
        return _clip_tail_no_marker(s, max_units=limit)

    tail = _clip_tail_no_marker(s, max_units=limit - m_units)
    return m + tail


def truncate_keep_head_tail(
    text: str,
    *,
    max_units: int,
    head_ratio: float = 0.7,
    marker: str = "\n\n...[truncated]...\n\n",
) -> str:
    s = str(text or "")
    limit = int(max_units or 0)
    if limit <= 0 or not s:
        return ""
    if text_units(s) <= limit:
        return s

    m = str(marker or "")
    m_units = text_units(m)
    if not m or limit <= m_units:
        return _clip_head_no_marker(s, max_units=limit)

    avail = max(0, limit - m_units)
    # Split budget between head and tail in units.
    hr = float(head_ratio)
    if hr <= 0.0:
        head_units = 0
    elif hr >= 1.0:
        head_units = avail
    else:
        head_units = int(avail * hr)
    tail_units = max(0, avail - head_units)

    head = _clip_head_no_marker(s, max_units=head_units)
    tail = _clip_tail_no_marker(s, max_units=tail_units)
    return head + m + tail


def truncate_system_user(
    *,
    system: Optional[str],
    user: str,
    max_units: int,
) -> Tuple[Optional[str], str]:
    """
    Truncate (system, user) pair to fit in max_units.

    Strategy:
    - keep the head of system (most instructions live there)
    - keep the tail of user (recent content is often most relevant)
    """

    limit = int(max_units or 0)
    if limit <= 0:
        return (system if system is not None else None), ""

    sys = str(system or "")
    usr = str(user or "")

    sys_units = text_units(sys)
    if sys_units > limit:
        return truncate_keep_head(sys, max_units=limit), ""

    allowed_user = max(0, limit - sys_units)
    if allowed_user <= 0:
        usr2 = ""
    elif text_units(usr) > allowed_user:
        usr2 = truncate_keep_tail(usr, max_units=allowed_user)
    else:
        usr2 = usr

    return (sys if system is not None else None), usr2
