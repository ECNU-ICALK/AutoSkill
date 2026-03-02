"""
Offline-only prompt replacement runtime.

This module patches LLM system prompts at runtime for offline channels without
modifying core autoskill extraction/maintenance logic.
"""

from __future__ import annotations

import json
import re
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Tuple

from autoskill.llm.base import LLM
from .prompts import maybe_offline_prompt


_REPAIR_MAX_RE = re.compile(r"return at most\s+(\d+)\s+skills", re.IGNORECASE)


def _safe_int(v: Any, default: int) -> int:
    """Run safe int."""
    try:
        return int(v)
    except Exception:
        return int(default)


def _extract_max_candidates(system: str, user: str) -> int:
    """Run extract max candidates."""
    m = _REPAIR_MAX_RE.search(str(system or ""))
    if m:
        return max(1, _safe_int(m.group(1), 1))
    try:
        obj = json.loads(str(user or ""))
        if isinstance(obj, dict):
            return max(1, _safe_int(obj.get("max_candidates"), 1))
    except Exception:
        pass
    if "DATA:" in str(user or ""):
        chunk = str(user or "")
        i = chunk.find("DATA:")
        if i >= 0:
            j = chunk.find("\n\nDRAFT:")
            data_text = chunk[i + len("DATA:") : j if j > i else None].strip()
            try:
                obj = json.loads(data_text)
                if isinstance(obj, dict):
                    return max(1, _safe_int(obj.get("max_candidates"), 1))
            except Exception:
                pass
    return 1


def _detect_prompt_kind(system: str) -> str:
    """Run detect prompt kind."""
    s = str(system or "").strip()
    if not s:
        return ""
    if "You are AutoSkill's Skill Extractor." in s:
        return "extract"
    if (
        "You are a JSON output fixer." in s
        and 'output ONLY strict JSON: {"skills": [...]}' in s
    ):
        return "repair"
    if "You are AutoSkill's Skill Set Manager." in s:
        return "manage_decide"
    if "You are AutoSkill's capability identity judge." in s:
        return "merge_gate"
    if "You are AutoSkill's Skill Merger." in s:
        return "merge"
    return ""


class OfflinePromptSwitchLLM(LLM):
    """
    LLM wrapper that swaps system prompts for offline channels only.
    """

    def __init__(self, base: LLM, *, channel: str) -> None:
        """Run init."""
        self._base = base
        self._channel = str(channel or "").strip().lower()

    def _rewrite_system(self, *, system: Optional[str], user: str) -> Optional[str]:
        """Run rewrite system."""
        src = str(system or "")
        kind = _detect_prompt_kind(src)
        if not kind:
            return system
        max_candidates = _extract_max_candidates(src, user)
        if kind in {"extract", "repair"}:
            repl = maybe_offline_prompt(
                channel=self._channel,
                kind=kind,
                max_candidates=max_candidates,
            )
        else:
            repl = maybe_offline_prompt(channel=self._channel, kind=kind)
        if repl and str(repl).strip():
            return str(repl)
        return system

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        """Run complete."""
        system2 = self._rewrite_system(system=system, user=user)
        return self._base.complete(system=system2, user=user, temperature=temperature)

    def stream_complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> Iterator[str]:
        """Run stream complete."""
        system2 = self._rewrite_system(system=system, user=user)
        return self._base.stream_complete(system=system2, user=user, temperature=temperature)


def _patch_attr(
    target: Any,
    *,
    attr: str,
    channel: str,
    changed: List[Tuple[Any, str, Any]],
) -> None:
    """Run patch attr."""
    if target is None or not hasattr(target, attr):
        return
    cur = getattr(target, attr)
    if cur is None:
        return
    if isinstance(cur, OfflinePromptSwitchLLM):
        return
    wrapped = OfflinePromptSwitchLLM(cur, channel=channel)
    setattr(target, attr, wrapped)
    changed.append((target, attr, cur))


@contextmanager
def activate_offline_prompt_runtime(*, sdk: Any, channel: str):
    """
    Temporarily wraps extractor/maintainer LLMs to replace prompts for offline jobs.
    """

    changed: List[Tuple[Any, str, Any]] = []
    try:
        _patch_attr(getattr(sdk, "extractor", None), attr="_llm", channel=channel, changed=changed)
        _patch_attr(getattr(sdk, "maintainer", None), attr="_llm", channel=channel, changed=changed)
        yield
    finally:
        for obj, attr, old in reversed(changed):
            try:
                setattr(obj, attr, old)
            except Exception:
                pass
