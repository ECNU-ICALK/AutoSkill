"""
Strict/recommended window planning for AutoSkill4Doc.

The goal is not equal-sized chunks. The goal is to preserve local, reusable
task blocks that are more likely to yield one clean child skill candidate.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from ..core.common import dedupe_strings, normalize_text
from ..core.config import normalize_extract_strategy
from ..models import DocumentRecord, DocumentSection, StrictWindow, TextSpan

_DEFAULT_NOISE_SECTION_MARKERS = (
    "abstract",
    "summary",
    "keywords",
    "keyword",
    "references",
    "reference",
    "bibliography",
    "doi",
    "funding",
    "acknowledg",
    "author contributions",
    "conflict of interest",
    "ethics",
    "appendix",
    "摘要",
    "关键词",
    "参考文献",
    "基金",
    "致谢",
    "附录",
    "利益冲突",
)

_DEFAULT_PRIORITY_MARKERS = (
    "goal",
    "session goal",
    "treatment goal",
    "intervention",
    "session intervention",
    "stage",
    "session",
    "homework",
    "worksheet",
    "work sheet",
    "risk",
    "safety",
    "relapse prevention",
    "protocol",
    "procedure",
    "technique",
    "目标",
    "干预",
    "阶段",
    "会谈",
    "作业",
    "工作表",
    "清单",
    "风险",
    "安全计划",
    "复发预防",
    "技术",
)

_DEFAULT_ANCHORS = (
    "阶段",
    "第1次咨询",
    "第2次咨询",
    "第3次咨询",
    "会谈",
    "咨询目标",
    "家庭作业",
    "作业",
    "工作表",
    "清单",
    "安全计划",
    "复发预防",
    "苏格拉底",
    "现实检验",
    "思维记录",
    "认知重构",
    "行为激活",
    "危机干预",
    "风险评估",
    "表格",
    "stage",
    "session",
    "goal",
    "homework",
    "worksheet",
    "safety plan",
    "relapse prevention",
    "socratic",
    "reality testing",
    "thought record",
    "cognitive restructuring",
    "behavioral activation",
    "crisis intervention",
    "risk assessment",
)

_DIALOGUE_LINE_RE = re.compile(
    r"^\s*(咨询师|来访者|治疗师|个案|访谈者|interviewer|therapist|counselor|client|patient)\s*[:：]",
    re.IGNORECASE,
)
_BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_REFERENCE_LINE_RE = re.compile(
    r"^\s*(?:\[\d+\]|\(\d+\)|\d+\.\s+.+\b(?:19|20)\d{2}[a-z]?\b.+|.+\bdoi\b.+|https?://\S+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParagraphBlock:
    """One paragraph-like block inside a section."""

    index: int
    text: str
    span: TextSpan
    anchor_hits: Tuple[str, ...]


def _noise_section_markers() -> List[str]:
    return dedupe_strings(list(_DEFAULT_NOISE_SECTION_MARKERS), lower=True)


def _priority_markers() -> List[str]:
    return dedupe_strings(list(_DEFAULT_PRIORITY_MARKERS), lower=True)


def _anchor_markers() -> List[str]:
    return dedupe_strings(list(_DEFAULT_ANCHORS), lower=True)


def _paragraphs_from_section(section: DocumentSection) -> List[Tuple[str, TextSpan]]:
    body = str(section.text or "")
    if not body.strip():
        return []
    pieces = [piece.strip() for piece in re.split(r"\n\s*\n+", body) if piece.strip()]
    out: List[Tuple[str, TextSpan]] = []
    cursor = 0
    for piece in pieces:
        idx = body.find(piece, cursor)
        if idx < 0:
            idx = cursor
        start = int(section.span.start or 0) + idx
        end = start + len(piece)
        out.append((piece, TextSpan(start=start, end=end)))
        cursor = idx + len(piece)
    return out


def _trimmed_slice_bounds(text: str, *, start: int, end: int) -> Tuple[int, int]:
    """Trims whitespace around one slice while preserving source-relative offsets."""

    safe_start = max(0, min(int(start or 0), len(text)))
    safe_end = max(safe_start, min(int(end or 0), len(text)))
    while safe_start < safe_end and text[safe_start].isspace():
        safe_start += 1
    while safe_end > safe_start and text[safe_end - 1].isspace():
        safe_end -= 1
    return safe_start, safe_end


def _preferred_split_offset(text: str, *, start: int, max_chars: int) -> int:
    """Finds a human-readable split boundary near the target size."""

    end = min(len(text), start + max_chars)
    if end >= len(text):
        return len(text)
    window = text[start:end]
    floor = max(0, int(max_chars * 0.6))
    for marker in ("\n\n", "\n", "。", "！", "？", ".", ";", "；"):
        rel = window.rfind(marker)
        if rel >= floor:
            return min(len(text), start + rel + len(marker))
    return end


def _split_long_section(section: DocumentSection, *, max_chars: int) -> List[DocumentSection]:
    """Splits one oversized section into pseudo-sections before final window planning."""

    src = str(section.text or "")
    safe_max = max(1000, int(max_chars or 0))
    if not src.strip() or len(src) <= safe_max:
        return [section]

    bounds: List[Tuple[int, int]] = []
    cursor = 0
    while cursor < len(src):
        split_end = _preferred_split_offset(src, start=cursor, max_chars=safe_max)
        if split_end <= cursor:
            split_end = min(len(src), cursor + safe_max)
        chunk_start, chunk_end = _trimmed_slice_bounds(src, start=cursor, end=split_end)
        if chunk_end > chunk_start:
            bounds.append((chunk_start, chunk_end))
        cursor = split_end

    if len(bounds) <= 1:
        return [section]

    original_start = int(section.span.start or 0)
    original_end = int(section.span.end or 0)
    base_md = dict(section.metadata or {})
    total = len(bounds)
    out: List[DocumentSection] = []
    for idx, (chunk_start, chunk_end) in enumerate(bounds, start=1):
        payload = section.to_dict()
        md: Dict[str, object] = dict(base_md)
        md["section_chunk_index"] = idx
        md["section_chunk_count"] = total
        md["section_chunk_span"] = {"start": chunk_start, "end": chunk_end}
        md["original_section_span"] = {"start": original_start, "end": original_end}
        payload["text"] = src[chunk_start:chunk_end].strip()
        payload["span"] = TextSpan(start=original_start + chunk_start, end=original_start + chunk_end).to_dict()
        payload["metadata"] = md
        out.append(DocumentSection.from_dict(payload))
    return out


def _is_noise_section(section: DocumentSection, *, markers: Sequence[str]) -> bool:
    heading = normalize_text(section.heading, lower=True)
    if any(marker in heading for marker in markers if marker):
        return True
    return _looks_like_reference_body(section.text)


def _looks_like_reference_body(text: str) -> bool:
    """Detects bibliography-like bodies even when the heading is noisy or missing."""

    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if len(lines) < 4:
        return False
    hits = 0
    for line in lines[:80]:
        if _REFERENCE_LINE_RE.search(line):
            hits += 1
    return hits >= max(3, int(len(lines) * 0.45))


def _is_dialogue_heavy(text: str) -> bool:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if len(lines) < 3:
        return False
    hits = sum(1 for line in lines if _DIALOGUE_LINE_RE.search(line))
    return hits >= 2 and hits >= max(2, len(lines) - 1)


def _has_process_signal(text: str, *, priority_markers: Sequence[str], anchor_markers: Sequence[str]) -> bool:
    normalized = normalize_text(text, lower=True)
    if _BULLET_RE.search(text):
        return True
    return any(marker in normalized for marker in list(priority_markers) + list(anchor_markers) if marker)


def _anchor_hits(text: str, *, anchor_markers: Sequence[str]) -> Tuple[str, ...]:
    normalized = normalize_text(text, lower=True)
    hits = [marker for marker in anchor_markers if marker and marker in normalized]
    return tuple(dedupe_strings(hits, lower=True))


def _build_paragraph_blocks(
    section: DocumentSection,
    *,
    anchor_markers: Sequence[str],
    priority_markers: Sequence[str],
) -> List[ParagraphBlock]:
    blocks: List[ParagraphBlock] = []
    for idx, (text, span) in enumerate(_paragraphs_from_section(section)):
        if _is_dialogue_heavy(text):
            continue
        hits = _anchor_hits(text, anchor_markers=anchor_markers)
        if hits or _has_process_signal(text, priority_markers=priority_markers, anchor_markers=anchor_markers):
            blocks.append(ParagraphBlock(index=idx, text=text, span=span, anchor_hits=hits))
        elif len(text) <= 320:
            blocks.append(ParagraphBlock(index=idx, text=text, span=span, anchor_hits=hits))
    return blocks


def _group_indices(blocks: Sequence[ParagraphBlock], *, priority_markers: Sequence[str], anchor_markers: Sequence[str]) -> List[Tuple[int, int]]:
    process_positions = [
        idx
        for idx, block in enumerate(blocks)
        if block.anchor_hits or _has_process_signal(block.text, priority_markers=priority_markers, anchor_markers=anchor_markers)
    ]
    if not process_positions:
        return []
    groups: List[Tuple[int, int]] = []
    start = process_positions[0]
    end = start
    for pos in process_positions[1:]:
        if pos <= end + 1:
            end = pos
            continue
        groups.append((start, end))
        start = pos
        end = pos
    groups.append((start, end))
    return groups


def _bounded_fallback_windows(
    *,
    record: DocumentRecord,
    section: DocumentSection,
    blocks: Sequence[ParagraphBlock],
    effective_strategy: str,
    max_chars: int,
) -> List[StrictWindow]:
    windows: List[StrictWindow] = []
    current: List[ParagraphBlock] = []
    current_chars = 0
    for block in blocks:
        projected = current_chars + (2 if current else 0) + len(block.text)
        if current and projected > max_chars:
            windows.append(_window_from_blocks(record=record, section=section, blocks=current, effective_strategy=effective_strategy))
            current = [block]
            current_chars = len(block.text)
            continue
        current.append(block)
        current_chars = projected
    if current:
        windows.append(_window_from_blocks(record=record, section=section, blocks=current, effective_strategy=effective_strategy))
    return windows


def _window_from_blocks(
    *,
    record: DocumentRecord,
    section: DocumentSection,
    blocks: Sequence[ParagraphBlock],
    effective_strategy: str,
) -> StrictWindow:
    text = "\n\n".join(block.text for block in blocks if str(block.text or "").strip()).strip()
    start = min(block.span.start for block in blocks)
    end = max(block.span.end for block in blocks)
    paragraph_start = min(block.index for block in blocks)
    paragraph_end = max(block.index for block in blocks)
    anchor_hits = dedupe_strings(
        [hit for block in blocks for hit in list(block.anchor_hits or [])],
        lower=True,
    )
    source_file = str((record.metadata or {}).get("source_file") or "").strip()
    section_md = dict(section.metadata or {})
    heading_path = list(section_md.get("heading_path") or [section.heading])
    parent_heading = str(section_md.get("parent_heading") or "").strip()
    key = f"{record.doc_id}:{section.heading}:{paragraph_start}:{paragraph_end}:{effective_strategy}"
    return StrictWindow(
        window_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill4doc-window:{key}")),
        doc_id=record.doc_id,
        source_file=source_file,
        unit_title=record.title,
        section_heading=section.heading,
        section_level=section.level,
        paragraph_start=paragraph_start,
        paragraph_end=paragraph_end,
        anchor_hits=anchor_hits,
        text=text,
        span=TextSpan(start=start, end=end),
        strategy=effective_strategy,
        metadata={
            "section_heading": section.heading,
            "effective_strategy": effective_strategy,
            "source_file": source_file,
            "heading_path": heading_path,
            "parent_heading": parent_heading,
            "sibling_headings": list(section_md.get("sibling_headings") or []),
            "subsection_headings": list(section_md.get("subsection_headings") or []),
            "heading_number": str(section_md.get("heading_number") or "").strip(),
            "heading_kind": str(section_md.get("heading_kind") or "").strip(),
            "section_summary": str(section_md.get("section_summary") or "").strip(),
            "section_chunk_index": int(section_md.get("section_chunk_index") or 0),
            "section_chunk_count": int(section_md.get("section_chunk_count") or 0),
            "section_chunk_span": dict(section_md.get("section_chunk_span") or {}),
            "original_section_span": dict(section_md.get("original_section_span") or {}),
        },
    )


def _section_context_snippets(sections: Sequence[DocumentSection]) -> Dict[Tuple[str, int, int], Dict[str, object]]:
    """Builds cheap hierarchy context from sibling sections without LLM calls."""

    sibling_groups: Dict[Tuple[str, ...], List[DocumentSection]] = {}
    for section in list(sections or []):
        md = dict(section.metadata or {})
        path = list(md.get("heading_path") or [section.heading])
        sibling_groups.setdefault(tuple(path[:-1]), []).append(section)

    out: Dict[Tuple[str, int, int], Dict[str, object]] = {}
    for section in list(sections or []):
        md = dict(section.metadata or {})
        path = list(md.get("heading_path") or [section.heading])
        siblings = [
            sibling
            for sibling in sibling_groups.get(tuple(path[:-1]), [])
            if sibling.heading != section.heading
        ]
        sibling_headings = [sibling.heading for sibling in siblings][:6]
        sibling_summaries = [
            f"{sibling.heading}: {str((sibling.metadata or {}).get('section_summary') or '').strip()}"
            for sibling in siblings[:3]
            if str((sibling.metadata or {}).get("section_summary") or "").strip()
        ]
        out[(section.heading, int(section.span.start or 0), int(section.span.end or 0))] = {
            "heading_path": path,
            "parent_heading": str(md.get("parent_heading") or "").strip(),
            "sibling_headings": sibling_headings,
            "context_snippets": sibling_summaries,
            "heading_number": str(md.get("heading_number") or "").strip(),
            "heading_kind": str(md.get("heading_kind") or "").strip(),
            "section_summary": str(md.get("section_summary") or "").strip(),
        }
    return out


def _root_heading_path(section: DocumentSection) -> List[str]:
    """Returns the normalized root heading path used for grouping planning sections."""

    md = dict(section.metadata or {})
    path = [str(item).strip() for item in list(md.get("heading_path") or []) if str(item).strip()]
    if path:
        return [path[0]]
    heading = str(section.heading or "").strip()
    return [heading] if heading else []


def _build_planning_section(group: Sequence[DocumentSection]) -> DocumentSection:
    """Builds one root-level planning section from one contiguous section group."""

    sections = list(group or [])
    if not sections:
        raise ValueError("planning section group cannot be empty")
    first = sections[0]
    root_path = _root_heading_path(first)
    root_heading = root_path[0] if root_path else str(first.heading or "").strip() or "Section"
    subsection_headings: List[str] = []
    subsection_summaries: List[str] = []
    body_parts: List[str] = []
    for section in sections:
        section_md = dict(section.metadata or {})
        path = [str(item).strip() for item in list(section_md.get("heading_path") or []) if str(item).strip()]
        current_heading = str(section.heading or "").strip()
        text = str(section.text or "").strip()
        if not text:
            continue
        is_subsection = bool(path) and path[0] == root_heading and len(path) > 1
        if is_subsection:
            subsection_headings.append(current_heading)
            body_parts.append(f"{current_heading}\n{text}")
        else:
            body_parts.append(text)
        summary = str(section_md.get("section_summary") or "").strip()
        if current_heading and summary:
            subsection_summaries.append(f"{current_heading}: {summary}")
    combined_text = "\n\n".join(part for part in body_parts if part).strip()
    if not combined_text:
        combined_text = "\n\n".join(str(section.text or "").strip() for section in sections if str(section.text or "").strip()).strip()
    root_md = dict(first.metadata or {})
    root_md["heading_path"] = [root_heading]
    root_md["parent_heading"] = ""
    root_md["subsection_headings"] = dedupe_strings(subsection_headings, lower=False)
    root_md["context_snippets"] = dedupe_strings(subsection_summaries, lower=False)[:6]
    root_md["grouped_section_count"] = len(sections)
    root_md["heading_kind"] = str(root_md.get("heading_kind") or ("grouped_root" if len(sections) > 1 else "")).strip()
    root_md["section_summary"] = str(root_md.get("section_summary") or "").strip() or combined_text[:180]
    return DocumentSection(
        heading=root_heading,
        text=combined_text,
        level=1,
        span=TextSpan(
            start=min(int(section.span.start or 0) for section in sections),
            end=max(int(section.span.end or 0) for section in sections),
        ),
        metadata=root_md,
    )


def _planning_sections(sections: Sequence[DocumentSection]) -> List[DocumentSection]:
    """Groups contiguous subsections under their top-level heading for window planning."""

    ordered = list(sections or [])
    if not ordered:
        return []
    out: List[DocumentSection] = []
    current_group: List[DocumentSection] = []
    current_root = ""
    for section in ordered:
        root_heading = (_root_heading_path(section) or [str(section.heading or "").strip()])[0]
        if not current_group or root_heading == current_root:
            current_group.append(section)
            current_root = root_heading
            continue
        out.append(_build_planning_section(current_group))
        current_group = [section]
        current_root = root_heading
    if current_group:
        out.append(_build_planning_section(current_group))
    return out


def _effective_strategy(strategy: str) -> str:
    raw = normalize_extract_strategy(strategy)
    if raw in {"recommended", "strict", ""}:
        return "strict"
    return "chunk"


def build_windows_for_record(
    record: DocumentRecord,
    *,
    strategy: str = "recommended",
    max_chars: int = 2400,
    max_section_chars: int = 10000,
) -> List[StrictWindow]:
    """Builds strict/recommended windows for one normalized document."""

    noise_markers = _noise_section_markers()
    priority_markers = _priority_markers()
    anchor_markers = _anchor_markers()
    effective_strategy = _effective_strategy(strategy)
    windows: List[StrictWindow] = []
    planning_sections = _planning_sections(list(record.sections or []))
    section_context = _section_context_snippets(planning_sections)

    for section in planning_sections:
        if _is_noise_section(section, markers=noise_markers):
            continue
        context = dict(section_context.get((section.heading, int(section.span.start or 0), int(section.span.end or 0))) or {})
        if context:
            payload = section.to_dict()
            md = dict(payload.get("metadata") or {})
            md.update(context)
            payload["metadata"] = md
            section = DocumentSection.from_dict(payload)
        for section_chunk in _split_long_section(section, max_chars=max_section_chars):
            blocks = _build_paragraph_blocks(section_chunk, anchor_markers=anchor_markers, priority_markers=priority_markers)
            if not blocks:
                continue
            if effective_strategy != "strict":
                windows.extend(
                    _bounded_fallback_windows(
                        record=record,
                        section=section_chunk,
                        blocks=blocks,
                        effective_strategy=effective_strategy,
                        max_chars=max_chars,
                    )
                )
                continue

            groups = _group_indices(blocks, priority_markers=priority_markers, anchor_markers=anchor_markers)
            if not groups:
                windows.extend(
                    _bounded_fallback_windows(
                        record=record,
                        section=section_chunk,
                        blocks=blocks,
                        effective_strategy=effective_strategy,
                        max_chars=max_chars,
                    )
                )
                continue

            for start_idx, end_idx in groups:
                left = max(0, start_idx - 1)
                right = min(len(blocks) - 1, end_idx + 1)
                selected = list(blocks[left : right + 1])
                text_len = len("\n\n".join(block.text for block in selected))
                while text_len > max_chars and len(selected) > 1:
                    if len(selected[0].text) >= len(selected[-1].text):
                        selected = selected[1:]
                    else:
                        selected = selected[:-1]
                    text_len = len("\n\n".join(block.text for block in selected))
                if selected:
                    windows.append(
                        _window_from_blocks(
                            record=record,
                            section=section_chunk,
                            blocks=selected,
                            effective_strategy=effective_strategy,
                        )
                    )

    return windows
