"""
Embedding connector factory with plugin-style registration.

Compatibility:
- Keeps `build_embeddings(config)` as the main entry point.
- Preserves existing built-in providers and aliases.
- Allows runtime registration of custom connectors via `register_embedding_connector(...)`.
- Allows config-driven external builders via `connector_factory="module:function"`.
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Callable, Dict, List

from .base import EmbeddingModel
from .bigmodel import BigModelEmbedding3
from .generic import GenericEmbedding
from .hashing import HashingEmbedding
from .none import DisabledEmbedding
from .openai import OpenAIEmbedding

EmbeddingBuilder = Callable[[Dict[str, Any]], EmbeddingModel]

_EMBEDDING_BUILDERS: Dict[str, EmbeddingBuilder] = {}
_EMBEDDING_ALIASES: Dict[str, str] = {
    # Generic OpenAI-compatible embeddings endpoint.
    "universal": "generic",
    "custom": "generic",
    "openai-compatible": "generic",
    "openai_compatible": "generic",
    # No-embedding mode (BM25-only retrieval fallback).
    "off": "none",
    "disabled": "none",
    "null": "none",
    "no_embedding": "none",
    "no-embedding": "none",
    # BigModel / GLM aliases.
    "bigmodel": "glm",
    "zhipu": "glm",
    # DashScope / Qwen aliases.
    "qwen": "dashscope",
}


def _normalize_provider(name: Any) -> str:
    """Run normalize provider."""
    s = str(name or "hashing").strip().lower()
    if not s:
        s = "hashing"
    return _EMBEDDING_ALIASES.get(s, s)


def _load_builder_from_path(path: str) -> EmbeddingBuilder:
    """Run load builder from path."""
    spec = str(path or "").strip()
    if not spec:
        raise ValueError("Empty connector_factory")
    if ":" in spec:
        module_name, attr = spec.split(":", 1)
    elif "." in spec:
        module_name, _, attr = spec.rpartition(".")
    else:
        raise ValueError(f"Invalid connector_factory path: {spec}")
    module_name = module_name.strip()
    attr = attr.strip()
    if not module_name or not attr:
        raise ValueError(f"Invalid connector_factory path: {spec}")
    module = importlib.import_module(module_name)
    builder = getattr(module, attr, None)
    if not callable(builder):
        raise ValueError(f"connector_factory is not callable: {spec}")
    return builder  # type: ignore[return-value]


def register_embedding_connector(
    provider: str,
    builder: EmbeddingBuilder,
    *,
    aliases: List[str] | None = None,
    override: bool = True,
) -> None:
    """
    Registers an embedding connector builder for a provider name.

    Example:
        register_embedding_connector("myemb", build_myemb, aliases=["my-emb"])
    """

    key = _normalize_provider(provider)
    if not key:
        raise ValueError("provider is required")
    if (not override) and key in _EMBEDDING_BUILDERS:
        return
    _EMBEDDING_BUILDERS[key] = builder
    for a in (aliases or []):
        alias = str(a or "").strip().lower()
        if alias:
            _EMBEDDING_ALIASES[alias] = key


def list_embedding_connectors() -> List[str]:
    """Run list embedding connectors."""
    _ensure_builtins_registered()
    return sorted(_EMBEDDING_BUILDERS.keys())


def _build_hashing(config: Dict[str, Any]) -> EmbeddingModel:
    """Run build hashing."""
    return HashingEmbedding(dims=int(config.get("dims", 256)))


def _build_none(config: Dict[str, Any]) -> EmbeddingModel:
    """Run build none."""
    return DisabledEmbedding()


def _build_openai(config: Dict[str, Any]) -> EmbeddingModel:
    """Run build openai."""
    return OpenAIEmbedding(
        model=str(config.get("model", "text-embedding-3-small")),
        api_key=config.get("api_key"),
        base_url=str(config.get("base_url", "https://api.openai.com")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_text_chars=int(config.get("max_text_chars", 10000)),
        min_text_chars=int(config.get("min_text_chars", 512)),
        max_batch_size=int(config.get("max_batch_size", 256)),
        extra_body=(config.get("extra_body") or config.get("extra_payload")),
    )


def _build_generic(config: Dict[str, Any]) -> EmbeddingModel:
    """Run build generic."""
    base_url = str(
        config.get("url")
        or config.get("base_url")
        or "http://s-20260204155338-p8gv8.ailab-evalservice.pjh-service.org.cn/v1"
    )
    return GenericEmbedding(
        model=str(config.get("model", "embd_qwen3vl8b")),
        api_key=(config.get("api_key") or os.getenv("AUTOSKILL_GENERIC_API_KEY") or ""),
        base_url=base_url,
        timeout_s=int(config.get("timeout_s", 60)),
        max_text_chars=int(config.get("max_text_chars", 10000)),
        min_text_chars=int(config.get("min_text_chars", 512)),
        max_batch_size=int(config.get("max_batch_size", 256)),
        extra_body=(config.get("extra_body") or config.get("extra_payload")),
    )


def _build_dashscope(config: Dict[str, Any]) -> EmbeddingModel:
    """Run build dashscope."""
    extra = config.get("extra_body") or config.get("extra_payload") or {}
    extra_dict = dict(extra) if isinstance(extra, dict) else {}
    extra_dict.setdefault("dimensions", 1024)
    extra_dict.setdefault("encoding_format", "float")
    return OpenAIEmbedding(
        model=str(config.get("model", "text-embedding-v4")),
        api_key=(config.get("api_key") or os.getenv("DASHSCOPE_API_KEY")),
        base_url=str(config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_text_chars=int(config.get("max_text_chars", 10000)),
        min_text_chars=int(config.get("min_text_chars", 512)),
        max_batch_size=int(config.get("max_batch_size", 1)),
        extra_body=extra_dict,
    )


def _build_glm(config: Dict[str, Any]) -> EmbeddingModel:
    """Run build glm."""
    return BigModelEmbedding3(
        model=str(config.get("model", "embedding-3")),
        api_key=config.get("api_key"),
        api_key_id=config.get("api_key_id"),
        api_key_secret=config.get("api_key_secret"),
        base_url=str(config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")),
        timeout_s=int(config.get("timeout_s", 60)),
        token_ttl_s=int(config.get("token_ttl_s", 3600)),
        token_time_unit=str(config.get("token_time_unit", "ms")),
        auth_mode=str(config.get("auth_mode", "auto")),
        extra_body=(config.get("extra_body") or config.get("extra_payload")),
        max_text_chars=int(config.get("max_text_chars", 10000)),
        min_text_chars=int(config.get("min_text_chars", 512)),
    )


def _ensure_builtins_registered() -> None:
    """Run ensure builtins registered."""
    if _EMBEDDING_BUILDERS:
        return
    register_embedding_connector("none", _build_none, aliases=["off", "disabled", "null", "no_embedding", "no-embedding"])
    register_embedding_connector("hashing", _build_hashing)
    register_embedding_connector("openai", _build_openai)
    register_embedding_connector("generic", _build_generic, aliases=["openai-compatible", "openai_compatible", "universal", "custom"])
    register_embedding_connector("dashscope", _build_dashscope, aliases=["qwen"])
    register_embedding_connector("glm", _build_glm, aliases=["bigmodel", "zhipu"])


def build_embeddings(config: Dict[str, Any]) -> EmbeddingModel:
    """
    Builds an embedding connector from config.

    Extra plugin options:
    - `connector_factory`: "module:function" returning an `EmbeddingModel` instance.
    - runtime registration via `register_embedding_connector(...)`.
    """

    _ensure_builtins_registered()
    cfg = dict(config or {})

    factory_path = str(
        cfg.get("connector_factory")
        or cfg.get("embedding_connector_factory")
        or cfg.get("provider_factory")
        or ""
    ).strip()
    if factory_path:
        return _load_builder_from_path(factory_path)(cfg)

    provider = _normalize_provider(cfg.get("provider") or "hashing")
    builder = _EMBEDDING_BUILDERS.get(provider)
    if builder is None:
        raise ValueError(
            f"Unknown embeddings provider: {provider}. "
            f"Available: {', '.join(list_embedding_connectors())}"
        )
    return builder(cfg)
