"""
Document ingestion stage for the offline document pipeline.

This stage turns file or structured input into normalized `DocumentRecord`
objects, computes stable content hashes, and performs incremental skip checks
against the document registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional, Protocol, Tuple

from .common import StageLogger, emit_stage_log
from .file_loader import data_to_text_unit, load_file_units
from .models import DocumentRecord, DocumentSection, TextSpan
from .registry import DocumentRegistry


def compute_content_hash(
    *,
    title: str,
    raw_text: str,
    sections: List[DocumentSection],
    metadata: Dict[str, Any],
    authors: List[str],
    year: Optional[int],
    domain: str,
    source_type: str,
) -> str:
    """Builds a stable content hash for incremental detection."""

    payload = {
        "title": str(title or "").strip(),
        "raw_text": str(raw_text or ""),
        "sections": [sec.to_dict() for sec in (sections or [])],
        "metadata": dict(metadata or {}),
        "authors": [str(x).strip() for x in (authors or []) if str(x).strip()],
        "year": int(year) if year is not None else None,
        "domain": str(domain or "").strip(),
        "source_type": str(source_type or "").strip(),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def parse_sections_from_text(text: str, *, default_title: str = "") -> List[DocumentSection]:
    """
    Parses markdown-style sections from text.

    If no headings are present, the whole document is treated as one section.
    """

    src = str(text or "")
    if not src.strip():
        return []

    heading_re = re.compile(r"(?m)^(#{1,6})\s+(.+?)\s*$")
    matches = list(heading_re.finditer(src))
    if not matches:
        return [
            DocumentSection(
                heading=str(default_title or "Document").strip() or "Document",
                text=src.strip(),
                level=1,
                span=TextSpan(start=0, end=len(src)),
            )
        ]

    out: List[DocumentSection] = []
    # Capture a preface block before the first heading if it contains content.
    first = matches[0]
    if first.start() > 0:
        prefix = src[: first.start()].strip()
        if prefix:
            out.append(
                DocumentSection(
                    heading=str(default_title or "Overview").strip() or "Overview",
                    text=prefix,
                    level=1,
                    span=TextSpan(start=0, end=first.start()),
                )
            )

    for idx, match in enumerate(matches):
        level = len(match.group(1))
        heading = str(match.group(2) or "").strip() or (default_title or "Section")
        content_start = match.end()
        content_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(src)
        body = src[content_start:content_end].strip()
        if not body:
            continue
        out.append(
            DocumentSection(
                heading=heading,
                text=body,
                level=level,
                span=TextSpan(start=content_start, end=content_end),
            )
        )
    return out


def _normalize_source_type(source_type: str, source_file: str) -> str:
    """Chooses a generic source type with lightweight file-based hints."""

    src = str(source_type or "").strip()
    if src:
        return src
    ext = os.path.splitext(str(source_file or "").strip())[1].lower()
    if ext in {".md", ".markdown"}:
        return "markdown_document"
    if ext in {".txt"}:
        return "text_document"
    if ext in {".json", ".jsonl"}:
        return "structured_document"
    return "document"


def _structured_units_from_data(data: Any, *, title: str = "") -> List[Dict[str, Any]]:
    """Normalizes in-memory structured input into document-like units."""

    if data is None:
        return []

    if isinstance(data, dict):
        for key in ("documents", "items", "records"):
            bucket = data.get(key)
            if isinstance(bucket, list):
                out: List[Dict[str, Any]] = []
                for idx, item in enumerate(bucket):
                    if isinstance(item, dict):
                        unit = dict(item)
                        unit.setdefault("title", str(unit.get("title") or f"inline_data_{idx + 1}"))
                        out.append(unit)
                    else:
                        out.append(data_to_text_unit(item, title=f"inline_data_{idx + 1}"))
                return out
        if any(k in data for k in {"raw_text", "text", "sections", "title"}):
            return [dict(data)]
        return [data_to_text_unit(data, title=str(title or "inline_data"))]

    if isinstance(data, list):
        out = []
        for idx, item in enumerate(data):
            if isinstance(item, dict) and any(k in item for k in {"raw_text", "text", "sections", "title"}):
                unit = dict(item)
                unit.setdefault("title", str(unit.get("title") or f"inline_data_{idx + 1}"))
                out.append(unit)
            else:
                out.append(data_to_text_unit(item, title=f"inline_data_{idx + 1}"))
        return out

    return [data_to_text_unit(data, title=str(title or "inline_data"))]


def _stable_document_id(*, source_key: str, explicit_doc_id: str = "") -> str:
    """Builds a stable document id derived from source identity rather than content."""

    explicit = str(explicit_doc_id or "").strip()
    if explicit:
        return explicit
    key = str(source_key or "").strip() or "document"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill-document:{key}"))


def _source_key_for_unit(unit: Dict[str, Any], default_title: str) -> str:
    """Chooses a stable identity key for one input unit."""

    source_file = str(unit.get("source_file") or "").strip()
    if source_file:
        return os.path.abspath(os.path.expanduser(source_file))
    title = str(unit.get("title") or "").strip() or str(default_title or "").strip()
    if title:
        return title
    doc_id = str(unit.get("doc_id") or "").strip()
    if doc_id:
        return doc_id
    return "document"


@dataclass
class DocumentIngestResult:
    """Output of the document ingestion stage."""

    documents: List[DocumentRecord] = field(default_factory=list)
    skipped_documents: List[DocumentRecord] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    source_file: Optional[str] = None


class DocumentIngestor(Protocol):
    """Pluggable document ingestion interface."""

    def ingest(
        self,
        *,
        data: Optional[Any],
        file_path: str,
        title: str,
        source_type: str,
        domain: str,
        metadata: Optional[Dict[str, Any]],
        registry: Optional[DocumentRegistry],
        continue_on_error: bool,
        dry_run: bool,
        max_documents: int,
        logger: StageLogger,
    ) -> DocumentIngestResult:
        """Runs the ingestion stage and returns normalized document records."""


class HeuristicDocumentIngestor:
    """Rule-based document ingestor used by the MVP offline pipeline."""

    def ingest(
        self,
        *,
        data: Optional[Any],
        file_path: str,
        title: str,
        source_type: str,
        domain: str,
        metadata: Optional[Dict[str, Any]],
        registry: Optional[DocumentRegistry],
        continue_on_error: bool,
        dry_run: bool,
        max_documents: int,
        logger: StageLogger,
    ) -> DocumentIngestResult:
        """Normalizes input into DocumentRecord objects and performs incremental skipping."""

        abs_input = ""
        if data is not None:
            units = _structured_units_from_data(data, title=title)
        elif str(file_path or "").strip():
            units, abs_input = load_file_units(str(file_path), max_files=int(max_documents or 0))
        else:
            raise ValueError("ingest_document requires data or file_path")

        result = DocumentIngestResult(source_file=(abs_input or None))
        base_md = dict(metadata or {})

        for idx, unit in enumerate(units):
            try:
                built = self._build_record(
                    unit=unit,
                    default_title=title,
                    source_type=source_type,
                    domain=domain,
                    metadata=base_md,
                )
                existing = (
                    registry.find_document_by_content_hash(
                        doc_id=built.doc_id,
                        content_hash=built.content_hash,
                        source_file=str((built.metadata or {}).get("source_file") or ""),
                    )
                    if registry is not None
                    else None
                )
                if existing is not None:
                    result.skipped_documents.append(existing)
                    emit_stage_log(logger, f"[ingest_document] skip unchanged doc={existing.doc_id}")
                    continue
                result.documents.append(built)
                emit_stage_log(logger, f"[ingest_document] prepared doc={built.doc_id}")
            except Exception as e:
                result.errors.append({"index": idx, "error": str(e)})
                emit_stage_log(logger, f"[ingest_document] error index={idx}: {e}")
                if not continue_on_error:
                    raise
        return result

    def _build_record(
        self,
        *,
        unit: Dict[str, Any],
        default_title: str,
        source_type: str,
        domain: str,
        metadata: Dict[str, Any],
    ) -> DocumentRecord:
        """Builds one normalized DocumentRecord from a mixed-shape unit."""

        raw = str(unit.get("raw_text") or unit.get("text") or "").strip()
        sections_raw = list(unit.get("sections") or [])
        title_value = str(unit.get("title") or "").strip() or str(default_title or "").strip() or "document"
        source_file = str(unit.get("source_file") or "").strip()
        authors = [str(x).strip() for x in list(unit.get("authors") or []) if str(x).strip()]
        year = unit.get("year")
        doc_domain = str(unit.get("domain") or domain or "").strip()
        md = dict(metadata or {})
        md.update(dict(unit.get("metadata") or {}))
        if source_file:
            md.setdefault("source_file", source_file)

        if sections_raw:
            sections = [
                sec if isinstance(sec, DocumentSection) else DocumentSection.from_dict(dict(sec or {}))
                for sec in sections_raw
            ]
            if not raw:
                raw = "\n\n".join(sec.text for sec in sections if str(sec.text or "").strip())
        else:
            sections = parse_sections_from_text(raw, default_title=title_value)

        normalized_source_type = _normalize_source_type(source_type, source_file)
        content_hash = compute_content_hash(
            title=title_value,
            raw_text=raw,
            sections=sections,
            metadata=md,
            authors=authors,
            year=(int(year) if year is not None and str(year).strip() else None),
            domain=doc_domain,
            source_type=normalized_source_type,
        )

        source_key = _source_key_for_unit(unit, default_title=title_value)
        doc_id = _stable_document_id(
            source_key=source_key,
            explicit_doc_id=str(unit.get("doc_id") or "").strip(),
        )
        return DocumentRecord(
            doc_id=doc_id,
            source_type=normalized_source_type,
            title=title_value,
            authors=authors,
            year=(int(year) if year is not None and str(year).strip() else None),
            domain=doc_domain,
            raw_text=raw,
            sections=sections,
            metadata=md,
            checksum=content_hash,
            content_hash=content_hash,
        )


def ingest_document(
    *,
    data: Optional[Any] = None,
    file_path: str = "",
    title: str = "",
    source_type: str = "document",
    domain: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    registry: Optional[DocumentRegistry] = None,
    ingestor: Optional[DocumentIngestor] = None,
    continue_on_error: bool = True,
    dry_run: bool = False,
    max_documents: int = 0,
    logger: StageLogger = None,
) -> DocumentIngestResult:
    """Public functional wrapper for the document ingestion stage."""

    impl = ingestor or HeuristicDocumentIngestor()
    return impl.ingest(
        data=data,
        file_path=file_path,
        title=title,
        source_type=source_type,
        domain=domain,
        metadata=metadata,
        registry=registry,
        continue_on_error=continue_on_error,
        dry_run=bool(dry_run),
        max_documents=int(max_documents or 0),
        logger=logger,
    )
