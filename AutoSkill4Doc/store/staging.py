"""
Canonical-merge staging helpers for AutoSkill4Doc.

The current implementation uses staging as a stable filesystem record of one
document-build batch so canonical-merge style commands can inspect or re-run the
same candidate set without rereading the original documents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import re
import uuid
from typing import Any, Dict, Iterable, List, Optional, Sequence

from ..models import SkillSpec
from .layout import normalize_library_root, safe_dir_component, staging_root

_RUN_ID_RE = re.compile(r"[^A-Za-z0-9_\-]+")
_DEFAULT_PROFILE_ID = "document_profile"


@dataclass
class StagingRunSummary:
    """Compact summary for one written or loaded staging run."""

    profile_id: str
    family_id: str
    child_type: str
    run_id: str
    run_dir: str
    files: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSON-safe summary payload."""

        return {
            "profile_id": self.profile_id,
            "family_id": self.family_id,
            "child_type": self.child_type,
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "files": list(self.files or []),
        }


def new_staging_run_id() -> str:
    """Creates a stable human-readable staging run id."""

    return f"{datetime.now().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:8]}"


def safe_run_id(run_id: str = "") -> str:
    """Normalizes one staging run id into a filesystem-safe value."""

    raw = str(run_id or "").strip()
    if not raw:
        return new_staging_run_id()
    cleaned = _RUN_ID_RE.sub("_", raw).strip("_")
    return cleaned or new_staging_run_id()


def document_merge_staging_root(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
) -> str:
    """Returns the staging root for one profile/family/child-type bucket."""

    return os.path.join(
        staging_root(normalize_library_root(base_store_root)),
        safe_dir_component(profile_id or _DEFAULT_PROFILE_ID),
        safe_dir_component(family_id or "unknown_family"),
        safe_dir_component(child_type or "general_child"),
    )


def document_merge_run_dir(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
    run_id: str,
) -> str:
    """Returns the directory for one specific staging run."""

    return os.path.join(
        document_merge_staging_root(
            base_store_root=base_store_root,
            profile_id=profile_id,
            family_id=family_id,
            child_type=child_type,
        ),
        safe_run_id(run_id),
    )


def write_run_payload(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
    run_id: str,
    name: str,
    payload: Any,
) -> str:
    """Writes one JSON payload into a staging run directory."""

    run_dir = document_merge_run_dir(
        base_store_root=base_store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
        run_id=run_id,
    )
    os.makedirs(run_dir, exist_ok=True)
    filename = str(name or "").strip() or "payload"
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    path = os.path.join(run_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=False)
    return path


def read_run_payload(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
    run_id: str,
    name: str,
) -> Optional[Dict[str, Any]]:
    """Loads one JSON payload from a staging run directory."""

    filename = str(name or "").strip() or "payload"
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    path = os.path.join(
        document_merge_run_dir(
            base_store_root=base_store_root,
            profile_id=profile_id,
            family_id=family_id,
            child_type=child_type,
            run_id=run_id,
        ),
        filename,
    )
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def list_child_types(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
) -> List[str]:
    """Lists all staged child types for one profile/family bucket."""

    root = os.path.join(
        staging_root(normalize_library_root(base_store_root)),
        safe_dir_component(profile_id or _DEFAULT_PROFILE_ID),
        safe_dir_component(family_id or "unknown_family"),
    )
    if not os.path.isdir(root):
        return []
    return [name for name in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, name))]


def list_run_ids(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
) -> List[str]:
    """Lists all run ids under one staging bucket."""

    root = document_merge_staging_root(
        base_store_root=base_store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
    )
    if not os.path.isdir(root):
        return []
    return [name for name in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, name))]


def latest_run_id(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
) -> str:
    """Returns the most recent run id for one staging bucket."""

    runs = list_run_ids(
        base_store_root=base_store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
    )
    if not runs:
        return ""
    runs_sorted = sorted(
        runs,
        key=lambda run: os.path.getmtime(
            document_merge_run_dir(
                base_store_root=base_store_root,
                profile_id=profile_id,
                family_id=family_id,
                child_type=child_type,
                run_id=run,
            )
        ),
        reverse=True,
    )
    return str(runs_sorted[0] or "")


def _read_json_file(path: str) -> Optional[Dict[str, Any]]:
    """Loads one JSON object from disk, returning None on malformed files."""

    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _bucket_metadata_from_run_dir(run_dir: str) -> Dict[str, str]:
    """Extracts raw profile/family/child identifiers from one staging run directory."""

    for filename in ("bucket.json", "canonical_results.json", "raw_candidates.json", "existing_active.json"):
        payload = _read_json_file(os.path.join(run_dir, filename)) or {}
        profile_id = str(payload.get("profile_id") or "").strip()
        family_id = str(payload.get("family_id") or "").strip()
        child_type = str(payload.get("child_type") or "").strip()
        if profile_id or family_id or child_type:
            return {
                "profile_id": profile_id,
                "family_id": family_id,
                "child_type": child_type,
            }
        for bucket_name in ("skills", "documents", "support_records"):
            for item in list(payload.get(bucket_name) or []):
                if not isinstance(item, dict):
                    continue
                metadata = dict(item.get("metadata") or {})
                profile_id = str(metadata.get("profile_id") or item.get("profile_id") or "").strip()
                family_id = str(
                    metadata.get("family_name")
                    or metadata.get("school_name")
                    or item.get("family_id")
                    or item.get("family_name")
                    or item.get("school_name")
                    or ""
                ).strip()
                child_type = str(metadata.get("child_type") or item.get("child_type") or "").strip()
                if profile_id or family_id or child_type:
                    return {
                        "profile_id": profile_id,
                        "family_id": family_id,
                        "child_type": child_type,
                    }
    return {}


def discover_staging_buckets(
    *,
    base_store_root: str,
    profile_id: str = "",
    family_id: str = "",
    child_type: str = "",
) -> List[Dict[str, str]]:
    """Scans staging directories and returns discovered bucket identities."""

    root = staging_root(normalize_library_root(base_store_root))
    if not os.path.isdir(root):
        return []

    want_profile = safe_dir_component(profile_id) if str(profile_id or "").strip() else ""
    want_family = safe_dir_component(family_id) if str(family_id or "").strip() else ""
    want_child = safe_dir_component(child_type) if str(child_type or "").strip() else ""

    buckets: List[Dict[str, str]] = []
    for profile_dir in sorted(os.listdir(root)):
        if want_profile and profile_dir != want_profile:
            continue
        profile_path = os.path.join(root, profile_dir)
        if not os.path.isdir(profile_path):
            continue
        for family_dir in sorted(os.listdir(profile_path)):
            if want_family and family_dir != want_family:
                continue
            family_path = os.path.join(profile_path, family_dir)
            if not os.path.isdir(family_path):
                continue
            for child_dir in sorted(os.listdir(family_path)):
                if want_child and child_dir != want_child:
                    continue
                child_path = os.path.join(family_path, child_dir)
                if not os.path.isdir(child_path):
                    continue
                run_ids = [name for name in sorted(os.listdir(child_path)) if os.path.isdir(os.path.join(child_path, name))]
                if not run_ids:
                    continue
                latest = sorted(run_ids, key=lambda run: os.path.getmtime(os.path.join(child_path, run)), reverse=True)[0]
                meta = _bucket_metadata_from_run_dir(os.path.join(child_path, latest))
                buckets.append(
                    {
                        "profile_id": str(meta.get("profile_id") or profile_dir).strip(),
                        "family_id": str(meta.get("family_id") or family_dir).strip(),
                        "child_type": str(meta.get("child_type") or child_dir).strip(),
                        "run_id": str(latest or "").strip(),
                    }
                )
    return buckets


def resolve_staging_bucket_context(
    *,
    base_store_root: str,
    profile_id: str = "",
    family_id: str = "",
    child_type: str = "",
) -> Dict[str, Any]:
    """Attempts to resolve one unique profile/family/child bucket from staging."""

    buckets = discover_staging_buckets(
        base_store_root=base_store_root,
        profile_id=profile_id,
        family_id=family_id,
        child_type=child_type,
    )
    if not buckets:
        return {
            "profile_id": str(profile_id or "").strip() or None,
            "family_id": str(family_id or "").strip() or None,
            "child_type": str(child_type or "").strip() or None,
            "run_id": None,
            "resolved": False,
            "ambiguous": False,
            "candidates": [],
        }

    profiles = sorted({str(item.get("profile_id") or "").strip() for item in buckets if str(item.get("profile_id") or "").strip()})
    families = sorted({str(item.get("family_id") or "").strip() for item in buckets if str(item.get("family_id") or "").strip()})
    child_types = sorted({str(item.get("child_type") or "").strip() for item in buckets if str(item.get("child_type") or "").strip()})
    resolved_profile = str(profile_id or "").strip() or (profiles[0] if len(profiles) == 1 else "")
    narrowed = [
        item
        for item in buckets
        if (not resolved_profile or str(item.get("profile_id") or "").strip() == resolved_profile)
    ]
    families_narrow = sorted({str(item.get("family_id") or "").strip() for item in narrowed if str(item.get("family_id") or "").strip()})
    resolved_family = str(family_id or "").strip() or (families_narrow[0] if len(families_narrow) == 1 else "")
    narrowed = [
        item
        for item in narrowed
        if (not resolved_family or str(item.get("family_id") or "").strip() == resolved_family)
    ]
    child_types_narrow = sorted({str(item.get("child_type") or "").strip() for item in narrowed if str(item.get("child_type") or "").strip()})
    resolved_child = str(child_type or "").strip() or (child_types_narrow[0] if len(child_types_narrow) == 1 else "")
    narrowed = [
        item
        for item in narrowed
        if (not resolved_child or str(item.get("child_type") or "").strip() == resolved_child)
    ]
    latest = ""
    if len(narrowed) == 1:
        latest = str(narrowed[0].get("run_id") or "").strip()
    return {
        "profile_id": resolved_profile or None,
        "family_id": resolved_family or None,
        "child_type": resolved_child or None,
        "run_id": latest or None,
        "resolved": bool(resolved_profile and resolved_family and resolved_child),
        "ambiguous": len(narrowed) > 1 or not (resolved_profile and resolved_family and resolved_child),
        "candidates": narrowed or buckets,
    }


def write_registration_staging(
    *,
    base_store_root: str,
    profile_id: str,
    family_id: str,
    child_type: str,
    run_id: str,
    documents: Sequence[Dict[str, Any]],
    support_records: Sequence[Dict[str, Any]],
    raw_candidates: Sequence[Dict[str, Any]],
    existing_active: Sequence[Dict[str, Any]],
    canonical_results: Sequence[Dict[str, Any]],
    change_logs: Sequence[Dict[str, Any]],
) -> StagingRunSummary:
    """Writes a standard set of staging payloads for one registration batch."""

    resolved_run_id = safe_run_id(run_id)
    written: List[str] = []
    files = {
        "bucket": {
            "schema": "autoskill.document.staging.bucket.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
        },
        "raw_candidates": {
            "schema": "autoskill.document.staging.raw_candidates.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
            "documents": list(documents or []),
            "support_records": list(support_records or []),
            "skills": list(raw_candidates or []),
        },
        "existing_active": {
            "schema": "autoskill.document.staging.existing_active.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
            "skills": list(existing_active or []),
        },
        "shortlists": {
            "schema": "autoskill.document.staging.shortlists.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
            "items": [],
        },
        "merge_decisions": {
            "schema": "autoskill.document.staging.merge_decisions.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
            "items": [],
        },
        "clusters": {
            "schema": "autoskill.document.staging.clusters.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
            "items": [],
        },
        "canonical_results": {
            "schema": "autoskill.document.staging.canonical_results.v1",
            "profile_id": str(profile_id or _DEFAULT_PROFILE_ID),
            "family_id": str(family_id or "unknown_family"),
            "child_type": str(child_type or "general_child"),
            "run_id": resolved_run_id,
            "skills": list(canonical_results or []),
            "change_logs": list(change_logs or []),
        },
    }
    for name, payload in files.items():
        written.append(
            write_run_payload(
                base_store_root=base_store_root,
                profile_id=profile_id,
                family_id=family_id,
                child_type=child_type,
                run_id=resolved_run_id,
                name=name,
                payload=payload,
            )
        )
    return StagingRunSummary(
        profile_id=str(profile_id or _DEFAULT_PROFILE_ID),
        family_id=str(family_id or "unknown_family"),
        child_type=str(child_type or "general_child"),
        run_id=resolved_run_id,
        run_dir=document_merge_run_dir(
            base_store_root=base_store_root,
            profile_id=profile_id,
            family_id=family_id,
            child_type=child_type,
            run_id=resolved_run_id,
        ),
        files=written,
    )


def group_skills_by_staging_bucket(
    *,
    skills: Sequence[SkillSpec],
    profile_id: str,
) -> Dict[str, List[SkillSpec]]:
    """Groups skills into stable `family_id::child_type` staging buckets."""

    out: Dict[str, List[SkillSpec]] = {}
    for skill in skills or []:
        metadata = dict(skill.metadata or {})
        family_id = str(
            metadata.get("family_name")
            or metadata.get("school_name")
            or metadata.get("taxonomy_class")
            or skill.domain
            or skill.method_family
            or "unknown_family"
        ).strip()
        child_type = str(metadata.get("child_type") or skill.task_family or skill.asset_type or "general_child").strip()
        key = f"{safe_dir_component(profile_id or _DEFAULT_PROFILE_ID)}::{safe_dir_component(family_id)}::{safe_dir_component(child_type)}"
        out.setdefault(key, []).append(skill)
    return out


def plain_skill_specs(skills: Iterable[SkillSpec]) -> List[Dict[str, Any]]:
    """Serializes a list of SkillSpec objects for staging payloads."""

    return [skill.to_dict() for skill in list(skills or [])]
