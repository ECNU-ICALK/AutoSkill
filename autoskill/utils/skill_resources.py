"""
Helpers for extracting resource file hints from Skill artifacts.

Resource paths can come from two places:
1) explicit `Skill.files` keys (when full files are loaded in memory)
2) the `## Files` section inside `SKILL.md` (when only SKILL.md is loaded)
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from ..models import Skill


_BACKTICK_BULLET_RE = re.compile(r"^\s*-\s*`([^`]+)`\s*$")
_PLAIN_BULLET_RE = re.compile(r"^\s*-\s+(.+?)\s*$")


def normalize_resource_rel_path(path: str) -> str:
    """Normalizes a relative artifact path into a safe repository-local form."""

    rel = str(path or "").strip().replace("\\", "/").lstrip("/")
    if not rel:
        return ""
    parts: List[str] = []
    for p in rel.split("/"):
        s = str(p).strip()
        if not s or s in {".", ".."}:
            continue
        if s.startswith(".."):
            s = s.replace("..", "_")
        parts.append(s)
    if not parts:
        return ""
    out = "/".join(parts)
    if out.lower() == "skill.md":
        return ""
    return out


def extract_resource_paths_from_files(
    files: Optional[Dict[str, str]], *, max_items: int = 200
) -> List[str]:
    """Collects unique non-SKILL.md resource paths from a files mapping."""

    out: List[str] = []
    seen = set()
    for key in list((files or {}).keys()):
        rel = normalize_resource_rel_path(str(key or ""))
        if not rel:
            continue
        low = rel.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(rel)
        if len(out) >= max(1, int(max_items)):
            break
    return out


def extract_resource_paths_from_skill_md(skill_md: str, *, max_items: int = 200) -> List[str]:
    """Parses resource paths from the `## Files` markdown section."""

    text = str(skill_md or "")
    if not text:
        return []
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "## files":
            start = i + 1
            break
    if start is None:
        return []

    out: List[str] = []
    seen = set()
    for ln in lines[start:]:
        stripped = ln.strip()
        if stripped.startswith("#"):
            break
        if not stripped:
            continue
        m = _BACKTICK_BULLET_RE.match(ln)
        if m:
            rel = normalize_resource_rel_path(m.group(1))
        else:
            m2 = _PLAIN_BULLET_RE.match(ln)
            rel = normalize_resource_rel_path(m2.group(1) if m2 else "")
        if not rel:
            continue
        low = rel.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(rel)
        if len(out) >= max(1, int(max_items)):
            break
    return out


def extract_skill_resource_paths(skill: Skill, *, max_items: int = 200) -> List[str]:
    """Returns merged resource paths from `Skill.files` and SKILL.md `## Files` section."""

    files = dict(getattr(skill, "files", {}) or {})
    direct = extract_resource_paths_from_files(files, max_items=max_items)
    if len(direct) >= max(1, int(max_items)):
        return direct[: max(1, int(max_items))]

    md_paths = extract_resource_paths_from_skill_md(
        str(files.get("SKILL.md") or ""),
        max_items=max_items,
    )
    out = list(direct)
    seen = {p.lower() for p in out}
    for p in md_paths:
        low = p.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(p)
        if len(out) >= max(1, int(max_items)):
            break
    return out
