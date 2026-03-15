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
        "raw_candidates": {
            "schema": "autoskill.document.staging.raw_candidates.v1",
            "documents": list(documents or []),
            "support_records": list(support_records or []),
            "skills": list(raw_candidates or []),
        },
        "existing_active": {
            "schema": "autoskill.document.staging.existing_active.v1",
            "skills": list(existing_active or []),
        },
        "shortlists": {
            "schema": "autoskill.document.staging.shortlists.v1",
            "items": [],
        },
        "merge_decisions": {
            "schema": "autoskill.document.staging.merge_decisions.v1",
            "items": [],
        },
        "clusters": {
            "schema": "autoskill.document.staging.clusters.v1",
            "items": [],
        },
        "canonical_results": {
            "schema": "autoskill.document.staging.canonical_results.v1",
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
