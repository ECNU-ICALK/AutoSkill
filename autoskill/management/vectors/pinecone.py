"""
Pinecone-backed vector index adapter (optional dependency).

This backend is loaded lazily via the vectors factory and only requires `pinecone`
when actually configured.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .base import VectorIndex


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    s = 0.0
    for x, y in zip(a, b):
        s += float(x) * float(y)
    return float(s)


def _to_dict(obj: Any) -> Dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        try:
            out = to_dict()
            if isinstance(out, dict):
                return out
        except Exception:
            return {}
    return {}


class PineconeVectorIndex(VectorIndex):
    def __init__(
        self,
        *,
        api_key: str,
        index_name: str,
        namespace: str = "",
        host: str = "",
    ) -> None:
        try:
            from pinecone import Pinecone  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Pinecone backend requires `pinecone`. Install it first "
                "(e.g. `pip install pinecone`)."
            ) from e

        key = str(api_key or "").strip()
        idx_name = str(index_name or "").strip()
        if not key:
            raise ValueError("Pinecone backend requires `api_key`")
        if not idx_name:
            raise ValueError("Pinecone backend requires `index_name`")

        self._lock = threading.RLock()
        self._dims: Optional[int] = None
        self._namespace = str(namespace or "").strip()
        self._pc = Pinecone(api_key=key)
        host_s = str(host or "").strip()
        if host_s:
            self._index = self._pc.Index(host=host_s)
        else:
            self._index = self._pc.Index(idx_name)
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
                out = self._index.fetch(ids=[sid], namespace=self._namespace)
            except Exception:
                return None
            obj = _to_dict(out)
            vectors = obj.get("vectors") or {}
            if not isinstance(vectors, dict):
                return None
            row = vectors.get(sid) or vectors.get(str(sid))
            if not isinstance(row, dict):
                return None
            values = row.get("values") or row.get("vector")
            if not isinstance(values, list):
                return None
            vec = [float(x) for x in values]
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
            self._index.upsert(
                vectors=[{"id": sid, "values": vec}],
                namespace=self._namespace,
            )

    def delete(self, key: str) -> bool:
        sid = str(key or "").strip()
        if not sid:
            return False
        existed = self.has(sid)
        with self._lock:
            try:
                self._index.delete(ids=[sid], namespace=self._namespace)
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
                out = self._index.query(
                    vector=q,
                    top_k=k,
                    namespace=self._namespace,
                    include_values=False,
                )
            except Exception:
                return []
            obj = _to_dict(out)
            matches = obj.get("matches") or []
            if not isinstance(matches, list):
                return []
            scored2: List[Tuple[str, float]] = []
            for m in matches:
                if not isinstance(m, dict):
                    continue
                sid = str(m.get("id") or "").strip()
                if not sid:
                    continue
                score = float(m.get("score") or 0.0)
                scored2.append((sid, score))
            scored2.sort(key=lambda x: x[1], reverse=True)
            return scored2[:k]

    def load(self) -> None:
        # No explicit load phase for managed Pinecone indexes.
        return None

    def save(self) -> None:
        # Managed service persists server-side.
        return None

    def reset(self, *, dims: Optional[int] = None) -> None:
        with self._lock:
            self._index.delete(delete_all=True, namespace=self._namespace)
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

