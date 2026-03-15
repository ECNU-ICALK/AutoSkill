"""
Minimal canonical-merge helpers backed by staging payloads.

The current pipeline already performs version registration during `build`. This
module exposes a small staging-centric view so users can inspect the most recent
canonicalized results for one profile/family/child-type bucket, similar to the
older standalone document pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..store.staging import latest_run_id, read_run_payload


def canonical_merge_from_staging(
    *,
    store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
    run_id: str = "",
) -> Dict[str, Any]:
    """Loads the latest staged canonical results for one bucket."""

    resolved_run_id = str(run_id or "").strip() or latest_run_id(
        base_store_root=store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
    )
    if not resolved_run_id:
        return {
            "route": "canonical_merge",
            "profile_id": profile_id or None,
            "family_id": family_id or None,
            "child_type": child_type or None,
            "run_id": None,
            "skills": [],
            "change_logs": [],
            "errors": [{"stage": "canonical_merge", "error": "no staged runs found"}],
        }

    canonical = read_run_payload(
        base_store_root=store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
        run_id=resolved_run_id,
        name="canonical_results",
    ) or {}
    raw_candidates = read_run_payload(
        base_store_root=store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
        run_id=resolved_run_id,
        name="raw_candidates",
    ) or {}
    existing_active = read_run_payload(
        base_store_root=store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
        run_id=resolved_run_id,
        name="existing_active",
    ) or {}

    return {
        "route": "canonical_merge",
        "profile_id": profile_id or None,
        "family_id": family_id or None,
        "child_type": child_type or None,
        "run_id": resolved_run_id,
        "skills": list(canonical.get("skills") or []),
        "change_logs": list(canonical.get("change_logs") or []),
        "raw_candidates": list(raw_candidates.get("skills") or []),
        "existing_active": list(existing_active.get("skills") or []),
        "errors": [],
    }


def available_merge_child_types(
    *,
    store_root: str,
    profile_id: str,
    family_id: str,
    child_types: List[str],
) -> Dict[str, Any]:
    """Builds a compact summary of available staging buckets for one family."""

    return {
        "route": "canonical_merge_buckets",
        "profile_id": profile_id or None,
        "family_id": family_id or None,
        "child_types": list(child_types or []),
        "errors": [],
    }
