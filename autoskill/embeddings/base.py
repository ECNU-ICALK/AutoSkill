"""
Embedding interface.

The store only needs one minimal capability: convert a list of texts into vectors
(List[List[float]]).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class EmbeddingModel(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Run embed."""
        raise NotImplementedError


# Backward-compatible semantic alias used by plugin-style factory APIs.
EmbeddingConnector = EmbeddingModel
