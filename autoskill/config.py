"""
A minimal SDK configuration object (low-dependency, serializable, constructible from dict).

AutoSkillConfig uses “plain dict provider configs” to:
- be embedded as a SDK in other projects
- avoid extra dependencies (e.g., official vendor SDKs)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AutoSkillConfig:
    """
    Minimal SDK configuration.

    All provider configs are plain dicts to keep the SDK dependency-free.
    """

    llm: Dict[str, Any] = field(default_factory=lambda: {"provider": "mock"})
    embeddings: Dict[str, Any] = field(
        default_factory=lambda: {"provider": "hashing", "dims": 256}
    )
    store: Dict[str, Any] = field(default_factory=lambda: {"provider": "inmemory"})

    namespace: str = "default"

    maintenance_strategy: str = "heuristic"  # "heuristic" | "llm"
    dedupe_similarity_threshold: float = 0.86
    max_candidates_per_ingest: int = 1
    max_similar_skills_to_consider: int = 5

    default_search_limit: int = 5
    max_context_chars: int = 6_000

    redact_sources_before_llm: bool = True

    store_sources: bool = True

    extra: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoSkillConfig":
        data = dict(data or {})
        if "embeddings" not in data and "embedding" in data:
            data["embeddings"] = data.get("embedding")
        if "store" not in data and "vector_store" in data:
            data["store"] = data.get("vector_store")
        known = {
            "llm",
            "embeddings",
            "store",
            "namespace",
            "maintenance_strategy",
            "dedupe_similarity_threshold",
            "max_candidates_per_ingest",
            "max_similar_skills_to_consider",
            "default_search_limit",
            "max_context_chars",
            "redact_sources_before_llm",
            "store_sources",
        }
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(
            llm=dict(data.get("llm") or {"provider": "mock"}),
            embeddings=dict(data.get("embeddings") or {"provider": "hashing", "dims": 256}),
            store=dict(data.get("store") or {"provider": "inmemory"}),
            namespace=str(data.get("namespace") or "default"),
            maintenance_strategy=str(data.get("maintenance_strategy") or "heuristic"),
            dedupe_similarity_threshold=float(data.get("dedupe_similarity_threshold", 0.86)),
            max_candidates_per_ingest=int(data.get("max_candidates_per_ingest", 1)),
            max_similar_skills_to_consider=int(data.get("max_similar_skills_to_consider", 5)),
            default_search_limit=int(data.get("default_search_limit", 5)),
            max_context_chars=int(data.get("max_context_chars", 6_000)),
            redact_sources_before_llm=bool(data.get("redact_sources_before_llm", True)),
            store_sources=bool(data.get("store_sources", True)),
            extra=extra or None,
        )
