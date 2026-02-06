"""
One-command importer: Agent Skill directories -> AutoSkill LocalSkillStore.

This script imports an existing set of Agent Skill artifacts (anthropics/skills style):
- each skill is a directory containing `SKILL.md` (and optional scripts/resources)

Import modes:
- scope=user: parse each `SKILL.md` and upsert into `Skills/Users/<user_id>/...` (maintainable user skills)
- scope=common: copy each skill directory into `Skills/Common/...` (shared library, treated read-only by the SDK)

Run:
  python3 -m examples.import_agent_skills --root-dir /path/to/skills --scope common --store-dir Skills
"""

from __future__ import annotations

import argparse
import os
import shutil
import uuid

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path
from autoskill.skill_management.formats.agent_skill import upsert_skill_md_id


def _iter_skill_dirs(root_dir: str, *, max_depth: int) -> list[str]:
    abs_root = os.path.abspath(os.path.expanduser(str(root_dir)))
    base_sep = abs_root.rstrip(os.sep) + os.sep
    out: list[str] = []
    for current, dirs, files in os.walk(abs_root):
        current_abs = os.path.abspath(current)
        rel = current_abs[len(base_sep) :] if current_abs.startswith(base_sep) else ""
        depth = 0 if not rel else rel.count(os.sep) + 1
        if depth > int(max_depth):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d and not d.startswith(".")]
        if "SKILL.md" in files:
            out.append(current_abs)
            dirs[:] = []
    return out


def _copy_skill_dir(src_dir: str, dst_dir: str, *, overwrite: bool, include_files: bool) -> bool:
    if os.path.exists(dst_dir):
        if not overwrite:
            return False
        shutil.rmtree(dst_dir)

    os.makedirs(dst_dir, exist_ok=True)
    if include_files:
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        return True

    src_md = os.path.join(src_dir, "SKILL.md")
    dst_md = os.path.join(dst_dir, "SKILL.md")
    shutil.copyfile(src_md, dst_md)
    return True


def _deterministic_import_id(*, scope: str, owner: str, rel_path: str) -> str:
    base = f"autoskill-skill-id-v1:{scope}:{owner}:{rel_path}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))


def _rewrite_skill_md_id(dir_path: str, *, skill_id: str) -> None:
    md_path = os.path.join(dir_path, "SKILL.md")
    if not os.path.isfile(md_path):
        return
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md = f.read()
        updated = upsert_skill_md_id(md, skill_id=str(skill_id))
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(updated)
    except Exception:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Agent Skill directories into AutoSkill")
    parser.add_argument(
        "--root-dir",
        required=True,
        help="Directory containing skill subfolders (each with SKILL.md).",
    )
    default_store_dir = (
        os.getenv("AUTOSKILL_STORE_DIR")
        or os.getenv("AUTOSKILL_STORE_PATH")
        or default_store_path()
    )
    parser.add_argument(
        "--store-dir",
        dest="store_dir",
        default=default_store_dir,
    )
    parser.add_argument(
        "--store-path",
        dest="store_dir",
        default=default_store_dir,
        help="Deprecated alias of --store-dir (directory-based store).",
    )
    parser.add_argument("--user-id", default=os.getenv("AUTOSKILL_USER_ID", "u1"))
    parser.add_argument(
        "--scope",
        default="common",
        choices=["common", "user"],
        help="Import scope: common (shared library) or user (user-maintained skills).",
    )
    parser.add_argument(
        "--library-name",
        default="",
        help="When scope=common, optionally group imports under Common/<library-name>/ (default: basename of --root-dir).",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing skills by id.")
    parser.add_argument("--no-files", action="store_true", help="Do not import extra files (only SKILL.md).")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
        help="Maximum directory depth to scan for SKILL.md.",
    )
    args = parser.parse_args()

    print("Store dir:", args.store_dir)
    print("Scope:", args.scope)

    if str(args.scope).lower() == "user":
        sdk = AutoSkill(
            AutoSkillConfig(
                llm={"provider": "mock"},
                embeddings={"provider": "hashing", "dims": 256},
                store={"provider": "local", "path": str(args.store_dir)},
            )
        )
        existing = sdk.list(user_id=str(args.user_id))
        print("Existing user skills:", len(existing))

        imported = sdk.import_agent_skill_dirs(
            root_dir=str(args.root_dir),
            user_id=str(args.user_id),
            overwrite=bool(args.overwrite),
            include_files=not bool(args.no_files),
            max_depth=int(args.max_depth),
        )
        print("Imported user skills:", len(imported))
        print("Total user skills:", len(sdk.list(user_id=str(args.user_id))))
        return

    common_root = os.path.join(str(args.store_dir), "Common")
    lib_name = str(args.library_name or "").strip()
    if not lib_name:
        lib_name = os.path.basename(os.path.abspath(os.path.expanduser(str(args.root_dir))).rstrip(os.sep)) or "library"
    dest_root = os.path.join(common_root, lib_name)
    os.makedirs(dest_root, exist_ok=True)
    print("Common library dir:", dest_root)

    abs_src_root = os.path.abspath(os.path.expanduser(str(args.root_dir)))
    skill_dirs = _iter_skill_dirs(abs_src_root, max_depth=int(args.max_depth))
    copied = 0
    for src_dir in skill_dirs:
        rel = os.path.relpath(src_dir, abs_src_root)
        if rel in {".", ""}:
            rel = os.path.basename(src_dir.rstrip(os.sep)) or "skill"
        rel = rel.lstrip("/").replace("..", "_")
        dst_dir = os.path.join(dest_root, rel.replace("/", os.sep))
        if _copy_skill_dir(
            src_dir,
            dst_dir,
            overwrite=bool(args.overwrite),
            include_files=not bool(args.no_files),
        ):
            new_id = _deterministic_import_id(scope="common", owner=lib_name, rel_path=rel.replace(os.sep, "/"))
            _rewrite_skill_md_id(dst_dir, skill_id=new_id)
            copied += 1
    print("Copied common skill directories:", copied)


if __name__ == "__main__":
    main()
