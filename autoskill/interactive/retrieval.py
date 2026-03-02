"""
Shared retrieval helpers for interactive/session/proxy runtimes.

Core behavior:
- when scope is `all`, retrieve user and library scopes independently
- apply threshold per scope
- keep per-scope hit lists for diagnostics
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..client import AutoSkill
from ..models import SkillHit


def normalize_scope(scope: str) -> str:
    """Run normalize scope."""
    s = str(scope or "all").strip().lower()
    if s == "common":
        s = "library"
    if s not in {"all", "user", "library"}:
        s = "all"
    return s


def _score_of(hit: SkillHit) -> float:
    """Run score of."""
    return float(getattr(hit, "score", 0.0) or 0.0)


def _hit_scope_match(hit: SkillHit, *, one_scope: str, user_id: str) -> bool:
    """
    Defensive scope filter.

    Some downstream integrations may return mixed-scope hits even when requesting one scope.
    Keep only hits that strictly match the requested branch.
    """

    skill = getattr(hit, "skill", None)
    owner = str(getattr(skill, "user_id", "") or "").strip()
    if one_scope == "user":
        return owner == str(user_id or "").strip()
    if one_scope == "library":
        return owner.startswith("library:")
    return True


def _filter_by_min_score(hits: List[SkillHit], *, min_score: float) -> List[SkillHit]:
    """Run filter by min score."""
    if not hits or min_score <= 0:
        return list(hits or [])
    out: List[SkillHit] = []
    for h in hits:
        if _score_of(h) >= min_score:
            out.append(h)
    return out


def retrieve_hits_by_scope(
    *,
    sdk: AutoSkill,
    query: str,
    user_id: str,
    scope: str,
    top_k: int,
    min_score: float,
    allow_partial_vectors: bool = False,
) -> Dict[str, Any]:
    """
    Retrieves hits with per-scope semantics.

    Returns:
    - `hits`: merged hit list used for downstream selection/context
    - `hits_user`: user-scope hits after threshold
    - `hits_library`: library-scope hits after threshold
    - `error`: joined error message across retrieval branches (or empty)
    - `errors`: raw error map by scope
    """

    scope_norm = normalize_scope(scope)
    lim = max(1, int(top_k or 1))
    min_score_v = float(min_score or 0.0)

    hits_user: List[SkillHit] = []
    hits_library: List[SkillHit] = []
    errors: Dict[str, str] = {}

    def _search(one_scope: str) -> List[SkillHit]:
        """Run search."""
        try:
            out = sdk.search(
                query,
                user_id=user_id,
                limit=lim,
                filters={
                    "scope": one_scope,
                    "allow_partial_vectors": bool(allow_partial_vectors),
                },
            )
        except Exception as e:
            errors[one_scope] = str(e)
            return []
        scoped: List[SkillHit] = []
        for h in list(out or []):
            if _hit_scope_match(h, one_scope=one_scope, user_id=user_id):
                scoped.append(h)
        return _filter_by_min_score(scoped, min_score=min_score_v)

    if scope_norm == "all":
        hits_user = _search("user")
        hits_library = _search("library")
    elif scope_norm == "user":
        hits_user = _search("user")
    else:
        hits_library = _search("library")

    merged = list(hits_user) + list(hits_library)
    merged.sort(key=_score_of, reverse=True)

    error = "; ".join(
        f"{k}: {v}" for k, v in errors.items() if str(v or "").strip()
    )
    return {
        "scope": scope_norm,
        "hits": merged,
        "hits_user": hits_user,
        "hits_library": hits_library,
        "errors": errors,
        "error": error,
    }
