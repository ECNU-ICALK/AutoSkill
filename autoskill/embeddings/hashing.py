"""
Offline hashing embeddings.

Use cases:
- demo / tests (no network, no external dependencies)
Limitations:
- not a real semantic embedding model; it is deterministic and mainly validates the “store/retrieval pipeline”
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import List

from .base import EmbeddingModel

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[^\W\d_]+")


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class HashingEmbedding(EmbeddingModel):
    """
    Dependency-free deterministic embeddings.

    This is NOT a semantic embedding model, but works as an offline fallback for demos/tests.
    """

    dims: int = 256

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            vec = [0.0] * self.dims
            for token in _tokenize(text):
                digest = hashlib.md5(token.encode("utf-8")).digest()
                idx = int.from_bytes(digest[:4], "little") % self.dims
                sign = 1.0 if (digest[4] & 1) == 0 else -1.0
                vec[idx] += sign
            # After normalization, dot product == cosine similarity, so the store can score with a simple dot().
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vectors.append([v / norm for v in vec])
        return vectors
