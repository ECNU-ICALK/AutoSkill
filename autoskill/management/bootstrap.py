"""
Service-start offline maintenance for local skill stores.

This module integrates two previously standalone operations:
1) normalize missing SKILL.md frontmatter ids
2) import external Agent Skill directories into Common library
"""

from __future__ import annotations

import os
import shutil
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .formats.agent_skill import load_agent_skill_dir, upsert_skill_md_id


def _iter_skill_dirs(root_dir: str, *, max_depth: int) -> List[Tuple[str, str]]:
    """Run iter skill dirs."""
    abs_root = os.path.abspath(os.path.expanduser(str(root_dir)))
    base_sep = abs_root.rstrip(os.sep) + os.sep
    out: List[Tuple[str, str]] = []
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
    """Run read."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write(path: str, content: str) -> None:
    """Run write."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _has_frontmatter_id(md: str) -> bool:
    """Run has frontmatter id."""
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


def _deterministic_import_id(*, scope: str, owner: str, rel_path: str) -> str:
    """Run deterministic import id."""
    base = f"autoskill-skill-id-v1:{scope}:{owner}:{rel_path}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))


def _rewrite_skill_md_id(
    *,
    dir_path: str,
    user_id: str,
    deterministic_id_key: str,
    force: bool,
) -> bool:
    """Run rewrite skill md id."""
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
    _write(md_path, updated)
    return True


def normalize_store_skill_ids(
    *,
    store_root: str,
    max_depth: int = 6,
    force: bool = False,
) -> Dict[str, int]:
    """
    Normalizes missing frontmatter ids under:
    - <store_root>/Common
    - <store_root>/Users/<user_id>
    """

    root = os.path.abspath(os.path.expanduser(str(store_root)))
    common_root = os.path.join(root, "Common")
    users_root = os.path.join(root, "Users")

    scanned = 0
    changed = 0

    if os.path.isdir(common_root):
        for name in sorted(os.listdir(common_root)):
            if not name or name.startswith("."):
                continue
            entry_root = os.path.join(common_root, name)
            if not os.path.isdir(entry_root):
                continue

            # Common/<skill>/SKILL.md
            if os.path.isfile(os.path.join(entry_root, "SKILL.md")):
                scanned += 1
                if _rewrite_skill_md_id(
                    dir_path=entry_root,
                    user_id="library:Common",
                    deterministic_id_key=name,
                    force=bool(force),
                ):
                    changed += 1
                continue

            # Common/<library>/**/SKILL.md
            lib_name = name
            for dir_path, rel_key in _iter_skill_dirs(entry_root, max_depth=int(max_depth)):
                scanned += 1
                if _rewrite_skill_md_id(
                    dir_path=dir_path,
                    user_id=f"library:{lib_name}",
                    deterministic_id_key=f"{lib_name}/{rel_key}",
                    force=bool(force),
                ):
                    changed += 1

    if os.path.isdir(users_root):
        for uid in sorted(os.listdir(users_root)):
            if not uid or uid.startswith("."):
                continue
            user_root = os.path.join(users_root, uid)
            if not os.path.isdir(user_root):
                continue
            for dir_path, rel_key in _iter_skill_dirs(user_root, max_depth=int(max_depth)):
                scanned += 1
                if _rewrite_skill_md_id(
                    dir_path=dir_path,
                    user_id=uid,
                    deterministic_id_key=rel_key,
                    force=bool(force),
                ):
                    changed += 1

    return {"scanned": int(scanned), "changed": int(changed)}


def import_agent_skills_to_common(
    *,
    store_root: str,
    source_root: str,
    library_name: str = "",
    overwrite: bool = False,
    include_files: bool = True,
    max_depth: int = 6,
) -> Dict[str, Any]:
    """
    Imports skill directories from source_root into:
    - <store_root>/Common/<library_name>/<skill...>
    """

    src_root = os.path.abspath(os.path.expanduser(str(source_root)))
    if not os.path.isdir(src_root):
        return {
            "source_root": src_root,
            "library": "",
            "imported": 0,
            "skipped": 0,
            "errors": [f"source_root is not a directory: {source_root}"],
        }

    root = os.path.abspath(os.path.expanduser(str(store_root)))
    lib_name = str(library_name or "").strip() or os.path.basename(src_root.rstrip(os.sep)) or "Imported"
    common_lib_root = os.path.join(root, "Common", lib_name)
    os.makedirs(common_lib_root, exist_ok=True)

    imported = 0
    skipped = 0
    errors: List[str] = []

    for src_dir, rel_key in _iter_skill_dirs(src_root, max_depth=int(max_depth)):
        rel_dst = str(rel_key or "").strip().replace("/", os.sep)
        if not rel_dst:
            rel_dst = os.path.basename(src_dir.rstrip(os.sep))
        dst_dir = os.path.join(common_lib_root, rel_dst)

        try:
            if os.path.exists(dst_dir):
                if not overwrite:
                    skipped += 1
                    continue
                shutil.rmtree(dst_dir)

            os.makedirs(dst_dir, exist_ok=True)
            if include_files:
                shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            else:
                shutil.copyfile(os.path.join(src_dir, "SKILL.md"), os.path.join(dst_dir, "SKILL.md"))

            skill_id = _deterministic_import_id(scope="common", owner=lib_name, rel_path=rel_key)
            md_path = os.path.join(dst_dir, "SKILL.md")
            raw = _read(md_path)
            _write(md_path, upsert_skill_md_id(raw, skill_id=skill_id))
            imported += 1
        except Exception as e:
            errors.append(f"{src_dir}: {e}")

    return {
        "source_root": src_root,
        "library": lib_name,
        "imported": int(imported),
        "skipped": int(skipped),
        "errors": errors,
    }


def _to_bool(v: Any, default: bool) -> bool:
    """Run to bool."""
    if v is None:
        return bool(default)
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if not s:
        return bool(default)
    if s in {"1", "true", "yes", "on"}:
        return True
    if s in {"0", "false", "no", "off"}:
        return False
    return bool(default)


def _to_int(v: Any, default: int) -> int:
    """Run to int."""
    try:
        return int(v)
    except Exception:
        return int(default)


def _to_str_list(v: Any) -> List[str]:
    """Run to str list."""
    if v is None:
        return []
    if isinstance(v, (list, tuple, set)):
        out = [str(x).strip() for x in v if str(x).strip()]
        return out
    s = str(v).strip()
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]


def run_service_startup_maintenance(
    *,
    sdk: Any,
    default_user_id: str,
    log_prefix: str = "[autoskill][startup]",
) -> Dict[str, Any]:
    """
    Runs startup offline checks/imports for local store.

    Controls:
    - AUTOSKILL_AUTO_NORMALIZE_IDS (default: 1)
    - AUTOSKILL_AUTO_IMPORT_DIRS (comma-separated paths)
    - AUTOSKILL_AUTO_IMPORT_SCOPE (common|user, default: common)
    - AUTOSKILL_AUTO_IMPORT_LIBRARY (for common scope)
    - AUTOSKILL_AUTO_IMPORT_OVERWRITE (default: 0)
    - AUTOSKILL_AUTO_IMPORT_INCLUDE_FILES (default: 1)
    - AUTOSKILL_AUTO_IMPORT_MAX_DEPTH (default: 6)
    - AUTOSKILL_AUTO_REFRESH_SKILLS (default: 1)
    - AUTOSKILL_AUTO_REFRESH_FORCE_VECTORS (default: 0)
    - AUTOSKILL_AUTO_REFRESH_BLOCKING (default: 1)
    """

    out: Dict[str, Any] = {
        "ran": False,
        "provider": "",
        "store_root": "",
        "normalize": None,
        "imports": [],
        "refresh": None,
    }
    try:
        cfg = dict(getattr(getattr(sdk, "config", None), "store", {}) or {})
        provider = str(cfg.get("provider") or "local").strip().lower()
        out["provider"] = provider
        if provider != "local":
            return out

        store_root = str(cfg.get("path") or "").strip()
        if not store_root:
            return out
        store_root = os.path.abspath(os.path.expanduser(store_root))
        out["store_root"] = store_root
        out["ran"] = True

        normalize_enabled = _to_bool(os.getenv("AUTOSKILL_AUTO_NORMALIZE_IDS"), default=True)
        max_depth = _to_int(os.getenv("AUTOSKILL_AUTO_IMPORT_MAX_DEPTH"), _to_int(cfg.get("auto_import_max_depth"), 6))
        if normalize_enabled:
            norm_stat = normalize_store_skill_ids(
                store_root=store_root,
                max_depth=max_depth,
                force=False,
            )
            out["normalize"] = norm_stat
            print(
                f"{log_prefix} normalize ids: scanned={norm_stat['scanned']} changed={norm_stat['changed']}"
            )

        cfg_dirs = _to_str_list(cfg.get("auto_import_dirs"))
        env_dirs = _to_str_list(os.getenv("AUTOSKILL_AUTO_IMPORT_DIRS"))
        auto_import_dirs = []
        seen = set()
        for d in cfg_dirs + env_dirs:
            ad = os.path.abspath(os.path.expanduser(str(d)))
            if ad in seen:
                continue
            seen.add(ad)
            auto_import_dirs.append(ad)

        if auto_import_dirs:
            scope = str(
                os.getenv("AUTOSKILL_AUTO_IMPORT_SCOPE")
                or cfg.get("auto_import_scope")
                or "common"
            ).strip().lower()
            if scope not in {"common", "user"}:
                scope = "common"
            overwrite = _to_bool(
                os.getenv("AUTOSKILL_AUTO_IMPORT_OVERWRITE"),
                default=_to_bool(cfg.get("auto_import_overwrite"), False),
            )
            include_files = _to_bool(
                os.getenv("AUTOSKILL_AUTO_IMPORT_INCLUDE_FILES"),
                default=_to_bool(cfg.get("auto_import_include_files"), True),
            )
            library_name = str(
                os.getenv("AUTOSKILL_AUTO_IMPORT_LIBRARY")
                or cfg.get("auto_import_library")
                or ""
            ).strip()
            import_user = str(cfg.get("auto_import_user_id") or default_user_id or "u1").strip() or "u1"

            for src in auto_import_dirs:
                if scope == "common":
                    stat = import_agent_skills_to_common(
                        store_root=store_root,
                        source_root=src,
                        library_name=library_name,
                        overwrite=overwrite,
                        include_files=include_files,
                        max_depth=max_depth,
                    )
                    out["imports"].append({"scope": "common", **stat})
                    print(
                        f"{log_prefix} auto-import common: src={src} imported={stat['imported']} skipped={stat['skipped']} errors={len(stat['errors'])}"
                    )
                    continue

                try:
                    imported = sdk.import_agent_skill_dirs(
                        root_dir=src,
                        user_id=import_user,
                        overwrite=overwrite,
                        include_files=include_files,
                        max_depth=max_depth,
                        reassign_ids=True,
                    )
                    stat = {
                        "scope": "user",
                        "source_root": src,
                        "user_id": import_user,
                        "imported": len(imported or []),
                        "skipped": 0,
                        "errors": [],
                    }
                except Exception as e:
                    stat = {
                        "scope": "user",
                        "source_root": src,
                        "user_id": import_user,
                        "imported": 0,
                        "skipped": 0,
                        "errors": [str(e)],
                    }
                out["imports"].append(stat)
                print(
                    f"{log_prefix} auto-import user: src={src} user={import_user} imported={stat['imported']} errors={len(stat['errors'])}"
                )

        refresh_enabled = _to_bool(os.getenv("AUTOSKILL_AUTO_REFRESH_SKILLS"), default=True)
        refresh_force_vectors = _to_bool(
            os.getenv("AUTOSKILL_AUTO_REFRESH_FORCE_VECTORS"),
            default=False,
        )
        refresh_blocking = _to_bool(
            os.getenv("AUTOSKILL_AUTO_REFRESH_BLOCKING"),
            default=True,
        )
        if refresh_enabled:
            stat = _refresh_local_store_runtime(
                sdk=sdk,
                force_vectors=refresh_force_vectors,
                blocking=refresh_blocking,
            )
            out["refresh"] = stat
            if isinstance(stat, dict):
                print(
                    f"{log_prefix} refresh skills: reloaded={stat.get('reloaded', 0)} vectors_rebuilt={stat.get('vectors_rebuilt_total', 0)} users={len(stat.get('users') or [])}"
                )
    except Exception as e:
        out["error"] = str(e)
        print(f"{log_prefix} startup maintenance failed: {e}")
    return out


def _refresh_local_store_runtime(
    *,
    sdk: Any,
    force_vectors: bool,
    blocking: bool,
) -> Optional[Dict[str, Any]]:
    """
    Best-effort local-store refresh hook:
    - reload disk skills into memory
    - refresh BM25 cache
    - refresh vector mappings
    """

    store = getattr(sdk, "store", None)
    if store is None:
        return None
    fn = getattr(store, "refresh_from_disk", None)
    if not callable(fn):
        return None
    try:
        out = fn(
            rebuild_vectors=True,
            force_rebuild_vectors=bool(force_vectors),
            blocking=bool(blocking),
        )
    except TypeError:
        out = fn()
    if out is None:
        return None
    if isinstance(out, dict):
        return dict(out)
    return {"result": out}
