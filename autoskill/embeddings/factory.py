"""
Embedding factory: build a concrete provider from a config dict.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import EmbeddingModel
from .bigmodel import BigModelEmbedding3
from .hashing import HashingEmbedding
from .openai import OpenAIEmbedding


def build_embeddings(config: Dict[str, Any]) -> EmbeddingModel:
    provider = (config.get("provider") or "hashing").lower()

    if provider == "hashing":
        return HashingEmbedding(dims=int(config.get("dims", 256)))

    if provider == "openai":
        return OpenAIEmbedding(
            model=str(config.get("model", "text-embedding-3-small")),
            api_key=config.get("api_key"),
            base_url=str(config.get("base_url", "https://api.openai.com")),
            timeout_s=int(config.get("timeout_s", 60)),
        )

    if provider in {"glm", "bigmodel", "zhipu"}:
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
            max_text_chars=int(config.get("max_text_chars", 12000)),
            min_text_chars=int(config.get("min_text_chars", 512)),
        )

    raise ValueError(f"Unknown embeddings provider: {provider}")
