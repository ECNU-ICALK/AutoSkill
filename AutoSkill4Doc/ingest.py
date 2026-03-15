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

from autoskill.llm.base import LLM
from autoskill.llm.factory import build_llm

from .core.common import StageLogger, document_progress_label, emit_stage_log
from .core.config import DEFAULT_EXTRACT_STRATEGY, DEFAULT_MAX_SECTION_CHARS, normalize_extract_strategy, normalize_section_outline_mode
from .core.llm_utils import llm_complete_json, maybe_json_dict
from .document.file_loader import data_to_text_unit, load_file_units
from .document.windowing import build_windows_for_record
from .models import DocumentRecord, DocumentSection, StrictWindow, TextSpan, TextUnit
from .store.registry import DocumentRegistry


_MARKDOWN_HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
_DECIMAL_HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+){0,4})(?:\s*[.)、])?\s+(.+?)\s*$")
_CHAPTER_HEADING_RE = re.compile(r"^\s*第([一二三四五六七八九十百零〇\d]+)(章|节|部分|篇)\s+(.+?)\s*$")
_CN_ENUM_HEADING_RE = re.compile(r"^\s*([一二三四五六七八九十百零〇]+)[、.]\s*(.+?)\s*$")
_PAREN_ENUM_HEADING_RE = re.compile(r"^\s*[（(]([一二三四五六七八九十百零〇\d]+)[）)]\s*(.+?)\s*$")
_ROMAN_HEADING_RE = re.compile(r"^\s*([IVXLCM]+)[.)]\s+(.+?)\s*$", re.IGNORECASE)
_BULLET_LINE_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_REFERENCE_LINE_RE = re.compile(
    r"^\s*(?:\[\d+\]|\(\d+\)|\d+\.\s+.+\b(?:19|20)\d{2}[a-z]?\b.+|.+\bdoi\b.+|https?://\S+)",
    re.IGNORECASE,
)
_OUTLINE_FALLBACK_MAX_CANDIDATES = 64


@dataclass(frozen=True)
class _DetectedHeading:
    """One detected section heading with a normalized hierarchy level."""

    start: int
    end: int
    heading: str
    level: int
    number: str = ""
    kind: str = "plain"


def _looks_like_heading_title(title: str, *, allow_sentence_like: bool = False) -> bool:
    """Heuristic guard used to reject numbered list items misread as headings."""

    text = str(title or "").strip()
    if not text:
        return False
    if len(text) > 120:
        return False
    if text.startswith(("-", "*", "•")):
        return False
    if re.search(r"[。！？!?；;]\s*$", text) and not allow_sentence_like:
        return False
    if text.count("。") + text.count(". ") + text.count("；") + text.count(";") >= 2:
        return False
    if len(text.split()) > 24:
        return False
    return True


def _detect_heading(line: str, *, start: int, end: int) -> Optional[_DetectedHeading]:
    """Detects markdown, numbered, and Chinese section headings in one line."""

    text = str(line or "").strip()
    if not text:
        return None

    match = _MARKDOWN_HEADING_RE.match(text)
    if match:
        heading = str(match.group(2) or "").strip()
        if _looks_like_heading_title(heading, allow_sentence_like=True):
            return _DetectedHeading(start=start, end=end, heading=heading, level=len(match.group(1)), kind="markdown")

    match = _CHAPTER_HEADING_RE.match(text)
    if match:
        heading = text
        return _DetectedHeading(start=start, end=end, heading=heading, level=1, number=str(match.group(1) or ""), kind="chapter")

    match = _DECIMAL_HEADING_RE.match(text)
    if match:
        number = str(match.group(1) or "").strip()
        title = str(match.group(2) or "").strip()
        if _looks_like_heading_title(title) and ("." in number or len(title) <= 72):
            return _DetectedHeading(
                start=start,
                end=end,
                heading=text,
                level=max(1, number.count(".") + 1),
                number=number,
                kind="decimal",
            )

    match = _PAREN_ENUM_HEADING_RE.match(text)
    if match:
        title = str(match.group(2) or "").strip()
        if _looks_like_heading_title(title):
            number = str(match.group(1) or "").strip()
            level = 3 if re.fullmatch(r"\d+", number) else 2
            return _DetectedHeading(start=start, end=end, heading=text, level=level, number=number, kind="paren")

    match = _CN_ENUM_HEADING_RE.match(text)
    if match:
        title = str(match.group(2) or "").strip()
        if _looks_like_heading_title(title):
            return _DetectedHeading(start=start, end=end, heading=text, level=1, number=str(match.group(1) or ""), kind="cn_enum")

    match = _ROMAN_HEADING_RE.match(text)
    if match:
        title = str(match.group(2) or "").strip()
        if _looks_like_heading_title(title):
            return _DetectedHeading(start=start, end=end, heading=text, level=1, number=str(match.group(1) or ""), kind="roman")

    return None


def _detect_headings(src: str) -> List[_DetectedHeading]:
    """Detects structural headings line-by-line so numbered sub-sections are preserved."""

    matches: List[_DetectedHeading] = []
    cursor = 0
    for line in str(src or "").splitlines(keepends=True):
        start = cursor
        end = cursor + len(line)
        detected = _detect_heading(line, start=start, end=end)
        if detected is not None:
            matches.append(detected)
        cursor = end
    return matches


def _first_nonempty_paragraph(text: str, *, limit: int = 180) -> str:
    """Returns a short summary-like snippet from one section body."""

    for piece in re.split(r"\n\s*\n+|\n", str(text or "")):
        normalized = str(piece or "").strip()
        if normalized:
            return normalized[:limit]
    return ""


def _annotate_section_hierarchy(sections: List[DocumentSection]) -> List[DocumentSection]:
    """Adds heading path, parent, and sibling metadata for later window planning."""

    stacks: List[str] = []
    enriched: List[DocumentSection] = []
    raw_paths: List[List[str]] = []
    for section in list(sections or []):
        payload = section.to_dict()
        md = dict(payload.get("metadata") or {})
        existing_path = [str(item).strip() for item in list(md.get("heading_path") or []) if str(item).strip()]
        if existing_path:
            path = existing_path
        else:
            normalized_level = max(1, min(int(section.level or 1), len(stacks) + 1))
            while len(stacks) >= normalized_level:
                stacks.pop()
            stacks.append(section.heading)
            path = list(stacks)
        md["heading_path"] = list(path)
        md["parent_heading"] = path[-2] if len(path) > 1 else ""
        md["section_summary"] = _first_nonempty_paragraph(section.text)
        payload["metadata"] = md
        enriched.append(DocumentSection.from_dict(payload))
        raw_paths.append(path)

    sibling_map: Dict[Tuple[str, ...], List[str]] = {}
    for path in raw_paths:
        sibling_map.setdefault(tuple(path[:-1]), []).append(path[-1])

    final_sections: List[DocumentSection] = []
    for section, path in zip(enriched, raw_paths):
        payload = section.to_dict()
        md = dict(payload.get("metadata") or {})
        siblings = [heading for heading in sibling_map.get(tuple(path[:-1]), []) if heading != section.heading]
        if siblings:
            md["sibling_headings"] = siblings[:8]
        payload["metadata"] = md
        final_sections.append(DocumentSection.from_dict(payload))
    return final_sections


def _fallback_single_section(src: str, *, default_title: str = "") -> List[DocumentSection]:
    """Returns one document-wide section when no structure can be recovered."""

    title = str(default_title or "Document").strip() or "Document"
    return [
        DocumentSection(
            heading=title,
            text=src.strip(),
            level=1,
            span=TextSpan(start=0, end=len(src)),
            metadata={"heading_path": [title]},
        )
    ]


def _build_sections_from_headings(src: str, matches: List[_DetectedHeading], *, default_title: str = "") -> List[DocumentSection]:
    """Builds sections from one ordered heading list."""

    if not matches:
        return _fallback_single_section(src, default_title=default_title)

    out: List[DocumentSection] = []
    first = matches[0]
    if first.start > 0:
        prefix = src[: first.start].strip()
        if prefix:
            overview = str(default_title or "Overview").strip() or "Overview"
            out.append(
                DocumentSection(
                    heading=overview,
                    text=prefix,
                    level=1,
                    span=TextSpan(start=0, end=first.start),
                    metadata={"heading_path": [overview]},
                )
            )

    heading_stack: List[_DetectedHeading] = []
    for idx, match in enumerate(matches):
        while heading_stack and heading_stack[-1].level >= match.level:
            heading_stack.pop()
        heading_stack.append(match)
        content_start = match.end
        content_end = matches[idx + 1].start if idx + 1 < len(matches) else len(src)
        body = src[content_start:content_end].strip()
        if not body:
            continue
        path = [item.heading for item in heading_stack]
        out.append(
            DocumentSection(
                heading=str(match.heading or "").strip() or (default_title or "Section"),
                text=body,
                level=int(match.level or 1),
                span=TextSpan(start=content_start, end=content_end),
                metadata={
                    "heading_path": path,
                    "parent_heading": path[-2] if len(path) > 1 else "",
                    "heading_number": str(match.number or "").strip(),
                    "heading_kind": str(match.kind or "").strip(),
                },
            )
        )
    return _annotate_section_hierarchy(out) if out else _fallback_single_section(src, default_title=default_title)


def _iter_line_records(src: str) -> List[Dict[str, Any]]:
    """Returns line records with stable offsets for outline classification."""

    records: List[Dict[str, Any]] = []
    cursor = 0
    for idx, raw_line in enumerate(str(src or "").splitlines(keepends=True)):
        text = raw_line.rstrip("\r\n")
        records.append(
            {
                "line_index": idx,
                "text": text,
                "stripped": text.strip(),
                "start": cursor,
                "end": cursor + len(raw_line),
                "blank": not text.strip(),
            }
        )
        cursor += len(raw_line)
    return records


def _next_nonempty_preview(lines: List[Dict[str, Any]], *, start_index: int, limit: int = 160) -> str:
    """Returns a short preview from the next non-empty paragraph after one heading candidate."""

    snippets: List[str] = []
    for idx in range(start_index + 1, len(lines)):
        text = str(lines[idx].get("stripped") or "").strip()
        if not text:
            if snippets:
                break
            continue
        snippets.append(text)
        if len(" ".join(snippets)) >= limit:
            break
    return " ".join(snippets)[:limit]


def _heading_outline_candidates(src: str) -> List[Dict[str, Any]]:
    """Builds a compact candidate outline for one document-wide LLM fallback pass."""

    lines = _iter_line_records(src)
    candidates: List[Dict[str, Any]] = []
    for idx, record in enumerate(lines):
        stripped = str(record.get("stripped") or "").strip()
        if not stripped:
            continue
        if len(stripped) > 120:
            continue
        if _BULLET_LINE_RE.match(stripped):
            continue
        if _REFERENCE_LINE_RE.search(stripped):
            continue
        if not _looks_like_heading_title(stripped):
            continue
        prev_blank = idx == 0 or bool(lines[idx - 1].get("blank"))
        next_blank = idx + 1 >= len(lines) or bool(lines[idx + 1].get("blank"))
        if not (prev_blank or next_blank):
            continue
        candidates.append(
            {
                "candidate_index": len(candidates),
                "line_index": int(record.get("line_index") or idx),
                "text": stripped,
                "preview": _next_nonempty_preview(lines, start_index=idx),
                "start": int(record.get("start") or 0),
                "end": int(record.get("end") or 0),
            }
        )
        if len(candidates) >= _OUTLINE_FALLBACK_MAX_CANDIDATES:
            break
    return candidates


def _outline_matches_from_llm(
    *,
    src: str,
    default_title: str,
    llm: Optional[LLM],
) -> List[_DetectedHeading]:
    """Runs one compact outline-classification call when rule-based heading detection found nothing."""

    if llm is None:
        return []
    candidates = _heading_outline_candidates(src)
    if len(candidates) < 2:
        return []

    payload = {
        "title": str(default_title or "").strip(),
        "instruction": "Identify only true structural section or subsection headings. Ignore bullets, references, lists, and ordinary sentences.",
        "candidates": [
            {
                "candidate_index": item["candidate_index"],
                "line_index": item["line_index"],
                "text": item["text"],
                "preview": item["preview"],
            }
            for item in candidates
        ],
    }
    system = (
        "You classify heading candidates for one long document outline.\n"
        "Return JSON only: {\"headings\": [{\"candidate_index\": 0, \"level\": 1}]}\n"
        "Rules:\n"
        "- Include only real structural headings.\n"
        "- level 1 means top-level section, level 2 means subsection, level 3 means sub-subsection.\n"
        "- Ignore references, bibliography, acknowledgements, figure/table captions, bullet items, and normal prose lines.\n"
        "- Use relative levels within this document only.\n"
    )
    repair_system = (
        "Return strict JSON only in the form {\"headings\": [{\"candidate_index\": 0, \"level\": 1}]}. "
        "Do not include explanations."
    )
    try:
        parsed = llm_complete_json(
            llm=llm,
            system=system,
            payload=payload,
            repair_system=repair_system,
            repair_payload=payload,
        )
    except Exception:
        return []

    obj = maybe_json_dict(parsed)
    raw_headings = list(obj.get("headings") or [])
    by_index = {int(item["candidate_index"]): item for item in candidates}
    matches: List[_DetectedHeading] = []
    for raw in raw_headings:
        if not isinstance(raw, dict):
            continue
        try:
            candidate_index = int(raw.get("candidate_index"))
        except Exception:
            continue
        item = by_index.get(candidate_index)
        if item is None:
            continue
        try:
            level = max(1, min(int(raw.get("level") or 1), 4))
        except Exception:
            level = 1
        matches.append(
            _DetectedHeading(
                start=int(item["start"]),
                end=int(item["end"]),
                heading=str(item["text"]).strip(),
                level=level,
                kind="outline_llm",
            )
        )
    return sorted(matches, key=lambda item: (item.start, item.end))


def _should_try_outline_fallback(src: str, matches: List[_DetectedHeading]) -> bool:
    """Returns whether one document structure looks weak enough to justify one outline pass."""

    if not str(src or "").strip():
        return False
    if not matches:
        return True
    candidates = _heading_outline_candidates(src)
    if len(candidates) < 3:
        return False
    top_level_count = sum(1 for item in matches if int(item.level or 1) <= 1)
    if len(matches) == 1:
        return True
    if top_level_count <= 1 and len(matches) <= 2 and len(candidates) >= 4:
        return True
    if top_level_count <= 1 and len(candidates) >= max(len(matches) + 3, 5):
        return True
    return False


def _prefer_outline_matches(
    *,
    src: str,
    rule_matches: List[_DetectedHeading],
    llm_matches: List[_DetectedHeading],
) -> bool:
    """Chooses whether LLM-derived headings look materially better than rule headings."""

    if not llm_matches:
        return False
    if not rule_matches:
        return True
    rule_top_level = sum(1 for item in rule_matches if int(item.level or 1) <= 1)
    llm_top_level = sum(1 for item in llm_matches if int(item.level or 1) <= 1)
    if len(llm_matches) > len(rule_matches):
        return True
    if llm_top_level > rule_top_level:
        return True
    if len(str(src or "")) >= 4000 and len(llm_matches) >= len(rule_matches) and llm_top_level >= rule_top_level:
        return True
    return False


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

    return _build_sections_from_headings(src, _detect_headings(src), default_title=default_title)


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

    text_units: List[TextUnit] = field(default_factory=list)
    documents: List[DocumentRecord] = field(default_factory=list)
    skipped_documents: List[DocumentRecord] = field(default_factory=list)
    windows: List[StrictWindow] = field(default_factory=list)
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
        extract_strategy: str,
        logger: StageLogger,
    ) -> DocumentIngestResult:
        """Runs the ingestion stage and returns normalized document records."""


class HeuristicDocumentIngestor:
    """Rule-based document ingestor used by the MVP offline pipeline."""

    def __init__(
        self,
        *,
        llm: Optional[LLM] = None,
        llm_config: Optional[Dict[str, Any]] = None,
        max_section_chars: int = DEFAULT_MAX_SECTION_CHARS,
        outline_fallback_mode: str = "auto",
    ) -> None:
        """Builds one document ingestor with optional low-frequency outline LLM fallback."""

        self._llm = llm
        self._llm_config = dict(llm_config or {})
        self.max_section_chars = max(1000, int(max_section_chars or _DEFAULT_MAX_SECTION_CHARS))
        self.outline_fallback_mode = normalize_section_outline_mode(outline_fallback_mode)

    def _outline_llm(self) -> Optional[LLM]:
        """Lazily builds the optional outline-classification LLM."""

        if self.outline_fallback_mode == "off":
            return None
        if self._llm is not None:
            return self._llm
        provider = str(self._llm_config.get("provider") or "").strip().lower()
        if not provider or provider == "mock":
            return None
        self._llm = build_llm(dict(self._llm_config))
        return self._llm

    def _parse_sections_with_fallback(self, *, raw_text: str, default_title: str, logger: StageLogger) -> List[DocumentSection]:
        """Uses rule-based headings first, then one outline LLM fallback if needed."""

        src = str(raw_text or "")
        matches = _detect_headings(src)
        llm = self._outline_llm() if _should_try_outline_fallback(src, matches) else None
        if llm is not None:
            llm_matches = _outline_matches_from_llm(src=src, default_title=default_title, llm=llm)
            if _prefer_outline_matches(src=src, rule_matches=matches, llm_matches=llm_matches):
                emit_stage_log(
                    logger,
                    f"[ingest_document] outline-fallback title={default_title or 'document'} rule_headings={len(matches)} llm_headings={len(llm_matches)}",
                )
                return _build_sections_from_headings(src, llm_matches, default_title=default_title)
        if matches:
            return _build_sections_from_headings(src, matches, default_title=default_title)
        return _fallback_single_section(src, default_title=default_title)

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
        extract_strategy: str,
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
        if not units and abs_input and os.path.isfile(abs_input):
            message = f"no readable text extracted from file: {abs_input}"
            result.errors.append({"source_file": abs_input, "error": message})
            emit_stage_log(logger, f"[ingest_document] error source_file={abs_input}: {message}")
            if not continue_on_error:
                raise ValueError(message)
            return result
        if not units and abs_input and os.path.isdir(abs_input):
            message = f"no readable text extracted from directory: {abs_input}"
            result.errors.append({"source_file": abs_input, "error": message})
            emit_stage_log(logger, f"[ingest_document] error source_file={abs_input}: {message}")
            if not continue_on_error:
                raise ValueError(message)
            return result
        base_md = dict(metadata or {})

        for idx, unit in enumerate(units):
            try:
                text_unit = self._build_text_unit(
                    unit=unit,
                    default_title=title,
                    source_type=source_type,
                    domain=domain,
                    metadata=base_md,
                )
                result.text_units.append(text_unit)
                built = self._build_record(
                    unit=unit,
                    default_title=title,
                    source_type=source_type,
                    domain=domain,
                    metadata=base_md,
                    logger=logger,
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
                    emit_stage_log(
                        logger,
                        f"[ingest_document] skip unchanged {document_progress_label(doc_id=existing.doc_id, title=existing.title, source_file=str((existing.metadata or {}).get('source_file') or ''))}",
                    )
                    continue
                result.windows.extend(
                    build_windows_for_record(
                        built,
                        strategy=extract_strategy,
                        max_section_chars=self.max_section_chars,
                    )
                )
                result.documents.append(built)
                emit_stage_log(
                    logger,
                    f"[ingest_document] prepared {document_progress_label(doc_id=built.doc_id, title=built.title, source_file=str((built.metadata or {}).get('source_file') or ''))} sections={len(built.sections or [])} windows={len([w for w in result.windows if w.doc_id == built.doc_id])}",
                )
            except Exception as e:
                result.errors.append({"index": idx, "error": str(e)})
                emit_stage_log(logger, f"[ingest_document] error index={idx}: {e}")
                if not continue_on_error:
                    raise
        return result

    def _build_text_unit(
        self,
        *,
        unit: Dict[str, Any],
        default_title: str,
        source_type: str,
        domain: str,
        metadata: Dict[str, Any],
    ) -> TextUnit:
        """Builds one normalized text unit from raw input payload."""

        raw = str(unit.get("raw_text") or unit.get("text") or "").strip()
        title_value = str(unit.get("title") or "").strip() or str(default_title or "").strip() or "document"
        source_file = str(unit.get("source_file") or "").strip()
        md = dict(metadata or {})
        md.update(dict(unit.get("metadata") or {}))
        if source_file:
            md.setdefault("source_file", source_file)
        source_key = _source_key_for_unit(unit, default_title=title_value)
        unit_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill4doc-unit:{source_key}"))
        return TextUnit(
            unit_id=unit_id,
            title=title_value,
            text=raw,
            source_file=source_file,
            source_type=_normalize_source_type(source_type, source_file),
            domain=str(unit.get("domain") or domain or "").strip(),
            metadata=md,
        )

    def _build_record(
        self,
        *,
        unit: Dict[str, Any],
        default_title: str,
        source_type: str,
        domain: str,
        metadata: Dict[str, Any],
        logger: StageLogger = None,
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
            sections = _annotate_section_hierarchy(sections)
            if not raw:
                raw = "\n\n".join(sec.text for sec in sections if str(sec.text or "").strip())
        else:
            sections = self._parse_sections_with_fallback(raw_text=raw, default_title=title_value, logger=logger)

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
    extract_strategy: str = DEFAULT_EXTRACT_STRATEGY,
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
        extract_strategy=normalize_extract_strategy(extract_strategy),
        logger=logger,
    )
