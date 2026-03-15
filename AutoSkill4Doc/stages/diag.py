"""
Diagnostic helpers for the current AutoSkill4Doc pipeline.

The goal is observability, not a separate extraction implementation. The diag
flow reuses the current ingest/extract stages, defaults to dry-run semantics,
and can optionally emit one JSONL row per extraction window.
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..pipeline import DocumentBuildPipeline


def run_document_diag(
    *,
    pipeline: "DocumentBuildPipeline",
    file_path: str,
    title: str = "",
    source_type: str = "document",
    domain: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    continue_on_error: bool = True,
    max_documents: int = 0,
    extract_strategy: str = "recommended",
    report_path: str = "",
    report_limit: int = 0,
) -> Dict[str, Any]:
    """Runs a non-persisting diagnostic extraction pass over one document source."""

    ingest_result = pipeline.ingest_document(
        file_path=str(file_path or "").strip(),
        title=str(title or "").strip(),
        source_type=str(source_type or "").strip() or "document",
        domain=str(domain or "").strip(),
        metadata=dict(metadata or {}),
        continue_on_error=bool(continue_on_error),
        dry_run=True,
        max_documents=int(max_documents or 0),
        extract_strategy=str(extract_strategy or "").strip() or "recommended",
    )
    extracted_result = pipeline.extract_skills(documents=ingest_result.documents, windows=ingest_result.windows)

    support_rows: Dict[str, List[Dict[str, Any]]] = {}
    draft_rows: Dict[str, List[Dict[str, Any]]] = {}
    for support in list(extracted_result.support_records or []):
        window_id = str((support.metadata or {}).get("window_id") or "").strip()
        if not window_id:
            continue
        support_rows.setdefault(window_id, []).append(
            {
                "support_id": support.support_id,
                "skill_id": support.skill_id,
                "section": support.section,
                "relation_type": support.relation_type.value,
                "confidence": support.confidence,
            }
        )
    for draft in list(extracted_result.skill_drafts or []):
        window_id = str((draft.metadata or {}).get("window_id") or "").strip()
        if not window_id:
            continue
        draft_rows.setdefault(window_id, []).append(
            {
                "draft_id": draft.draft_id,
                "name": draft.name,
                "asset_type": draft.asset_type,
                "granularity": draft.granularity,
                "task_family": draft.task_family,
                "method_family": draft.method_family,
                "stage": draft.stage,
            }
        )

    windows = []
    jsonl_rows: List[Dict[str, Any]] = []
    for index, window in enumerate(list(ingest_result.windows or [])):
        row = {
            "window_index": index,
            "window_id": window.window_id,
            "doc_id": window.doc_id,
            "section_heading": window.section_heading,
            "strategy": window.strategy,
            "anchor_hits": list(window.anchor_hits or []),
            "paragraph_start": window.paragraph_start,
            "paragraph_end": window.paragraph_end,
            "char_count": len(str(window.text or "")),
            "supports": list(support_rows.get(window.window_id) or []),
            "drafts": list(draft_rows.get(window.window_id) or []),
        }
        windows.append(row)
        if report_limit <= 0 or len(jsonl_rows) < int(report_limit):
            jsonl_rows.append(row)

    report_abs = ""
    if str(report_path or "").strip():
        report_abs = os.path.abspath(os.path.expanduser(str(report_path).strip()))
        os.makedirs(os.path.dirname(report_abs) or ".", exist_ok=True)
        with open(report_abs, "w", encoding="utf-8") as f:
            for row in jsonl_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return {
        "route": "diag",
        "dry_run": True,
        "extract_only": True,
        "source_file": ingest_result.source_file,
        "documents": len(ingest_result.documents),
        "skipped_documents": len(ingest_result.skipped_documents),
        "windows": windows,
        "total_windows": len(windows),
        "total_support_records": len(extracted_result.support_records),
        "total_skill_drafts": len(extracted_result.skill_drafts),
        "report_path": report_abs or None,
        "errors": list(ingest_result.errors or []) + list(extracted_result.errors or []),
    }
