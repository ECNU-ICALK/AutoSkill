"""
Shared library/runtime path helpers for AutoSkill4Doc.

The document skill library exposes two layers:

- visible layer under `<store_root>/<school_name>/...`
- runtime layer under `<store_root>/.runtime/...`

These helpers centralize path rules so visible tree sync, staging, hierarchy
browse, and migration do not all maintain separate path conventions.
"""

from __future__ import annotations

import os
import re

from ..core.config import default_store_path

_DIR_COMPONENT_CLEAN_RE = re.compile(r"[\s/\\:]+")
_DIR_COMPONENT_NOISE_RE = re.compile(r"[^\w\-\u4e00-\u9fff]+")
_VISIBLE_COMPONENT_NOISE_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_RESERVED_VISIBLE_ROOT_NAMES = {
    ".runtime",
    "users",
    "common",
    "vectors",
    "index",
    "__pycache__",
}


def normalize_library_root(base_store_root: str = "") -> str:
    """Normalizes one document skill library root path."""

    return os.path.abspath(os.path.expanduser(str(base_store_root or "").strip() or default_store_path()))


def runtime_root(base_store_root: str = "") -> str:
    """Returns the runtime root under one document skill library."""

    return os.path.join(normalize_library_root(base_store_root), ".runtime")


def runtime_store_root(base_store_root: str = "") -> str:
    """Returns the reserved runtime store root for future canonical stores."""

    return os.path.join(runtime_root(base_store_root), "store")


def registry_root(base_store_root: str = "") -> str:
    """Returns the document registry root under the runtime tree."""

    return os.path.join(runtime_root(base_store_root), "document_registry")


def library_manifest_path(base_store_root: str = "") -> str:
    """Returns the path to `.runtime/library_manifest.json`."""

    return os.path.join(runtime_root(base_store_root), "library_manifest.json")


def staging_root(base_store_root: str = "") -> str:
    """Returns the canonical-merge staging root."""

    return os.path.join(runtime_root(base_store_root), "staging")


def intermediate_runs_root(base_store_root: str = "") -> str:
    """Returns the intermediate run root for incremental stage artifacts."""

    return os.path.join(runtime_root(base_store_root), "intermediate_runs")


def intermediate_run_dir(*, base_store_root: str, run_id: str) -> str:
    """Returns the directory for one intermediate extraction run."""

    return os.path.join(intermediate_runs_root(base_store_root), safe_dir_component(run_id or "run"))


def previews_root(base_store_root: str = "") -> str:
    """Returns the preview export root."""

    return os.path.join(runtime_root(base_store_root), "previews")


def legacy_backup_root(base_store_root: str = "") -> str:
    """Returns the legacy-layout backup root."""

    return os.path.join(runtime_root(base_store_root), "legacy_backup")


def school_visible_root(*, base_store_root: str, school_name: str) -> str:
    """Returns the visible root directory for one school/family."""

    return os.path.join(normalize_library_root(base_store_root), safe_school_name(school_name or "未命名流派"))


def school_parent_visible_root(*, base_store_root: str, school_name: str) -> str:
    """Returns the visible `总技能` directory for one school."""

    return os.path.join(school_visible_root(base_store_root=base_store_root, school_name=school_name), "总技能")


def school_children_visible_root(*, base_store_root: str, school_name: str) -> str:
    """Returns the visible `子技能` directory for one school."""

    return os.path.join(school_visible_root(base_store_root=base_store_root, school_name=school_name), "子技能")


def safe_dir_component(value: str) -> str:
    """Converts one internal identifier into a filesystem-safe path component."""

    s = str(value or "").strip()
    if not s:
        return "unknown"
    s = _DIR_COMPONENT_CLEAN_RE.sub("_", s).strip("_")
    s = _DIR_COMPONENT_NOISE_RE.sub("_", s).strip("_")
    s = re.sub(r"_+", "_", s).strip("_")
    if len(s) > 64:
        s = s[:64].rstrip("_")
    return s or "unknown"


def safe_visible_name(value: str) -> str:
    """Converts one visible school/skill name into a safe readable directory name."""

    s = str(value or "").strip()
    if not s:
        return "未命名"
    s = _VISIBLE_COMPONENT_NOISE_RE.sub("-", s)
    s = re.sub(r"\s+", " ", s).strip(" .-")
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > 80:
        s = s[:80].rstrip(" .-")
    return s or "未命名"


def safe_school_name(value: str) -> str:
    """Converts a visible school/family name into a root-safe directory name."""

    name = safe_visible_name(value or "未命名流派")
    if str(name or "").strip().lower() in _RESERVED_VISIBLE_ROOT_NAMES:
        return f"{name}-skills"
    return name
