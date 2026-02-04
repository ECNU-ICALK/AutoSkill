"""
Vector index interfaces.

AutoSkill stores Skills as directory artifacts (SKILL.md + optional resources). For retrieval, it
needs a fast mapping between Skill IDs and embedding vectors, plus a similarity search primitive.

This module defines a minimal, dependency-free interface for vector indexes so the SDK can support:
- a simple flat (exact) index stored on disk
- optional accelerated backends when available (e.g., hnswlib/faiss) without hard dependencies
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Sequence, Tuple


class VectorIndex(ABC):
    """
    Minimal vector index interface.

    Vectors are assumed to be dense float lists. Similarity is dot product (often equivalent to cosine
    similarity when embeddings are normalized).
    """

    @property
    @abstractmethod
    def dims(self) -> Optional[int]:
        raise NotImplementedError

    @abstractmethod
    def has(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> Optional[List[float]]:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, key: str, vector: Sequence[float]) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_vector: Sequence[float],
        *,
        keys: Optional[Iterable[str]] = None,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        raise NotImplementedError

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def reset(self, *, dims: Optional[int] = None) -> None:
        raise NotImplementedError
