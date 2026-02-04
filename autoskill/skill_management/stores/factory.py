"""
Store factory: build a SkillStore from config.store/provider.
"""

from __future__ import annotations

import os
from typing import List, Tuple

from ...config import AutoSkillConfig
from ...embeddings.factory import build_embeddings
from .base import SkillStore
from .inmemory import InMemorySkillStore
from .local import LocalSkillStore


def build_store(config: AutoSkillConfig) -> SkillStore:
    provider = (config.store.get("provider") or "inmemory").lower()
    embeddings = build_embeddings(config.embeddings)

    if provider == "inmemory":
        return InMemorySkillStore(embeddings=embeddings)

    if provider in {"local", "dir", "skill_dir", "skills", "filesystem"}:
        # Filesystem store: one skill per directory (SKILL.md + optional resources).
        default_dir = "Skills"
        path = str(
            config.store.get("path")
            or config.store.get("root_dir")
            or config.store.get("dir")
            or default_dir
        )
        max_depth = int(config.store.get("max_depth", 6))
        cache_vectors = bool(config.store.get("cache_vectors", True))
        vector_cache_dirname = str(
            config.store.get("vector_cache_dirname", ".autoskill/vectors")
        )

        users_dirname = str(
            config.store.get("users_dirname")
            or config.store.get("users_dir")
            or config.store.get("user_dirname")
            or "Users"
        )
        libraries_dirname = str(
            config.store.get("libraries_dirname")
            or config.store.get("libraries_dir")
            or config.store.get("library_dirname")
            or "Common"
        )
        include_libraries = bool(config.store.get("include_libraries", True))
        include_legacy_root = bool(config.store.get("include_legacy_root", False))

        library_dirs: List[Tuple[str, str]] = []
        raw_libs = (
            config.store.get("libraries")
            or config.store.get("library_dirs")
            or config.store.get("library_paths")
            or []
        )
        if isinstance(raw_libs, str):
            raw_libs = [p.strip() for p in raw_libs.split(",") if p.strip()]
        if isinstance(raw_libs, list):
            for item in raw_libs:
                if isinstance(item, str):
                    p = item.strip()
                    if not p:
                        continue
                    name = os.path.basename(p.rstrip("/")) or "library"
                    library_dirs.append((name, p))
                elif isinstance(item, dict):
                    p = str(item.get("path") or item.get("dir") or "").strip()
                    if not p:
                        continue
                    name = str(item.get("name") or os.path.basename(p.rstrip("/")) or "library").strip()
                    library_dirs.append((name, p))

        return LocalSkillStore(
            embeddings=embeddings,
            path=path,
            max_depth=max_depth,
            cache_vectors=cache_vectors,
            vector_cache_dirname=vector_cache_dirname,
            users_dirname=users_dirname,
            libraries_dirname=libraries_dirname,
            library_dirs=library_dirs or None,
            include_libraries=include_libraries,
            include_legacy_root=include_legacy_root,
        )

    raise ValueError(f"Unknown store provider: {provider}")
