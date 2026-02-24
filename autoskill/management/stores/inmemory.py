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
from .base import SkillStore


def _cosine(a: List[float], b: List[float]) -> float:
    # Assumes vectors are normalized; dot product can be used as cosine similarity.
    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(x * y for x, y in zip(a, b)))


def _skill_to_text(skill: Skill) -> str:
    # Use structured fields to keep vectors stable across versions/ids and avoid
    # coupling similarity to artifact frontmatter formatting.
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
    vector: List[float]
    raw: Optional[Dict[str, Any]] = None


class InMemorySkillStore(SkillStore):
    def __init__(self, *, embeddings: EmbeddingModel) -> None:
        self._embeddings = embeddings
        self._lock = threading.RLock()
        self._records: Dict[str, _Record] = {}

    def upsert(self, skill: Skill, *, raw: Optional[Dict[str, Any]] = None) -> None:
        text = _skill_to_text(skill)
        vector = self._embeddings.embed([text])[0]
        with self._lock:
            self._records[skill.id] = _Record(skill=skill, vector=vector, raw=raw)

    def get(self, skill_id: str) -> Optional[Skill]:
        with self._lock:
            rec = self._records.get(skill_id)
            return rec.skill if rec else None

    def delete(self, skill_id: str) -> bool:
        with self._lock:
            return self._records.pop(skill_id, None) is not None

    def list(self, *, user_id: str) -> List[Skill]:
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
        qvec = self._embeddings.embed([query])[0]
        with self._lock:
            candidates: List[Tuple[float, Skill]] = []
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
                score = _cosine(qvec, rec.vector)
                candidates.append((score, skill))

        candidates.sort(key=lambda x: x[0], reverse=True)
        hits = [SkillHit(skill=s, score=float(sc)) for sc, s in candidates[:limit]]
        return hits


def _passes_filters(skill: Skill, filters: Dict[str, Any]) -> bool:
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
