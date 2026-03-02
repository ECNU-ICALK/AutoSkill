"""
Disabled embedding connector.

Use provider `none` to run retrieval in keyword/BM25-only mode.
"""

from __future__ import annotations

from typing import List

from .base import EmbeddingModel


class DisabledEmbedding(EmbeddingModel):
    disabled = True

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Run embed."""
        raise RuntimeError("Embeddings are disabled (provider=none).")

