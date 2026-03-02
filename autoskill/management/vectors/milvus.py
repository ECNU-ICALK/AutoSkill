"""
Milvus-backed vector index adapter (optional dependency).

This backend is loaded lazily via the vectors factory and only requires `pymilvus`
when actually configured.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .base import VectorIndex


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Run dot."""
    if not a or not b or len(a) != len(b):
        return 0.0
    s = 0.0
    for x, y in zip(a, b):
        s += float(x) * float(y)
    return float(s)


class MilvusVectorIndex(VectorIndex):
    def __init__(
        self,
        *,
        uri: str,
        token: str = "",
        collection_name: str = "autoskill_skills",
        metric_type: str = "COSINE",
    ) -> None:
        """Run init."""
        try:
            import pymilvus  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "Milvus backend requires `pymilvus`. Install it first "
                "(e.g. `pip install pymilvus`)."
            ) from e

        client_cls = getattr(pymilvus, "MilvusClient", None)
        if client_cls is None:
            raise RuntimeError(
                "Current `pymilvus` does not expose MilvusClient; please upgrade pymilvus."
            )

        uri_s = str(uri or "").strip()
        if not uri_s:
            raise ValueError("Milvus backend requires `uri`")

        kwargs: Dict[str, Any] = {"uri": uri_s}
        tok = str(token or "").strip()
        if tok:
            kwargs["token"] = tok

        self._lock = threading.RLock()
        self._client = client_cls(**kwargs)
        self._collection = str(collection_name or "autoskill_skills").strip() or "autoskill_skills"
        self._metric = str(metric_type or "COSINE").strip().upper() or "COSINE"
        self._dims: Optional[int] = None
        self.load()

    @property
    def dims(self) -> Optional[int]:
        """Run dims."""
        return self._dims

    def has(self, key: str) -> bool:
        """Run has."""
        return self.get(key) is not None

    def get(self, key: str) -> Optional[List[float]]:
        """Run get."""
        sid = str(key or "").strip()
        if not sid or not self._has_collection():
            return None
        with self._lock:
            rows = self._get_rows([sid])
            if not rows:
                return None
            row = rows[0]
            vec = (
                row.get("vector")
                or row.get("embedding")
                or row.get("values")
                or row.get("emb")
            )
            if not isinstance(vec, list):
                return None
            out = [float(x) for x in vec]
            if out and self._dims is None:
                self._dims = len(out)
            return out

    def upsert(self, key: str, vector: Sequence[float]) -> None:
        """Run upsert."""
        sid = str(key or "").strip()
        vec = [float(x) for x in (vector or [])]
        if not sid or not vec:
            return
        with self._lock:
            self._ensure_collection(len(vec))
            payload = [{"id": sid, "vector": vec}]
            try:
                self._client.upsert(collection_name=self._collection, data=payload)
            except Exception:
                # Some deployments may prefer `embedding` field naming.
                payload2 = [{"id": sid, "embedding": vec}]
                self._client.upsert(collection_name=self._collection, data=payload2)

    def delete(self, key: str) -> bool:
        """Run delete."""
        sid = str(key or "").strip()
        if not sid or not self._has_collection():
            return False
        existed = self.has(sid)
        with self._lock:
            try:
                self._client.delete(collection_name=self._collection, ids=[sid])
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
        """Run search."""
        k = max(0, int(top_k))
        q = [float(x) for x in (query_vector or [])]
        if k <= 0 or not q or not self._has_collection():
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
                out = self._client.search(
                    collection_name=self._collection,
                    data=[q],
                    limit=k,
                    output_fields=["id"],
                )
            except Exception:
                return []

            rows = out[0] if isinstance(out, list) and out else []
            if not isinstance(rows, list):
                return []
            scored2: List[Tuple[str, float]] = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                sid = str(
                    row.get("id")
                    or row.get("pk")
                    or row.get("primary_key")
                    or ""
                ).strip()
                if not sid:
                    continue
                score = row.get("score", row.get("distance", 0.0))
                scored2.append((sid, float(score or 0.0)))
            scored2.sort(key=lambda x: x[1], reverse=True)
            return scored2[:k]

    def load(self) -> None:
        # Milvus metadata does not reliably expose vector dims across versions without schema traversal.
        # Keep lazy dimension detection from first upsert/get.
        """Run load."""
        return None

    def save(self) -> None:
        # Managed by Milvus server.
        """Run save."""
        return None

    def reset(self, *, dims: Optional[int] = None) -> None:
        """Run reset."""
        with self._lock:
            if self._has_collection():
                try:
                    self._client.drop_collection(collection_name=self._collection)
                except Exception:
                    pass
            self._dims = int(dims) if dims is not None else None
            if self._dims is not None and self._dims > 0:
                self._ensure_collection(int(self._dims))

    def _has_collection(self) -> bool:
        """Run has collection."""
        try:
            return bool(self._client.has_collection(collection_name=self._collection))
        except Exception:
            try:
                return bool(self._client.has_collection(self._collection))
            except Exception:
                return False

    def _ensure_collection(self, dims: int) -> None:
        """Run ensure collection."""
        d = int(dims)
        if d <= 0:
            return
        if self._dims is None:
            self._dims = d
        elif int(self._dims) != d:
            self.reset(dims=d)
            return

        if self._has_collection():
            return
        # Keep schema creation minimal for cross-version compatibility.
        try:
            self._client.create_collection(
                collection_name=self._collection,
                dimension=d,
                metric_type=self._metric,
            )
        except Exception:
            # Retry with required explicit kwargs in some deployments.
            self._client.create_collection(
                collection_name=self._collection,
                dimension=d,
                metric_type=self._metric,
                auto_id=False,
            )

    def _get_rows(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Run get rows."""
        try:
            out = self._client.get(
                collection_name=self._collection,
                ids=ids,
                output_fields=["vector", "embedding"],
            )
        except Exception:
            try:
                out = self._client.get(collection_name=self._collection, ids=ids)
            except Exception:
                return []
        if not isinstance(out, list):
            return []
        return [row for row in out if isinstance(row, dict)]

