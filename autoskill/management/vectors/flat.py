"""
Flat (exact) persistent vector index.

This index is dependency-free and optimized for fast load/save and predictable behavior.
It stores vectors as float32 in a single binary file with an accompanying ID list.

File layout (inside a directory):
- <name>.meta.json   {"version": 1, "dims": 256, "count": 123, "dtype": "float32"}
- <name>.ids.txt     one key per line (Skill ID)
- <name>.vecs.f32    float32 vectors, row-major, length = count * dims
"""

from __future__ import annotations

import json
import os
import threading
from array import array
from typing import Iterable, List, Optional, Sequence, Tuple

from .base import VectorIndex


def _dot(q: Sequence[float], vecs: array, *, offset: int, dims: int) -> float:
    s = 0.0
    for i in range(dims):
        s += q[i] * vecs[offset + i]
    return float(s)


class FlatFileVectorIndex(VectorIndex):
    def __init__(self, *, dir_path: str, name: str = "skills") -> None:
        """Initializes index paths and loads existing on-disk data if present."""

        self._dir = os.path.abspath(os.path.expanduser(str(dir_path)))
        self._name = str(name or "skills").strip() or "skills"

        self._meta_path = os.path.join(self._dir, f"{self._name}.meta.json")
        self._ids_path = os.path.join(self._dir, f"{self._name}.ids.txt")
        self._vecs_path = os.path.join(self._dir, f"{self._name}.vecs.f32")

        self._lock = threading.RLock()
        self._dims: Optional[int] = None
        self._ids: List[str] = []
        self._id_to_pos: dict[str, int] = {}
        self._vecs: array = array("f")

        os.makedirs(self._dir, exist_ok=True)
        self.load()

    @property
    def dims(self) -> Optional[int]:
        """Returns current embedding dimension, or None for empty index."""

        return self._dims

    def has(self, key: str) -> bool:
        """Checks whether a vector exists for the given key."""

        k = str(key or "").strip()
        if not k:
            return False
        with self._lock:
            return k in self._id_to_pos

    def ids(self) -> List[str]:
        """Returns all indexed keys (best-effort helper for maintenance sync)."""

        with self._lock:
            return list(self._ids)

    def get(self, key: str) -> Optional[List[float]]:
        """Returns one vector by key, or None when key/dims are missing."""

        k = str(key or "").strip()
        if not k:
            return None
        with self._lock:
            pos = self._id_to_pos.get(k)
            if pos is None or self._dims is None:
                return None
            d = int(self._dims)
            start = pos * d
            return [float(x) for x in self._vecs[start : start + d]]

    def upsert(self, key: str, vector: Sequence[float]) -> None:
        """Upserts one vector row; auto-resets index when dims change."""

        k = str(key or "").strip()
        if not k:
            return
        vec = [float(x) for x in (vector or [])]
        if not vec:
            return

        with self._lock:
            self._ensure_dims(len(vec))
            d = int(self._dims or 0)
            if d <= 0:
                return

            arr = array("f", vec)
            pos = self._id_to_pos.get(k)
            if pos is None:
                pos = len(self._ids)
                self._ids.append(k)
                self._id_to_pos[k] = pos
                self._vecs.extend(arr)
                return

            start = pos * d
            self._vecs[start : start + d] = arr

    def delete(self, key: str) -> bool:
        """Deletes one key using swap-with-last for O(1) compaction."""

        k = str(key or "").strip()
        if not k:
            return False
        with self._lock:
            pos = self._id_to_pos.get(k)
            if pos is None or self._dims is None:
                return False

            d = int(self._dims)
            last_pos = len(self._ids) - 1
            if last_pos < 0:
                return False

            last_id = self._ids[last_pos]
            last_start = last_pos * d
            if pos != last_pos:
                start = pos * d
                self._vecs[start : start + d] = self._vecs[last_start : last_start + d]
                self._ids[pos] = last_id
                self._id_to_pos[last_id] = pos

            del self._ids[last_pos]
            del self._id_to_pos[k]
            del self._vecs[last_start : last_start + d]
            return True

    def search(
        self,
        query_vector: Sequence[float],
        *,
        keys: Optional[Iterable[str]] = None,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Exact dot-product search.

        When `keys` is provided, search is restricted to that subset.
        """

        k = max(0, int(top_k))
        if k == 0:
            return []

        q = [float(x) for x in (query_vector or [])]
        if not q:
            return []

        with self._lock:
            d = int(self._dims or 0)
            if d <= 0 or len(q) != d:
                return []

            # Maintain a small min-heap of (score, id).
            import heapq

            heap: List[Tuple[float, str]] = []

            if keys is None:
                for pos, sid in enumerate(self._ids):
                    off = pos * d
                    score = _dot(q, self._vecs, offset=off, dims=d)
                    if len(heap) < k:
                        heapq.heappush(heap, (score, sid))
                    elif score > heap[0][0]:
                        heapq.heapreplace(heap, (score, sid))
            else:
                for sid in keys:
                    sid_s = str(sid or "").strip()
                    if not sid_s:
                        continue
                    pos = self._id_to_pos.get(sid_s)
                    if pos is None:
                        continue
                    off = pos * d
                    score = _dot(q, self._vecs, offset=off, dims=d)
                    if len(heap) < k:
                        heapq.heappush(heap, (score, sid_s))
                    elif score > heap[0][0]:
                        heapq.heapreplace(heap, (score, sid_s))

            heap.sort(key=lambda x: x[0], reverse=True)
            return [(sid, float(score)) for score, sid in heap]

    def reset(self, *, dims: Optional[int] = None) -> None:
        """Clears all vectors and optionally pins a new target dimension."""

        with self._lock:
            self._dims = int(dims) if dims is not None else None
            self._ids = []
            self._id_to_pos = {}
            self._vecs = array("f")

    def load(self) -> None:
        """Loads index files from disk; silently keeps empty state on corruption."""

        with self._lock:
            if not os.path.isfile(self._meta_path) or not os.path.isfile(self._ids_path) or not os.path.isfile(self._vecs_path):
                return

            try:
                meta = _read_json(self._meta_path)
                dims = int(meta.get("dims") or 0)
                if dims <= 0:
                    return
                ids = _read_lines(self._ids_path)
                want_count = len(ids) * dims

                vecs = array("f")
                with open(self._vecs_path, "rb") as f:
                    vecs.fromfile(f, want_count)
                if len(vecs) != want_count:
                    return

                self._dims = dims
                self._ids = ids
                self._id_to_pos = {sid: i for i, sid in enumerate(ids) if sid}
                self._vecs = vecs
            except Exception:
                # Treat any parse error as a corrupt cache; keep empty state.
                return

    def save(self) -> None:
        """Atomically persists meta/ids/vectors files to disk."""

        with self._lock:
            if self._dims is None:
                return
            dims = int(self._dims)
            if dims <= 0:
                return

            meta = {"version": 1, "dims": dims, "count": len(self._ids), "dtype": "float32"}
            _atomic_write_json(self._meta_path, meta)
            _atomic_write_lines(self._ids_path, self._ids)
            _atomic_write_vecs(self._vecs_path, self._vecs)

    def _ensure_dims(self, dims: int) -> None:
        """Ensures index dimension consistency, resetting when model dims changed."""

        d = int(dims)
        if d <= 0:
            return
        if self._dims is None:
            self._dims = d
            return
        if int(self._dims) != d:
            # Embedding dimension changed; clear the index and start fresh.
            self.reset(dims=d)


def _read_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.loads(f.read())
    return obj if isinstance(obj, dict) else {}


def _read_lines(path: str) -> List[str]:
    out: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                out.append(s)
    return out


def _atomic_write_json(path: str, obj: dict) -> None:
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False))
    os.replace(tmp, path)


def _atomic_write_lines(path: str, lines: List[str]) -> None:
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        for s in lines:
            if s:
                f.write(str(s).strip() + "\n")
    os.replace(tmp, path)


def _atomic_write_vecs(path: str, vecs: array) -> None:
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "wb") as f:
        vecs.tofile(f)
    os.replace(tmp, path)
