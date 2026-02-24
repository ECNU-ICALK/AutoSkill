"""
Skill artifact operations (export/write).

These helpers keep filesystem concerns out of the main SDK entrypoint while preserving the existing
behavior and formats.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .formats.agent_skill import build_agent_skill_files, render_skill_md, skill_dir_name
from ..models import Skill
from .stores.base import SkillStore


def export_skill_md(store: SkillStore, skill_id: str) -> Optional[str]:
    skill = store.get(skill_id)
    if not skill:
        return None
    return (skill.files or {}).get("SKILL.md") or render_skill_md(skill)


def export_skill_dir(store: SkillStore, skill_id: str) -> Optional[Dict[str, str]]:
    skill = store.get(skill_id)
    if not skill:
        return None
    files = dict(skill.files or {})
    if "SKILL.md" not in files:
        files.update(build_agent_skill_files(skill))
    return files


def write_skill_dir(store: SkillStore, skill_id: str, *, root_dir: str) -> Optional[str]:
    skill = store.get(skill_id)
    if not skill:
        return None
    dir_name = skill_dir_name(skill)
    files = export_skill_dir(store, skill_id) or {}

    import os

    skill_root = os.path.join(root_dir, dir_name)
    os.makedirs(skill_root, exist_ok=True)
    for rel_path, content in files.items():
        rel_path = str(rel_path).lstrip("/").replace("..", "_")
        abs_path = os.path.join(skill_root, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
    return skill_root


def write_skill_dirs(store: SkillStore, *, user_id: str, root_dir: str) -> List[str]:
    """
    Writes all active skills for a user as Agent Skill artifacts (one folder per skill).
    Directory names are derived from skill text fields and de-duplicated with numeric suffixes.
    """

    skills = store.list(user_id=user_id)
    written: List[str] = []
    used = set()
    for s in skills:
        base = skill_dir_name(s)
        dir_name = base
        if dir_name in used:
            i = 2
            while f"{base}-{i}" in used:
                i += 1
            dir_name = f"{base}-{i}"
        used.add(dir_name)

        files = export_skill_dir(store, s.id) or {}
        import os

        skill_root = os.path.join(root_dir, dir_name)
        os.makedirs(skill_root, exist_ok=True)
        for rel_path, content in files.items():
            rel_path = str(rel_path).lstrip("/").replace("..", "_")
            abs_path = os.path.join(skill_root, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
        written.append(skill_root)
    return written


def ensure_skill_files(skill: Skill) -> Dict[str, str]:
    files = dict(skill.files or {})
    if "SKILL.md" not in files or not str(files.get("SKILL.md") or "").strip():
        files.update(build_agent_skill_files(skill))
    return files
