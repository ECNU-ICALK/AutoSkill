"""
Hybrid retrieval helpers for document-skill maintenance.

This module reuses AutoSkill's low-level embedding + BM25 ranking primitives, but
builds a document-pipeline-specific retrieval text that includes execution
metadata such as asset layer, domain type, family, stage, and workflow fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

from autoskill.embeddings.base import EmbeddingModel
from autoskill.embeddings.factory import build_embeddings
from autoskill.management.stores.hybrid_rank import blend_scores, bm25_normalized_scores

from ..core.common import dedupe_strings, normalize_text
from ..models import SkillSpec

DEFAULT_RETRIEVAL_LIMIT = 8
DEFAULT_BM25_WEIGHT = 0.1


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Returns a cosine-ready dot product for normalized vectors."""

    if not a or not b or len(a) != len(b):
        return 0.0
    return float(sum(float(x) * float(y) for x, y in zip(a, b)))


def _granularity_rank(value: str) -> int:
    """Maps granularity labels into a stable coarse-to-fine rank."""

    raw = str(value or "").strip().lower()
    if raw == "macro":
        return 0
    if raw == "micro":
        return 2
    return 1


def _metadata_value(skill: SkillSpec, key: str) -> str:
    """Reads one string metadata field from a skill spec."""

    return str((skill.metadata or {}).get(key) or "").strip()


def _family_name(skill: SkillSpec) -> str:
    """Returns the normalized family label for one skill."""

    return _metadata_value(skill, "family_name") or _metadata_value(skill, "school_name")


def _domain_type(skill: SkillSpec) -> str:
    """Returns the configured domain type for one skill."""

    return _metadata_value(skill, "domain_type")


def _taxonomy_id(skill: SkillSpec) -> str:
    """Returns the taxonomy id for one skill."""

    return _metadata_value(skill, "taxonomy_id")


def _profile_id(skill: SkillSpec) -> str:
    """Returns the configured profile id for one skill."""

    return _metadata_value(skill, "profile_id")


def skill_retrieval_text(skill: SkillSpec) -> str:
    """Builds one retrieval text that includes execution fields plus metadata."""

    family_name = _family_name(skill)
    lines: List[str] = [
        f"Name: {str(skill.name or '').strip()}",
        f"Description: {str(skill.description or '').strip()}",
        f"Objective: {str(skill.objective or '').strip()}",
        f"Asset Type: {str(skill.asset_type or '').strip()}",
        f"Granularity: {str(skill.granularity or '').strip()}",
        f"Domain: {str(skill.domain or '').strip()}",
        f"Domain Type: {_domain_type(skill)}",
        f"Taxonomy ID: {_taxonomy_id(skill)}",
        f"Profile ID: {_profile_id(skill)}",
        f"Family: {family_name}",
        f"Task Family: {str(skill.task_family or '').strip()}",
        f"Method Family: {str(skill.method_family or '').strip()}",
        f"Stage: {str(skill.stage or '').strip()}",
    ]

    def add_block(title: str, values: Iterable[str]) -> None:
        items = dedupe_strings([str(value or "").strip() for value in values if str(value or "").strip()])
        if not items:
            return
        lines.append(f"{title}: {' | '.join(items)}")

    add_block("Applicable Signals", list(skill.applicable_signals or []))
    add_block("Contraindications", list(skill.contraindications or []))
    add_block("Intervention Moves", list(skill.intervention_moves or []))
    add_block("Workflow Steps", list(skill.workflow_steps or []))
    add_block("Constraints", list(skill.constraints or []))
    add_block("Cautions", list(skill.cautions or []))
    add_block("Output Contract", list(skill.output_contract or []))
    add_block("Triggers", list(skill.triggers or []))
    add_block("Tags", list(skill.tags or []))
    return "\n".join(line for line in lines if str(line or "").strip()).strip()


@dataclass(frozen=True)
class SkillRetrievalHit:
    """One ranked similar-skill hit returned by the document retriever."""

    skill: SkillSpec
    score: float
    vector_score: float
    bm25_score: float


class DocumentSkillRetriever:
    """Mutable hybrid retriever used by AutoSkill4Doc version maintenance."""

    def __init__(
        self,
        *,
        embeddings: Optional[EmbeddingModel],
        bm25_weight: float = DEFAULT_BM25_WEIGHT,
    ) -> None:
        self._embeddings = embeddings
        self._bm25_weight = float(bm25_weight)
        self._skills: Dict[str, SkillSpec] = {}
        self._texts: Dict[str, str] = {}
        self._vectors: Dict[str, List[float]] = {}
        self._vectors_available = embeddings is not None and not bool(getattr(embeddings, "disabled", False))

    def refresh(self, skills: Sequence[SkillSpec]) -> None:
        """Rebuilds the retriever corpus from a skill sequence."""

        self._skills = {}
        self._texts = {}
        self._vectors = {}
        ordered_ids: List[str] = []
        for skill in list(skills or []):
            skill_id = str(skill.skill_id or "").strip()
            if not skill_id:
                continue
            self._skills[skill_id] = skill
            self._texts[skill_id] = skill_retrieval_text(skill)
            ordered_ids.append(skill_id)

        if not self._vectors_available or not ordered_ids:
            return
        try:
            embedded = self._embeddings.embed([self._texts[skill_id] for skill_id in ordered_ids])
            self._vectors = {
                skill_id: [float(x) for x in list(vec or [])]
                for skill_id, vec in zip(ordered_ids, embedded)
                if vec
            }
        except Exception:
            self._vectors_available = False
            self._vectors = {}

    def upsert(self, skill: SkillSpec) -> None:
        """Adds or replaces one skill in the retrieval corpus."""

        skill_id = str(skill.skill_id or "").strip()
        if not skill_id:
            return
        self._skills[skill_id] = skill
        text = skill_retrieval_text(skill)
        self._texts[skill_id] = text
        if not self._vectors_available:
            return
        try:
            embedded = self._embeddings.embed([text])[0]
            self._vectors[skill_id] = [float(x) for x in list(embedded or [])]
        except Exception:
            self._vectors_available = False
            self._vectors = {}

    def remove(self, skill_id: str) -> None:
        """Removes one skill from the retrieval corpus."""

        skill_id_s = str(skill_id or "").strip()
        if not skill_id_s:
            return
        self._skills.pop(skill_id_s, None)
        self._texts.pop(skill_id_s, None)
        self._vectors.pop(skill_id_s, None)

    def search(
        self,
        candidate: SkillSpec,
        *,
        limit: int = DEFAULT_RETRIEVAL_LIMIT,
        exclude_ids: Optional[Iterable[str]] = None,
    ) -> List[SkillRetrievalHit]:
        """Returns top-k similar skills from the current corpus."""

        excluded = {str(item or "").strip() for item in list(exclude_ids or []) if str(item or "").strip()}
        pool: List[SkillSpec] = []
        candidate_domain = normalize_text(candidate.domain, lower=True)
        candidate_domain_type = normalize_text(_domain_type(candidate), lower=True)
        candidate_taxonomy_id = normalize_text(_taxonomy_id(candidate), lower=True)
        candidate_profile_id = normalize_text(_profile_id(candidate), lower=True)
        candidate_family = normalize_text(_family_name(candidate), lower=True)

        for skill in self._skills.values():
            skill_id = str(skill.skill_id or "").strip()
            if not skill_id or skill_id in excluded:
                continue
            skill_domain = normalize_text(skill.domain, lower=True)
            if candidate_domain and skill_domain and skill_domain != candidate_domain:
                continue
            skill_domain_type = normalize_text(_domain_type(skill), lower=True)
            if candidate_domain_type and skill_domain_type and skill_domain_type != candidate_domain_type:
                continue
            skill_taxonomy_id = normalize_text(_taxonomy_id(skill), lower=True)
            if candidate_taxonomy_id and skill_taxonomy_id and skill_taxonomy_id != candidate_taxonomy_id:
                continue
            skill_profile_id = normalize_text(_profile_id(skill), lower=True)
            if candidate_profile_id and skill_profile_id and skill_profile_id != candidate_profile_id:
                continue
            skill_family = normalize_text(_family_name(skill), lower=True)
            if candidate_family and skill_family and skill_family != candidate_family:
                continue
            pool.append(skill)

        if not pool:
            return []

        query = skill_retrieval_text(candidate)
        docs = {skill.skill_id: self._texts.get(skill.skill_id) or skill_retrieval_text(skill) for skill in pool}
        bm25_scores = bm25_normalized_scores(query=query, docs=docs)

        vector_scores: Dict[str, float] = {}
        use_vector = False
        if self._vectors_available:
            try:
                qvec = self._embeddings.embed([query])[0]
                qvec = [float(x) for x in list(qvec or [])]
                use_vector = bool(qvec)
            except Exception:
                use_vector = False
                qvec = []
            if use_vector:
                for skill in pool:
                    skill_id = str(skill.skill_id or "").strip()
                    vec = self._vectors.get(skill_id)
                    if not vec:
                        continue
                    vector_scores[skill_id] = _dot(qvec, vec)

        merged = blend_scores(
            vector_scores=vector_scores,
            bm25_scores=bm25_scores,
            bm25_weight=self._bm25_weight,
            use_vector=use_vector,
        )
        def boosted_score(item: SkillSpec) -> float:
            score = float(merged.get(item.skill_id, 0.0))
            if (
                str(item.asset_type or "").strip() == str(candidate.asset_type or "").strip()
                and str(item.granularity or "").strip() == str(candidate.granularity or "").strip()
            ):
                score += 0.15
            elif _granularity_rank(item.granularity) < _granularity_rank(candidate.granularity):
                # Keep broader parent skills available for split detection.
                score += 0.05
            return score

        ranked = sorted(pool, key=boosted_score, reverse=True)
        hits: List[SkillRetrievalHit] = []
        for skill in ranked[: max(1, int(limit or DEFAULT_RETRIEVAL_LIMIT))]:
            skill_id = str(skill.skill_id or "").strip()
            hits.append(
                SkillRetrievalHit(
                    skill=skill,
                    score=float(boosted_score(skill)),
                    vector_score=float(vector_scores.get(skill_id, 0.0)),
                    bm25_score=float(bm25_scores.get(skill_id, 0.0)),
                )
            )
        return hits


def build_document_skill_retriever(
    *,
    embeddings_config: Optional[Dict[str, Any]] = None,
    bm25_weight: float = DEFAULT_BM25_WEIGHT,
) -> DocumentSkillRetriever:
    """Builds the document retriever from one embedding config."""

    config = dict(embeddings_config or {})
    if not config:
        config = {"provider": "hashing", "dims": 256}
    embeddings = build_embeddings(config)
    return DocumentSkillRetriever(embeddings=embeddings, bm25_weight=bm25_weight)
