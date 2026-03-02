"""
InMemorySkillStore: an in-memory “vector database”.

Key points:
- on upsert: embed skill text and store (skill, vector)
- on search: embed query text and rank by dot product (≈ cosine similarity)
- good for demos/single-machine; not suitable for multi-process or large-scale datasets
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ...embeddings.base import EmbeddingModel
from ...models import Skill, SkillHit, SkillStatus
from .hybrid_rank import blend_scores, bm25_normalized_scores
from .base import SkillStore


def _cosine(a: List[float], b: List[float]) -> float:
    # Assumes vectors are normalized; dot product can be used as cosine similarity.
    """Run cosine."""
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(x * y for x, y in zip(a, b)))


def _skill_to_text(skill: Skill) -> str:
    # Use structured fields to keep vectors stable across versions/ids and avoid
    # coupling similarity to artifact frontmatter formatting.
    """Run skill to text."""
    triggers = "\n".join(skill.triggers or [])
    tags = " ".join(skill.tags or [])
    return (
        f"Name: {skill.name}\n"
        f"Description: {skill.description}\n"
        f"Instructions: {skill.instructions}\n"
        f"Triggers:\n{triggers}\n"
        f"Tags: {tags}\n"
    )


@dataclass
class _Record:
    skill: Skill
    vector: Optional[List[float]]
    raw: Optional[Dict[str, Any]] = None


class InMemorySkillStore(SkillStore):
    def __init__(self, *, embeddings: EmbeddingModel, bm25_weight: float = 0.1) -> None:
        """Run init."""
        self._embeddings = embeddings
        self._embedding_disabled = bool(getattr(embeddings, "disabled", False))
        self._bm25_weight = float(bm25_weight)
        if self._bm25_weight < 0.0:
            self._bm25_weight = 0.0
        if self._bm25_weight > 1.0:
            self._bm25_weight = 1.0
        self._lock = threading.RLock()
        self._records: Dict[str, _Record] = {}
        self._bm25_docs_by_id: Dict[str, str] = {}

    def upsert(self, skill: Skill, *, raw: Optional[Dict[str, Any]] = None) -> None:
        """Run upsert."""
        vector: Optional[List[float]] = None
        if not self._embedding_disabled:
            text = _skill_to_text(skill)
            try:
                vector = [float(x) for x in self._embeddings.embed([text])[0]]
            except Exception:
                vector = None
        with self._lock:
            self._records[skill.id] = _Record(skill=skill, vector=vector, raw=raw)
            self._bm25_docs_by_id[str(skill.id)] = _skill_to_text(skill)

    def get(self, skill_id: str) -> Optional[Skill]:
        """Run get."""
        with self._lock:
            rec = self._records.get(skill_id)
            return rec.skill if rec else None

    def delete(self, skill_id: str) -> bool:
        """Run delete."""
        with self._lock:
            removed = self._records.pop(skill_id, None) is not None
            self._bm25_docs_by_id.pop(str(skill_id), None)
            return removed

    def list(self, *, user_id: str) -> List[Skill]:
        """Run list."""
        with self._lock:
            return [
                r.skill
                for r in self._records.values()
                if r.skill.user_id == user_id and r.skill.status != SkillStatus.ARCHIVED
            ]

    def search(
        self,
        *,
        user_id: str,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SkillHit]:
        """Run search."""
        filters = filters or {}
        want_ids_raw = filters.get("ids")
        if want_ids_raw is None:
            want_id_set = None
        else:
            if isinstance(want_ids_raw, (list, tuple, set)):
                want_ids = list(want_ids_raw)
            else:
                want_ids = [want_ids_raw]
            want_id_set = {str(x).strip() for x in want_ids if str(x).strip()} or None
        with self._lock:
            docs_by_id: Dict[str, str] = {}
            recs: List[_Record] = []
            for rec in self._records.values():
                skill = rec.skill
                if skill.user_id != user_id:
                    continue
                if skill.status == SkillStatus.ARCHIVED:
                    continue
                if want_id_set is not None and skill.id not in want_id_set:
                    continue

                if not _passes_filters(skill, filters):
                    continue
                recs.append(rec)
                sid = str(skill.id)
                txt = self._bm25_docs_by_id.get(sid)
                if not txt:
                    txt = _skill_to_text(skill)
                    self._bm25_docs_by_id[sid] = txt
                docs_by_id[sid] = txt

        if not recs:
            return []

        bm25_scores = bm25_normalized_scores(query=query, docs=docs_by_id)

        vector_scores: Dict[str, float] = {}
        use_vector = False
        if not self._embedding_disabled:
            try:
                qvec = self._embeddings.embed([query])[0]
                use_vector = bool(qvec)
            except Exception:
                qvec = []
                use_vector = False
            if use_vector:
                for rec in recs:
                    vec = rec.vector or []
                    if not vec:
                        continue
                    vector_scores[rec.skill.id] = _cosine(qvec, vec)

        merged_scores = blend_scores(
            vector_scores=vector_scores,
            bm25_scores=bm25_scores,
            bm25_weight=self._bm25_weight,
            use_vector=use_vector,
        )

        candidates: List[Tuple[float, Skill]] = []
        for rec in recs:
            sid = rec.skill.id
            candidates.append((float(merged_scores.get(sid, 0.0)), rec.skill))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [SkillHit(skill=s, score=float(sc)) for sc, s in candidates[:limit]]


def _passes_filters(skill: Skill, filters: Dict[str, Any]) -> bool:
    """Run passes filters."""
    want_tags = filters.get("tags")
    if want_tags:
        want_set = {str(t).strip().lower() for t in want_tags if str(t).strip()}
        have_set = {t.strip().lower() for t in (skill.tags or []) if t.strip()}
        if want_set and not (want_set & have_set):
            return False

    want_status = filters.get("status")
    if want_status and str(skill.status.value) != str(want_status):
        return False

    want_meta = filters.get("metadata")
    if isinstance(want_meta, dict):
        for k, v in want_meta.items():
            if skill.metadata.get(k) != v:
                return False

    return True
