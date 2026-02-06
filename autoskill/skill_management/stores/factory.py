"""
Store factory: build a SkillStore from config.store/provider.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import List, Tuple

from ...config import AutoSkillConfig, default_store_path
from ...embeddings.factory import build_embeddings
from .base import SkillStore
from .inmemory import InMemorySkillStore
from .local import LocalSkillStore


_SAFE_NAME_RE = re.compile(r"[^a-z0-9]+")


def _slug(value: str, *, max_len: int = 32) -> str:
    s = str(value or "").strip().lower()
    s = _SAFE_NAME_RE.sub("-", s).strip("-")
    if not s:
        return "model"
    return s[: max(1, int(max_len))]


def _embedding_signature(config: AutoSkillConfig) -> dict:
    emb = dict(config.embeddings or {})
    provider = str(emb.get("provider") or "hashing").strip().lower()
    if provider in {"bigmodel", "zhipu"}:
        provider = "glm"
    if provider == "qwen":
        provider = "dashscope"

    model = str(emb.get("model") or "").strip()
    if not model:
        if provider == "openai":
            model = "text-embedding-3-small"
        elif provider == "glm":
            model = "embedding-3"
        elif provider == "dashscope":
            model = "text-embedding-v4"
        else:
            model = "default"

    dimensions = None
    if provider == "hashing":
        try:
            dimensions = int(emb.get("dims", 256))
        except Exception:
            dimensions = 256
    else:
        extra = emb.get("extra_body") or emb.get("extra_payload") or {}
        if isinstance(extra, dict):
            dimensions = extra.get("dimensions")
        if dimensions is None:
            dimensions = emb.get("dimensions")
        try:
            dimensions = int(dimensions) if dimensions is not None else None
        except Exception:
            dimensions = None

    sig = {"provider": provider, "model": model}
    if dimensions is not None:
        sig["dimensions"] = int(dimensions)
    return sig


def _vector_index_name_from_embeddings(config: AutoSkillConfig) -> str:
    sig = _embedding_signature(config)
    provider = str(sig.get("provider") or "emb")
    model = str(sig.get("model") or "model")
    dims = sig.get("dimensions")

    payload = json.dumps(sig, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:10]

    parts = ["skills", _slug(provider, max_len=16), _slug(model, max_len=28)]
    if isinstance(dims, int) and dims > 0:
        parts.append(f"d{dims}")
    parts.append(digest)
    return "-".join([p for p in parts if p])


def build_store(config: AutoSkillConfig) -> SkillStore:
    provider = (config.store.get("provider") or "inmemory").lower()
    embeddings = build_embeddings(config.embeddings)

    if provider == "inmemory":
        return InMemorySkillStore(embeddings=embeddings)

    if provider in {"local", "dir", "skill_dir", "skills", "filesystem"}:
        # Filesystem store: one skill per directory (SKILL.md + optional resources).
        default_dir = default_store_path()
        path = str(
            config.store.get("path")
            or config.store.get("root_dir")
            or config.store.get("dir")
            or default_dir
        )
        max_depth = int(config.store.get("max_depth", 6))
        cache_vectors = bool(config.store.get("cache_vectors", True))
        vector_cache_dirname = str(
            config.store.get("vector_cache_dirname", "vectors")
        )
        vector_index_name = str(
            config.store.get("vector_index_name")
            or config.store.get("vector_index")
            or _vector_index_name_from_embeddings(config)
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
            vector_index_name=vector_index_name,
            users_dirname=users_dirname,
            libraries_dirname=libraries_dirname,
            library_dirs=library_dirs or None,
            include_libraries=include_libraries,
            include_legacy_root=include_legacy_root,
        )

    raise ValueError(f"Unknown store provider: {provider}")
