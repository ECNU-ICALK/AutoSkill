"""
Import existing Agent Skill directory artifacts (anthropics/skills style) into a SkillStore.
"""

from __future__ import annotations

import os
from typing import List

from .formats.agent_skill import load_agent_skill_dir, upsert_skill_md_id
from ..models import Skill
from .stores.base import SkillStore
from ..utils.time import now_iso


def import_agent_skill_dirs(
    *,
    store: SkillStore,
    root_dir: str,
    user_id: str,
    overwrite: bool = True,
    include_files: bool = True,
    max_file_bytes: int = 1_000_000,
    max_depth: int = 6,
    reassign_ids: bool = True,
) -> List[Skill]:
    """
    Imports existing Agent Skill directory artifacts (anthropics/skills style) into a store.

    Expected layout:
    - root_dir/**/SKILL.md (recursively scanned)
    """

    abs_root = os.path.abspath(os.path.expanduser(str(root_dir)))
    if not os.path.isdir(abs_root):
        raise ValueError(f"root_dir is not a directory: {root_dir}")

    def iter_skill_dirs(base: str):
        base_sep = base.rstrip(os.sep) + os.sep
        for current, dirs, files in os.walk(base):
            current_abs = os.path.abspath(current)
            rel = current_abs[len(base_sep) :] if current_abs.startswith(base_sep) else ""
            depth = 0 if not rel else rel.count(os.sep) + 1
            if depth > int(max_depth):
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d and not d.startswith(".")]
            if "SKILL.md" in files:
                yield current_abs
                dirs[:] = []

    imported: List[Skill] = []
    for abs_dir in iter_skill_dirs(abs_root):
        skill = load_agent_skill_dir(
            abs_dir,
            user_id=user_id,
            include_files=include_files,
            max_file_bytes=max_file_bytes,
            deterministic_id_key=os.path.relpath(abs_dir, abs_root).replace(os.sep, "/"),
            ignore_frontmatter_id=bool(reassign_ids),
        )
        if reassign_ids:
            skill.files["SKILL.md"] = upsert_skill_md_id(
                (skill.files or {}).get("SKILL.md") or "", skill_id=skill.id
            )

        existing = store.get(skill.id)
        if existing is not None and not overwrite:
            continue

        if existing is not None and existing.created_at:
            skill.created_at = existing.created_at
        if not skill.created_at:
            skill.created_at = now_iso()
        skill.updated_at = now_iso()

        store.upsert(skill)
        imported.append(skill)

    return imported
