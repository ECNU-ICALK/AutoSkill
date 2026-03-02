"""
Shared skill version snapshot helpers.

This module centralizes snapshot/history operations used by both proxy APIs and web UI,
so version rollback behavior stays consistent across entry points.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..models import Skill, SkillExample

HISTORY_KEY = "_autoskill_version_history"
DEFAULT_HISTORY_LIMIT = 30


def examples_to_raw(examples: List[SkillExample]) -> List[Dict[str, Any]]:
    """Run examples to raw."""
    out: List[Dict[str, Any]] = []
    for ex in examples or []:
        out.append(
            {
                "input": str(getattr(ex, "input", "") or ""),
                "output": (str(getattr(ex, "output", "")) if getattr(ex, "output", None) is not None else None),
                "notes": (str(getattr(ex, "notes", "")) if getattr(ex, "notes", None) is not None else None),
            }
        )
    return out


def examples_from_raw(raw: Any) -> List[SkillExample]:
    """Run examples from raw."""
    out: List[SkillExample] = []
    if not isinstance(raw, list):
        return out
    for item in raw[:50]:
        if not isinstance(item, dict):
            continue
        inp = str(item.get("input") or "").strip()
        if not inp:
            continue
        out.append(
            SkillExample(
                input=inp,
                output=(str(item.get("output")).strip() if item.get("output") else None),
                notes=(str(item.get("notes")).strip() if item.get("notes") else None),
            )
        )
    return out


def metadata_without_history(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run metadata without history."""
    md = dict(metadata or {})
    md.pop(HISTORY_KEY, None)
    return md


def make_skill_snapshot(skill: Skill) -> Dict[str, Any]:
    """Run make skill snapshot."""
    files = dict(getattr(skill, "files", {}) or {})
    return {
        "version": str(getattr(skill, "version", "") or ""),
        "name": str(getattr(skill, "name", "") or ""),
        "description": str(getattr(skill, "description", "") or ""),
        "instructions": str(getattr(skill, "instructions", "") or ""),
        "tags": [str(t).strip() for t in (getattr(skill, "tags", []) or []) if str(t).strip()],
        "triggers": [str(t).strip() for t in (getattr(skill, "triggers", []) or []) if str(t).strip()],
        "examples": examples_to_raw(list(getattr(skill, "examples", []) or [])),
        "skill_md": str(files.get("SKILL.md") or ""),
        "metadata": metadata_without_history(dict(getattr(skill, "metadata", {}) or {})),
        "source": dict(getattr(skill, "source", {}) or {}) if getattr(skill, "source", None) else None,
        "updated_at": str(getattr(skill, "updated_at", "") or ""),
    }


def history_from_metadata(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run history from metadata."""
    hist = metadata.get(HISTORY_KEY)
    if not isinstance(hist, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in hist:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def push_skill_snapshot(skill: Skill, *, limit: int = DEFAULT_HISTORY_LIMIT) -> int:
    """Run push skill snapshot."""
    metadata = dict(getattr(skill, "metadata", {}) or {})
    history = history_from_metadata(metadata)
    history.append(make_skill_snapshot(skill))
    if len(history) > int(limit):
        history = history[-int(limit) :]
    metadata[HISTORY_KEY] = history
    skill.metadata = metadata
    return len(history)


def pop_skill_snapshot(skill: Skill) -> Optional[Dict[str, Any]]:
    """Run pop skill snapshot."""
    metadata = dict(getattr(skill, "metadata", {}) or {})
    history = history_from_metadata(metadata)
    if not history:
        return None
    snapshot = dict(history[-1])
    history = history[:-1]
    metadata[HISTORY_KEY] = history
    skill.metadata = metadata
    return snapshot


def apply_snapshot(skill: Skill, snapshot: Dict[str, Any]) -> None:
    """Run apply snapshot."""
    skill.version = str(snapshot.get("version") or str(getattr(skill, "version", "0.1.0")))
    skill.name = str(snapshot.get("name") or str(getattr(skill, "name", "")))
    skill.description = str(snapshot.get("description") or str(getattr(skill, "description", "")))
    skill.instructions = str(snapshot.get("instructions") or str(getattr(skill, "instructions", "")))

    tags = snapshot.get("tags")
    if isinstance(tags, list):
        skill.tags = [str(t).strip() for t in tags if str(t).strip()]

    triggers = snapshot.get("triggers")
    if isinstance(triggers, list):
        skill.triggers = [str(t).strip() for t in triggers if str(t).strip()]

    examples = snapshot.get("examples")
    if isinstance(examples, list):
        skill.examples = examples_from_raw(examples)

    files = dict(getattr(skill, "files", {}) or {})
    skill_md = snapshot.get("skill_md")
    if skill_md is not None:
        files["SKILL.md"] = str(skill_md)
    skill.files = files

    md_saved = snapshot.get("metadata")
    if isinstance(md_saved, dict):
        current_history = history_from_metadata(dict(getattr(skill, "metadata", {}) or {}))
        new_md = dict(md_saved)
        new_md[HISTORY_KEY] = current_history
        skill.metadata = new_md

    src = snapshot.get("source")
    if src is not None:
        skill.source = dict(src) if isinstance(src, dict) else None
