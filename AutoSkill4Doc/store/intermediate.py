"""
Intermediate run persistence for AutoSkill4Doc.

Long-running document extraction should expose observable artifacts before the
final registry/store sync completes. This module writes stage snapshots under
`<store_root>/.runtime/intermediate_runs/<run_id>/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from typing import Any, Dict, List, Optional

from autoskill.utils.time import now_iso

from ..ingest import DocumentIngestResult
from ..models import DocumentRecord, SkillDraft, StrictWindow, SupportRecord
from ..stages.compiler import SkillCompilationResult
from ..stages.extractor import SkillExtractionResult
from ..store.versioning import VersionRegistrationResult
from .layout import intermediate_run_dir, normalize_library_root
from .staging import new_staging_run_id, safe_run_id


@dataclass
class IntermediateRunSummary:
    """Compact summary for one intermediate persistence run."""

    run_id: str
    run_dir: str
    status_path: str
    files: List[str] = field(default_factory=list)
    current_stage: str = "initialized"
    completed_stages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Returns a JSON-safe summary payload."""

        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "status_path": self.status_path,
            "files": list(self.files or []),
            "current_stage": self.current_stage,
            "completed_stages": list(self.completed_stages or []),
        }


def new_intermediate_run_id() -> str:
    """Creates a new run id for intermediate persistence."""

    return new_staging_run_id()


class IntermediateRunWriter:
    """Writes incremental stage snapshots for one document build run."""

    def __init__(
        self,
        *,
        base_store_root: str,
        run_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        store_root = normalize_library_root(base_store_root)
        resolved_run_id = safe_run_id(run_id or new_intermediate_run_id())
        self.run_id = resolved_run_id
        self.run_dir = intermediate_run_dir(base_store_root=store_root, run_id=resolved_run_id)
        self.status_path = os.path.join(self.run_dir, "status.json")
        self._files: List[str] = []
        self._state: Dict[str, Any] = {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "status": "running",
            "current_stage": "initialized",
            "completed_stages": [],
            "metadata": dict(metadata or {}),
            "counts": {},
            "source_file": "",
        }
        os.makedirs(self.run_dir, exist_ok=True)
        self._flush_state()

    def summary(self) -> IntermediateRunSummary:
        """Builds the latest run summary."""

        return IntermediateRunSummary(
            run_id=self.run_id,
            run_dir=self.run_dir,
            status_path=self.status_path,
            files=list(self._files or []),
            current_stage=str(self._state.get("current_stage") or "initialized"),
            completed_stages=list(self._state.get("completed_stages") or []),
        )

    def write_ingest(self, result: DocumentIngestResult) -> None:
        """Writes the completed ingest snapshot."""

        payload = {
            "source_file": result.source_file,
            "text_units": [unit.to_dict() for unit in list(result.text_units or [])],
            "documents": [doc.to_dict() for doc in list(result.documents or [])],
            "skipped_documents": [doc.to_dict() for doc in list(result.skipped_documents or [])],
            "windows": [window.to_dict() for window in list(result.windows or [])],
            "errors": list(result.errors or []),
        }
        self._write_json("ingest/result.json", payload)
        self._set_stage(
            stage="ingest_completed",
            completed_stage="ingest",
            source_file=result.source_file,
            counts={
                "documents": len(result.documents),
                "skipped_documents": len(result.skipped_documents),
                "text_units": len(result.text_units),
                "windows": len(result.windows),
            },
        )

    def write_extract_progress(
        self,
        *,
        record: DocumentRecord,
        supports: List[SupportRecord],
        drafts: List[SkillDraft],
        cumulative: SkillExtractionResult,
        total_documents: int,
    ) -> None:
        """Writes per-document extraction progress as soon as one doc finishes."""

        payload = {
            "doc_id": record.doc_id,
            "title": record.title,
            "source_file": str((record.metadata or {}).get("source_file") or ""),
            "supports": [support.to_dict() for support in list(supports or [])],
            "skill_drafts": [draft.to_dict() for draft in list(drafts or [])],
            "cumulative_support_records": len(list(cumulative.support_records or [])),
            "cumulative_skill_drafts": len(list(cumulative.skill_drafts or [])),
            "processed_documents": len(
                {
                    str(item.doc_id or "").strip()
                    for item in list(cumulative.documents or [])
                    if str(item.doc_id or "").strip()
                }
            ),
            "total_documents": int(total_documents or 0),
        }
        doc_name = str(record.doc_id or "").strip() or "document"
        self._write_json(f"extract/documents/{doc_name}.json", payload)
        self._set_stage(
            stage="extract_running",
            counts={
                "documents": total_documents,
                "processed_documents": min(total_documents, self._count_progress_documents()),
                "support_records": len(list(cumulative.support_records or [])),
                "skill_drafts": len(list(cumulative.skill_drafts or [])),
            },
        )

    def write_extract(self, result: SkillExtractionResult) -> None:
        """Writes the aggregate extraction snapshot."""

        payload = {
            "documents": [doc.to_dict() for doc in list(result.documents or [])],
            "windows": [window.to_dict() for window in list(result.windows or [])],
            "support_records": [support.to_dict() for support in list(result.support_records or [])],
            "skill_drafts": [draft.to_dict() for draft in list(result.skill_drafts or [])],
            "errors": list(result.errors or []),
        }
        self._write_json("extract/result.json", payload)
        self._set_stage(
            stage="extract_completed",
            completed_stage="extract",
            counts={
                "support_records": len(result.support_records),
                "skill_drafts": len(result.skill_drafts),
                "documents": len(result.documents),
                "windows": len(result.windows),
            },
        )

    def write_compile(self, result: SkillCompilationResult) -> None:
        """Writes the completed compile snapshot."""

        payload = {
            "support_records": [support.to_dict() for support in list(result.support_records or [])],
            "skill_drafts": [draft.to_dict() for draft in list(result.skill_drafts or [])],
            "skill_specs": [skill.to_dict() for skill in list(result.skill_specs or [])],
            "errors": list(result.errors or []),
        }
        self._write_json("compile/result.json", payload)
        self._set_stage(
            stage="compile_completed",
            completed_stage="compile",
            counts={
                "compiled_support_records": len(result.support_records),
                "compiled_skill_drafts": len(result.skill_drafts),
                "skill_specs": len(result.skill_specs),
            },
        )

    def write_registration(self, result: VersionRegistrationResult) -> None:
        """Writes the completed registration snapshot."""

        payload = {
            "documents": [doc.to_dict() for doc in list(result.documents or [])],
            "support_records": [support.to_dict() for support in list(result.support_records or [])],
            "skill_specs": [skill.to_dict() for skill in list(result.skill_specs or [])],
            "lifecycles": [item.to_dict() for item in list(result.lifecycles or [])],
            "change_logs": list(result.change_logs or []),
            "version_history": list(result.version_history or []),
            "provenance_links": list(result.provenance_links or []),
            "upserted_store_skills": list(result.upserted_store_skills or []),
            "staging_runs": list(result.staging_runs or []),
            "visible_tree": dict(result.visible_tree or {}),
            "errors": list(result.errors or []),
            "dry_run": bool(result.dry_run),
        }
        self._write_json("register/result.json", payload)
        self._set_stage(
            stage="register_completed",
            completed_stage="register",
            counts={
                "lifecycles": len(result.lifecycles),
                "change_logs": len(result.change_logs),
                "version_history_entries": len(result.version_history),
                "provenance_links": len(result.provenance_links),
                "upserted_store_skills": len(result.upserted_store_skills),
                "staging_runs": len(result.staging_runs),
            },
        )

    def complete(self, *, summary: Optional[Dict[str, Any]] = None) -> None:
        """Marks the intermediate run as completed and optionally writes a summary."""

        if summary:
            self._write_json("final/summary.json", dict(summary or {}))
        self._state["status"] = "completed"
        self._state["updated_at"] = now_iso()
        self._flush_state()

    def fail(self, *, error: str) -> None:
        """Marks the intermediate run as failed."""

        self._state["status"] = "failed"
        self._state["updated_at"] = now_iso()
        self._state["last_error"] = str(error or "").strip()
        self._flush_state()

    def _count_progress_documents(self) -> int:
        path = os.path.join(self.run_dir, "extract", "documents")
        if not os.path.isdir(path):
            return 0
        return len([name for name in os.listdir(path) if name.endswith(".json")])

    def _write_json(self, relative_path: str, payload: Any) -> str:
        path = os.path.join(self.run_dir, relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=False)
        if path not in self._files:
            self._files.append(path)
        self._state["updated_at"] = now_iso()
        self._flush_state()
        return path

    def _set_stage(
        self,
        *,
        stage: str,
        completed_stage: str = "",
        source_file: str = "",
        counts: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._state["current_stage"] = str(stage or "").strip() or self._state.get("current_stage") or "initialized"
        if completed_stage:
            existing = list(self._state.get("completed_stages") or [])
            if completed_stage not in existing:
                existing.append(completed_stage)
            self._state["completed_stages"] = existing
        if source_file:
            self._state["source_file"] = str(source_file or "").strip()
        if counts:
            merged = dict(self._state.get("counts") or {})
            merged.update(dict(counts or {}))
            self._state["counts"] = merged
        self._state["updated_at"] = now_iso()
        self._flush_state()

    def _flush_state(self) -> None:
        os.makedirs(os.path.dirname(self.status_path), exist_ok=True)
        with open(self.status_path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, ensure_ascii=False, indent=2, sort_keys=False)

