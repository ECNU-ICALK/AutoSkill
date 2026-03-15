"""
Strict/recommended window planning for AutoSkill4Doc.

The goal is not equal-sized chunks. The goal is to preserve local, reusable
task blocks that are more likely to yield one clean child skill candidate.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import List, Sequence, Tuple

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


def _is_noise_section(section: DocumentSection, *, markers: Sequence[str]) -> bool:
    heading = normalize_text(section.heading, lower=True)
    return any(marker in heading for marker in markers if marker)


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
        },
    )


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
) -> List[StrictWindow]:
    """Builds strict/recommended windows for one normalized document."""

    noise_markers = _noise_section_markers()
    priority_markers = _priority_markers()
    anchor_markers = _anchor_markers()
    effective_strategy = _effective_strategy(strategy)
    windows: List[StrictWindow] = []

    for section in list(record.sections or []):
        if _is_noise_section(section, markers=noise_markers):
            continue
        blocks = _build_paragraph_blocks(section, anchor_markers=anchor_markers, priority_markers=priority_markers)
        if not blocks:
            continue
        if effective_strategy != "strict":
            windows.extend(
                _bounded_fallback_windows(
                    record=record,
                    section=section,
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
                    section=section,
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
                        section=section,
                        blocks=selected,
                        effective_strategy=effective_strategy,
                    )
                )

    return windows
