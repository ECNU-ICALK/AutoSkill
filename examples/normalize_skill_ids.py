"""
Normalize SKILL.md frontmatter IDs for a local Skills store.

Why:
- External Agent Skill libraries often omit `id:` in SKILL.md.
- AutoSkill can derive deterministic IDs at load time, but writing them into SKILL.md makes the
  artifact self-contained and avoids brittle ID inference later.

Run:
  python3 -m examples.normalize_skill_ids --store-dir Skills --scope common
  python3 -m examples.normalize_skill_ids --store-dir Skills --scope user --user-id u1
  python3 -m examples.normalize_skill_ids --store-dir Skills --scope all --dry-run
"""

from __future__ import annotations

import argparse
import os

from autoskill.config import default_store_path
from autoskill.management.formats.agent_skill import load_agent_skill_dir


def _iter_skill_dirs(root_dir: str, *, max_depth: int) -> list[tuple[str, str]]:
    """
    Returns [(abs_dir, rel_key)] where rel_key is the path from root_dir to abs_dir (POSIX style).
    """

    abs_root = os.path.abspath(os.path.expanduser(str(root_dir)))
    base_sep = abs_root.rstrip(os.sep) + os.sep
    out: list[tuple[str, str]] = []
    for current, dirs, files in os.walk(abs_root):
        current_abs = os.path.abspath(current)
        rel = current_abs[len(base_sep) :] if current_abs.startswith(base_sep) else ""
        depth = 0 if not rel else rel.count(os.sep) + 1
        if depth > int(max_depth):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d and not d.startswith(".")]
        if "SKILL.md" in files:
            rel_key = rel.replace(os.sep, "/") or os.path.basename(current_abs)
            out.append((current_abs, rel_key))
            dirs[:] = []
    return out


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _has_frontmatter_id(md: str) -> bool:
    lines = (md or "").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return False
    for ln in lines[1:end]:
        s = ln.strip()
        if not s:
            continue
        if s.lower().startswith("id:"):
            val = s.split(":", 1)[1].strip()
            if not val or val in {'""', "''", ">", ">-", "|", "|-"}:
                return False
            return True
    return False


def _normalize_dir(
    dir_path: str,
    *,
    user_id: str,
    deterministic_id_key: str,
    dry_run: bool,
    force: bool,
) -> bool:
    md_path = os.path.join(dir_path, "SKILL.md")
    if not os.path.isfile(md_path):
        return False
    raw = _read(md_path)
    if not force and _has_frontmatter_id(raw):
        return False

    skill = load_agent_skill_dir(
        dir_path,
        user_id=user_id,
        include_files=False,
        deterministic_id_key=deterministic_id_key,
        ignore_frontmatter_id=bool(force),
    )
    updated = (skill.files or {}).get("SKILL.md") or ""
    if not updated or updated == raw:
        return False
    if not dry_run:
        _write(md_path, updated)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize missing `id:` in SKILL.md files")
    default_store_dir = (
        os.getenv("AUTOSKILL_STORE_DIR")
        or os.getenv("AUTOSKILL_STORE_PATH")
        or default_store_path()
    )
    parser.add_argument("--store-dir", default=default_store_dir)
    parser.add_argument(
        "--scope",
        default="all",
        choices=["all", "common", "user"],
        help="Which part of the store to normalize.",
    )
    parser.add_argument("--user-id", default="")
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Overwrite existing ids (reassign).")
    args = parser.parse_args()

    store_dir = os.path.abspath(os.path.expanduser(str(args.store_dir)))
    common_root = os.path.join(store_dir, "Common")
    users_root = os.path.join(store_dir, "Users")

    changed = 0
    scanned = 0

    if args.scope in {"all", "common"} and os.path.isdir(common_root):
        for name in sorted(os.listdir(common_root)):
            if not name or name.startswith("."):
                continue
            entry_root = os.path.join(common_root, name)
            if not os.path.isdir(entry_root):
                continue
            if os.path.isfile(os.path.join(entry_root, "SKILL.md")):
                scanned += 1
                if _normalize_dir(
                    entry_root,
                    user_id="library:Common",
                    deterministic_id_key=name,
                    dry_run=bool(args.dry_run),
                    force=bool(args.force),
                ):
                    changed += 1
                continue

            # Grouped library: Common/<library>/**/SKILL.md
            lib_name = name
            for dir_path, rel_key in _iter_skill_dirs(entry_root, max_depth=int(args.max_depth)):
                scanned += 1
                if _normalize_dir(
                    dir_path,
                    user_id=f"library:{lib_name}",
                    deterministic_id_key=f"{lib_name}/{rel_key}",
                    dry_run=bool(args.dry_run),
                    force=bool(args.force),
                ):
                    changed += 1

    if args.scope in {"all", "user"} and os.path.isdir(users_root):
        target_uid = str(args.user_id or "").strip()
        for uid in sorted(os.listdir(users_root)):
            if not uid or uid.startswith("."):
                continue
            if target_uid and uid != target_uid:
                continue
            user_root = os.path.join(users_root, uid)
            if not os.path.isdir(user_root):
                continue
            for dir_path, rel_key in _iter_skill_dirs(user_root, max_depth=int(args.max_depth)):
                scanned += 1
                if _normalize_dir(
                    dir_path,
                    user_id=uid,
                    deterministic_id_key=rel_key,
                    dry_run=bool(args.dry_run),
                    force=bool(args.force),
                ):
                    changed += 1

    mode = "DRY RUN" if args.dry_run else "WRITE"
    print("Mode:", mode)
    print("Store dir:", store_dir)
    print("Scanned skills:", scanned)
    print("Updated SKILL.md:", changed)


if __name__ == "__main__":
    main()
