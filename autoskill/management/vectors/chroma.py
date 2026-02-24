"""
Chroma-backed vector index adapter (optional dependency).

This backend is loaded lazily via the vectors factory and only requires `chromadb`
when actually configured.
"""

from __future__ import annotations

import threading
from typing import Any, Iterable, List, Optional, Sequence, Tuple

from .base import VectorIndex


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    s = 0.0
    for x, y in zip(a, b):
        s += float(x) * float(y)
    return float(s)


class ChromaVectorIndex(VectorIndex):
    def __init__(
        self,
        *,
        persist_dir: str,
        collection_name: str = "skills",
        metric: str = "cosine",
    ) -> None:
        try:
            import chromadb  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Chroma backend requires `chromadb`. Install it first "
                "(e.g. `pip install chromadb`)."
            ) from e

        self._lock = threading.RLock()
        self._dims: Optional[int] = None
        self._collection_name = str(collection_name or "skills").strip() or "skills"
        self._metric = str(metric or "cosine").strip().lower() or "cosine"
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": self._metric},
        )
        self.load()

    @property
    def dims(self) -> Optional[int]:
        return self._dims

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def get(self, key: str) -> Optional[List[float]]:
        sid = str(key or "").strip()
        if not sid:
            return None
        with self._lock:
            try:
                out = self._collection.get(ids=[sid], include=["embeddings"])
            except Exception:
                return None
            ids = list(out.get("ids") or [])
            embs = list(out.get("embeddings") or [])
            if not ids or not embs:
                return None
            emb0 = embs[0]
            if not isinstance(emb0, list):
                return None
            vec = [float(x) for x in emb0]
            if vec and self._dims is None:
                self._dims = len(vec)
            return vec

    def upsert(self, key: str, vector: Sequence[float]) -> None:
        sid = str(key or "").strip()
        vec = [float(x) for x in (vector or [])]
        if not sid or not vec:
            return
        with self._lock:
            self._ensure_dims(len(vec))
            self._collection.upsert(ids=[sid], embeddings=[vec])

    def delete(self, key: str) -> bool:
        sid = str(key or "").strip()
        if not sid:
            return False
        existed = self.has(sid)
        with self._lock:
            try:
                self._collection.delete(ids=[sid])
            except Exception:
                return False
        return existed

    def search(
        self,
        query_vector: Sequence[float],
        *,
        keys: Optional[Iterable[str]] = None,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        k = max(0, int(top_k))
        q = [float(x) for x in (query_vector or [])]
        if k <= 0 or not q:
            return []

        with self._lock:
            d = int(self._dims or 0)
            if d > 0 and len(q) != d:
                return []

            if keys is not None:
                scored: List[Tuple[str, float]] = []
                for sid in keys:
                    sid_s = str(sid or "").strip()
                    if not sid_s:
                        continue
                    vec = self.get(sid_s)
                    if not vec:
                        continue
                    scored.append((sid_s, _dot(q, vec)))
                scored.sort(key=lambda x: x[1], reverse=True)
                return scored[:k]

            try:
                out = self._collection.query(
                    query_embeddings=[q],
                    n_results=k,
                    include=["distances"],
                )
            except Exception:
                return []

            ids_rows = list(out.get("ids") or [])
            if not ids_rows:
                return []
            ids = list(ids_rows[0] or [])
            dist_rows = list(out.get("distances") or [])
            dists = list(dist_rows[0] or []) if dist_rows else []

            scored2: List[Tuple[str, float]] = []
            for i, sid in enumerate(ids):
                sid_s = str(sid or "").strip()
                if not sid_s:
                    continue
                # For cosine distance, smaller is better, convert to similarity-like score.
                if i < len(dists):
                    score = 1.0 - float(dists[i])
                else:
                    score = 0.0
                scored2.append((sid_s, float(score)))

            scored2.sort(key=lambda x: x[1], reverse=True)
            return scored2[:k]

    def load(self) -> None:
        with self._lock:
            try:
                out = self._collection.get(limit=1, include=["embeddings"])
            except Exception:
                return
            embs = list(out.get("embeddings") or [])
            if not embs:
                return
            first = embs[0]
            if isinstance(first, list) and first:
                self._dims = len(first)

    def save(self) -> None:
        # Chroma persistence is managed by the client.
        return None

    def reset(self, *, dims: Optional[int] = None) -> None:
        with self._lock:
            try:
                self._client.delete_collection(self._collection_name)
            except Exception:
                pass
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": self._metric},
            )
            self._dims = int(dims) if dims is not None else None

    def _ensure_dims(self, dims: int) -> None:
        d = int(dims)
        if d <= 0:
            return
        if self._dims is None:
            self._dims = d
            return
        if int(self._dims) != d:
            self.reset(dims=d)

