"""
Vector backend factory with plugin registration.

Default backend:
- `flat`: dependency-free persistent exact index

Optional backends:
- `chroma`
- `milvus`
- `pinecone`

Custom backend:
- `backend_factory`: "module:function" returning a `VectorIndex` instance
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Callable, Dict, List

from .base import VectorIndex
from .chroma import ChromaVectorIndex
from .flat import FlatFileVectorIndex
from .milvus import MilvusVectorIndex
from .pinecone import PineconeVectorIndex

VectorBackendBuilder = Callable[[str, str, Dict[str, Any]], VectorIndex]

_VECTOR_BUILDERS: Dict[str, VectorBackendBuilder] = {}
_VECTOR_ALIASES: Dict[str, str] = {
    "filesystem": "flat",
    "local": "flat",
    "file": "flat",
    "disk": "flat",
}


def _normalize_backend(name: Any) -> str:
    """Run normalize backend."""
    s = str(name or "flat").strip().lower()
    if not s:
        s = "flat"
    return _VECTOR_ALIASES.get(s, s)


def _load_builder_from_path(path: str) -> VectorBackendBuilder:
    """Run load builder from path."""
    spec = str(path or "").strip()
    if not spec:
        raise ValueError("Empty backend_factory")
    if ":" in spec:
        module_name, attr = spec.split(":", 1)
    elif "." in spec:
        module_name, _, attr = spec.rpartition(".")
    else:
        raise ValueError(f"Invalid backend_factory path: {spec}")
    module_name = module_name.strip()
    attr = attr.strip()
    if not module_name or not attr:
        raise ValueError(f"Invalid backend_factory path: {spec}")
    module = importlib.import_module(module_name)
    builder = getattr(module, attr, None)
    if not callable(builder):
        raise ValueError(f"backend_factory is not callable: {spec}")
    return builder  # type: ignore[return-value]


def register_vector_backend(
    backend: str,
    builder: VectorBackendBuilder,
    *,
    aliases: List[str] | None = None,
    override: bool = True,
) -> None:
    """Run register vector backend."""
    key = _normalize_backend(backend)
    if not key:
        raise ValueError("backend is required")
    if (not override) and key in _VECTOR_BUILDERS:
        return
    _VECTOR_BUILDERS[key] = builder
    for a in (aliases or []):
        alias = str(a or "").strip().lower()
        if alias:
            _VECTOR_ALIASES[alias] = key


def list_vector_backends() -> List[str]:
    """Run list vector backends."""
    _ensure_builtins_registered()
    return sorted(_VECTOR_BUILDERS.keys())


def _build_flat(dir_path: str, name: str, config: Dict[str, Any]) -> VectorIndex:
    """Run build flat."""
    return FlatFileVectorIndex(dir_path=dir_path, name=name)


def _build_chroma(dir_path: str, name: str, config: Dict[str, Any]) -> VectorIndex:
    """Run build chroma."""
    persist_dir = str(config.get("persist_dir") or config.get("path") or dir_path)
    collection_name = str(config.get("collection_name") or config.get("collection") or name)
    metric = str(config.get("metric") or "cosine")
    return ChromaVectorIndex(
        persist_dir=persist_dir,
        collection_name=collection_name,
        metric=metric,
    )


def _build_milvus(dir_path: str, name: str, config: Dict[str, Any]) -> VectorIndex:
    """Run build milvus."""
    uri = str(config.get("uri") or config.get("host") or "").strip()
    if not uri:
        raise ValueError("Milvus backend requires `vector_backend_config.uri`")
    token = str(config.get("token") or os.getenv("MILVUS_TOKEN") or "")
    collection_name = str(config.get("collection_name") or config.get("collection") or name)
    metric_type = str(config.get("metric_type") or config.get("metric") or "COSINE")
    return MilvusVectorIndex(
        uri=uri,
        token=token,
        collection_name=collection_name,
        metric_type=metric_type,
    )


def _build_pinecone(dir_path: str, name: str, config: Dict[str, Any]) -> VectorIndex:
    """Run build pinecone."""
    api_key = str(config.get("api_key") or os.getenv("PINECONE_API_KEY") or "")
    index_name = str(config.get("index_name") or config.get("index") or "").strip()
    if not index_name:
        raise ValueError("Pinecone backend requires `vector_backend_config.index_name`")
    namespace = str(config.get("namespace") or "")
    host = str(config.get("host") or "")
    return PineconeVectorIndex(
        api_key=api_key,
        index_name=index_name,
        namespace=namespace,
        host=host,
    )


def _ensure_builtins_registered() -> None:
    """Run ensure builtins registered."""
    if _VECTOR_BUILDERS:
        return
    register_vector_backend("flat", _build_flat, aliases=["filesystem", "local", "file", "disk"])
    register_vector_backend("chroma", _build_chroma)
    register_vector_backend("milvus", _build_milvus)
    register_vector_backend("pinecone", _build_pinecone)


def build_vector_index(
    *,
    backend: str,
    dir_path: str,
    name: str = "skills",
    config: Dict[str, Any] | None = None,
) -> VectorIndex:
    """
    Builds a vector backend by name.

    `config` supports:
    - `backend_factory`: "module:function"
    - backend-specific settings (e.g., Milvus URI, Pinecone index_name).
    """

    _ensure_builtins_registered()
    cfg = dict(config or {})

    factory_path = str(
        cfg.get("backend_factory")
        or cfg.get("vector_factory")
        or cfg.get("provider_factory")
        or ""
    ).strip()
    if factory_path:
        return _load_builder_from_path(factory_path)(dir_path, name, cfg)

    key = _normalize_backend(backend)
    builder = _VECTOR_BUILDERS.get(key)
    if builder is None:
        raise ValueError(
            f"Unknown vector backend: {key}. "
            f"Available: {', '.join(list_vector_backends())}"
        )
    return builder(dir_path, name, cfg)

