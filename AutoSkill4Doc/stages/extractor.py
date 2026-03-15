"""
LLM-driven skill extraction stage for the offline document pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
import uuid
from typing import Callable, Dict, List, Optional, Protocol, Tuple

from autoskill.llm.base import LLM
from autoskill.llm.factory import build_llm
from autoskill.models import SkillExample

from ..core.common import StageLogger, document_progress_label, emit_stage_log, normalize_text, summarize_names
from ..core.llm_utils import (
    clip_confidence,
    coerce_str_list,
    compact_text_list,
    llm_complete_json,
    maybe_json_dict,
    section_items_from_prompt,
)
from ..models import (
    DocumentRecord,
    SkillDraft,
    StrictWindow,
    SupportRecord,
    SupportRelation,
    TextSpan,
)
from ..prompts import OFFLINE_CHANNEL_DOC, maybe_offline_prompt

_WORKFLOW_PATTERNS = [r"^\s*[\-\*\u2022]\s+", r"^\s*\d+[\.\)]\s+"]
_DEFAULT_SECTION_CHARS = 2400
_DEFAULT_CHUNK_OVERLAP_CHARS = 200
_DEFAULT_MAX_CANDIDATES_PER_UNIT = 3
_DEFAULT_SECTION_PRIORITY_TERMS = (
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
    "workflow",
    "step-by-step",
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
    "流程",
    "步骤",
)
_DEFAULT_SECTION_DEPRIORITIZE_TERMS = (
    "demographics",
    "growth history",
    "background",
    "abstract",
    "summary",
    "keywords",
    "references",
    "reference",
    "bibliography",
    "appendix",
    "author contributions",
    "funding",
    "acknowledg",
    "ethics",
    "conflict of interest",
    "人口统计",
    "成长史",
    "背景",
    "摘要",
    "关键词",
    "参考文献",
    "附录",
    "基金",
    "致谢",
    "伦理",
    "利益冲突",
)


def _split_section_blocks(text: str) -> List[str]:
    """Splits one section into paragraph-like blocks before fallback chunking."""

    src = str(text or "").strip()
    if not src:
        return []
    blocks: List[str] = []
    for paragraph in [p.strip() for p in src.split("\n\n") if p.strip()]:
        lines = [ln.strip() for ln in paragraph.splitlines() if ln.strip()]
        bullet_lines = [ln for ln in lines if any(re.search(pattern, ln) for pattern in _WORKFLOW_PATTERNS)]
        if bullet_lines and len(bullet_lines) == len(lines):
            blocks.extend(bullet_lines)
            continue
        blocks.append(paragraph)
    return blocks


def _text_span(record: DocumentRecord, *, section_start: int, text: str, cursor: int) -> TextSpan:
    """Builds a best-effort source span for one extracted text unit."""

    raw = str(record.raw_text or "")
    target = str(text or "").strip()
    if not target:
        return TextSpan(start=section_start, end=section_start)
    idx = raw.find(target, max(0, int(cursor)))
    if idx < 0:
        idx = raw.find(target, max(0, int(section_start)))
    if idx < 0:
        idx = max(0, int(section_start))
    return TextSpan(start=idx, end=idx + len(target))


def _split_text_windows(text: str, *, max_chars: int, overlap_chars: int) -> List[str]:
    """Splits a long text into overlapping windows."""

    src = str(text or "").strip()
    if not src:
        return []
    if len(src) <= max_chars:
        return [src]

    safe_max = max(80, int(max_chars or 0))
    safe_overlap = max(0, min(int(overlap_chars or 0), safe_max // 3))
    step = max(40, safe_max - safe_overlap)
    out: List[str] = []
    start = 0
    while start < len(src):
        end = min(len(src), start + safe_max)
        chunk = src[start:end].strip()
        if chunk:
            out.append(chunk)
        if end >= len(src):
            break
        start = end - safe_overlap
    return out


def _plan_section_units(
    *,
    record: DocumentRecord,
    section_text: str,
    section_start: int,
    section_span: TextSpan,
    max_section_chars: int,
    overlap_chars: int,
) -> List[Tuple[str, TextSpan, str]]:
    """Plans extraction units for one section."""

    src = str(section_text or "").strip()
    if not src:
        return []
    if len(src) <= max_section_chars:
        return [(src, section_span, "section")]

    blocks = _split_section_blocks(src) or [src]
    grouped_texts: List[str] = []
    current_blocks: List[str] = []
    current_size = 0
    for raw_block in blocks:
        block = str(raw_block or "").strip()
        if not block:
            continue
        if len(block) > max_section_chars:
            if current_blocks:
                grouped_texts.append("\n\n".join(current_blocks))
                current_blocks = []
                current_size = 0
            grouped_texts.extend(
                _split_text_windows(
                    block,
                    max_chars=max_section_chars,
                    overlap_chars=overlap_chars,
                )
            )
            continue
        projected = current_size + (2 if current_blocks else 0) + len(block)
        if current_blocks and projected > max_section_chars:
            grouped_texts.append("\n\n".join(current_blocks))
            current_blocks = [block]
            current_size = len(block)
            continue
        current_blocks.append(block)
        current_size = projected

    if current_blocks:
        grouped_texts.append("\n\n".join(current_blocks))

    units: List[Tuple[str, TextSpan, str]] = []
    cursor = int(section_start or 0)
    for text in grouped_texts or _split_text_windows(src, max_chars=max_section_chars, overlap_chars=overlap_chars):
        span = _text_span(record, section_start=section_start, text=text, cursor=cursor)
        cursor = int(span.end or cursor)
        units.append((text, span, "chunk"))
    return units


def _default_section_priority_terms() -> List[str]:
    """Returns normalized built-in terms for budget-aware section ordering."""

    return compact_text_list(list(_DEFAULT_SECTION_PRIORITY_TERMS), limit=64)


def _default_section_deprioritize_terms() -> List[str]:
    """Returns normalized built-in low-value section terms."""

    return compact_text_list(list(_DEFAULT_SECTION_DEPRIORITIZE_TERMS), limit=64)


def _section_priority_score(
    *,
    heading: str,
    text: str,
    priority_terms: List[str],
    deprioritize_terms: List[str],
) -> int:
    """Scores a section heading/body for budget-aware extraction ordering."""

    heading_text = normalize_text(str(heading or ""), lower=True)
    preview_text = normalize_text(str(text or "")[:600], lower=True)
    score = 0
    for term in priority_terms:
        token = normalize_text(term, lower=True)
        if not token:
            continue
        if token in heading_text:
            score += 6
        elif token in preview_text:
            score += 2
    for term in deprioritize_terms:
        token = normalize_text(term, lower=True)
        if not token:
            continue
        if token in heading_text:
            score -= 6
        elif token in preview_text:
            score -= 2
    return score


def _ordered_sections_for_budget(record: DocumentRecord, *, max_units_per_document: int) -> List[object]:
    """Reorders sections when a unit budget is active so higher-value sections go first."""

    sections = list(record.sections or [])
    if max_units_per_document <= 0 or not sections:
        return sections
    priority_terms = _default_section_priority_terms()
    deprioritize_terms = _default_section_deprioritize_terms()
    if not priority_terms and not deprioritize_terms:
        return sections
    ranked: List[Tuple[int, int, object]] = []
    for idx, section in enumerate(sections):
        score = _section_priority_score(
            heading=getattr(section, "heading", ""),
            text=getattr(section, "text", ""),
            priority_terms=priority_terms,
            deprioritize_terms=deprioritize_terms,
        )
        ranked.append((score, idx, section))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [section for _, _, section in ranked]


def _coerce_relation(value: str) -> SupportRelation:
    """Coerces a model relation label into a supported enum."""

    raw = str(value or "").strip().lower()
    if raw == SupportRelation.CONFLICT.value:
        return SupportRelation.CONFLICT
    if raw == SupportRelation.CONSTRAINT.value:
        return SupportRelation.CONSTRAINT
    if raw == SupportRelation.CASE_VARIANT.value:
        return SupportRelation.CASE_VARIANT
    return SupportRelation.SUPPORT


def _coerce_risk_class(value: str) -> str:
    """Normalizes the risk class label."""

    raw = str(value or "").strip().lower()
    return raw if raw in {"low", "medium", "high"} else "low"


def _objective_from_item(item: Dict[str, object], prompt: str, description: str) -> str:
    """Builds a single-goal objective with prompt fallback."""

    explicit = str(item.get("objective") or "").strip()
    if explicit:
        return explicit
    extracted = section_items_from_prompt(
        prompt,
        [
            "goal",
            "objective",
            "role & objective",
            "target",
            "目标",
            "目的",
        ],
    )
    if extracted:
        return str(extracted[0] or "").strip()
    return str(description or "").strip()


def _applicable_signals_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds applicable client/context signals with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("applicable_signals")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "applicable signals",
            "signals",
            "when to use",
            "indications",
            "适用信号",
            "适用情形",
            "使用时机",
        ],
    )


def _contraindications_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds contraindications with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("contraindications")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "contraindications",
            "do not use when",
            "avoid when",
            "not for",
            "禁忌",
            "不适用",
        ],
    )


def _intervention_moves_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds therapist intervention moves with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("intervention_moves")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "intervention moves",
            "micro skills",
            "techniques",
            "response moves",
            "intervention",
            "干预动作",
            "微技能",
            "技术要点",
        ],
    )


def _workflow_steps_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds workflow steps with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("workflow_steps")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "workflow",
            "core workflow",
            "step-by-step",
            "步骤",
            "流程",
            "核心流程",
        ],
    )


def _constraint_items_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds constraint items with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("constraints")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "rules",
            "constraints",
            "rules & constraints",
            "约束",
            "规则",
            "限制",
        ],
    )


def _caution_items_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds caution items with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("cautions")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "cautions",
            "anti-patterns",
            "warnings",
            "注意",
            "风险",
            "禁忌",
        ],
    )


def _output_contract_from_item(item: Dict[str, object], prompt: str) -> List[str]:
    """Builds output requirements with prompt-based fallback."""

    explicit = compact_text_list(coerce_str_list(item.get("output_contract")), limit=12)
    if explicit:
        return explicit
    return section_items_from_prompt(
        prompt,
        [
            "output",
            "output format",
            "deliverable",
            "输出",
            "输出格式",
            "交付",
        ],
    )


def _examples_from_item(item: Dict[str, object]) -> List[SkillExample]:
    """Builds short therapist-response examples from the model payload."""

    raw = item.get("examples")
    if raw is None:
        return []
    items = list(raw) if isinstance(raw, list) else [raw]
    out: List[SkillExample] = []
    for entry in items[:3]:
        if isinstance(entry, SkillExample):
            out.append(entry)
            continue
        if not isinstance(entry, dict):
            continue
        input_text = str(entry.get("input") or entry.get("client") or entry.get("scenario") or "").strip()
        output_text = str(entry.get("output") or entry.get("therapist") or "").strip()
        notes_text = str(entry.get("notes") or "").strip()
        if not input_text or not output_text:
            continue
        out.append(
            SkillExample(
                input=input_text,
                output=output_text,
                notes=notes_text or None,
            )
        )
    return out


def _draft_identity_seed(*, doc_id: str, section: str, name: str, prompt: str, unit_key: str = "") -> str:
    """Builds a stable UUID seed for one extracted draft."""

    normalized = "|".join(
        [
            str(doc_id or "").strip(),
            normalize_text(section, lower=True),
            normalize_text(name, lower=True),
            normalize_text(prompt, lower=True),
            normalize_text(unit_key, lower=True),
        ]
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill-document-draft:{normalized}"))


@dataclass
class SkillExtractionResult:
    """Output of the direct skill extraction stage."""

    documents: List[DocumentRecord] = field(default_factory=list)
    windows: List[StrictWindow] = field(default_factory=list)
    support_records: List[SupportRecord] = field(default_factory=list)
    skill_drafts: List[SkillDraft] = field(default_factory=list)
    errors: List[Dict[str, str]] = field(default_factory=list)
    extractor_name: str = "llm"


ExtractionProgressCallback = Optional[
    Callable[[DocumentRecord, List[SupportRecord], List[SkillDraft], SkillExtractionResult], None]
]


class DocumentSkillExtractor(Protocol):
    """Pluggable document-to-skill extractor interface."""

    def extract(
        self,
        *,
        documents: List[DocumentRecord],
        windows: Optional[List[StrictWindow]],
        logger: StageLogger,
        progress_callback: ExtractionProgressCallback = None,
    ) -> SkillExtractionResult:
        """Extracts support records and skill drafts from normalized documents."""


class LLMDocumentSkillExtractor:
    """Model-driven document-to-skill extractor."""

    def __init__(
        self,
        *,
        llm: Optional[LLM] = None,
        llm_config: Optional[Dict[str, object]] = None,
        max_section_chars: int = _DEFAULT_SECTION_CHARS,
        overlap_chars: int = _DEFAULT_CHUNK_OVERLAP_CHARS,
        max_candidates_per_unit: int = _DEFAULT_MAX_CANDIDATES_PER_UNIT,
        max_units_per_document: int = 0,
    ) -> None:
        self._llm = llm or build_llm(dict(llm_config or {"provider": "mock"}))
        self.max_section_chars = max(200, int(max_section_chars or _DEFAULT_SECTION_CHARS))
        self.overlap_chars = max(0, int(overlap_chars or 0))
        self.max_candidates_per_unit = max(1, int(max_candidates_per_unit or _DEFAULT_MAX_CANDIDATES_PER_UNIT))
        self.max_units_per_document = max(0, int(max_units_per_document or 0))

    def _extract_unit_skills(
        self,
        *,
        record: DocumentRecord,
        section_heading: str,
        section_level: int,
        span: TextSpan,
        unit_text: str,
        unit_type: str,
    ) -> List[Dict[str, object]]:
        payload = {
            "document": {
                "doc_id": record.doc_id,
                "title": record.title,
                "domain": record.domain,
                "source_type": record.source_type,
                "authors": list(record.authors or []),
                "year": record.year,
                "metadata": dict(record.metadata or {}),
            },
            "section": {
                "heading": section_heading,
                "level": section_level,
                "span": span.to_dict(),
                "unit_type": unit_type,
            },
            "excerpt": str(unit_text or "").strip(),
            "max_candidates": self.max_candidates_per_unit,
        }
        system = maybe_offline_prompt(
            channel=OFFLINE_CHANNEL_DOC,
            kind="extract",
            max_candidates=self.max_candidates_per_unit,
        )
        repair_system = maybe_offline_prompt(
            channel=OFFLINE_CHANNEL_DOC,
            kind="repair",
            max_candidates=self.max_candidates_per_unit,
        )
        repaired_payload = (
            f"DATA:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            f"DRAFT:\n__DRAFT__"
        )
        parsed = llm_complete_json(
            llm=self._llm,
            system=system,
            payload=payload,
            repair_system=repair_system,
            repair_payload=repaired_payload,
        )
        obj = maybe_json_dict(parsed)
        raw_skills = obj.get("skills") if isinstance(obj.get("skills"), list) else parsed
        if not isinstance(raw_skills, list):
            return []
        return [maybe_json_dict(item) for item in raw_skills if isinstance(item, dict)]

    def _build_support_and_draft(
        self,
        *,
        record: DocumentRecord,
        section_heading: str,
        span: TextSpan,
        unit_text: str,
        unit_type: str,
        item: Dict[str, object],
        unit_metadata: Optional[Dict[str, object]] = None,
    ) -> Tuple[Optional[SupportRecord], Optional[SkillDraft]]:
        name = str(item.get("name") or "").strip()
        description = str(item.get("description") or "").strip()
        prompt = str(item.get("prompt") or item.get("skill_body") or "").strip()
        if not name or not description or not prompt:
            return None, None

        objective = _objective_from_item(item, prompt, description)
        applicable_signals = _applicable_signals_from_item(item, prompt)
        contraindications = _contraindications_from_item(item, prompt)
        intervention_moves = _intervention_moves_from_item(item, prompt)
        workflow_steps = _workflow_steps_from_item(item, prompt)
        constraints = _constraint_items_from_item(item, prompt)
        cautions = _caution_items_from_item(item, prompt)
        output_contract = _output_contract_from_item(item, prompt)
        examples = _examples_from_item(item)
        if not workflow_steps and not intervention_moves and not constraints and not cautions:
            return None, None

        support_id = str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"autoskill-document-support:{record.doc_id}:{section_heading}:{span.start}:{span.end}:{name}:{normalize_text(unit_text, lower=True)}",
            )
        )
        tags = compact_text_list(coerce_str_list(item.get("tags")), limit=6)
        triggers = compact_text_list(coerce_str_list(item.get("triggers")), limit=5)
        draft = SkillDraft(
            draft_id=_draft_identity_seed(
                doc_id=record.doc_id,
                section=section_heading,
                name=name,
                prompt=prompt,
                unit_key=f"{unit_type}:{int(span.start or 0)}:{int(span.end or 0)}",
            ),
            doc_id=record.doc_id,
            name=name,
            description=description,
            asset_type=str(item.get("asset_type") or "").strip(),
            granularity=str(item.get("granularity") or "").strip(),
            objective=objective,
            domain=str(item.get("domain") or record.domain or "").strip(),
            task_family=str(item.get("task_family") or "").strip(),
            method_family=str(item.get("method_family") or "").strip(),
            stage=str(item.get("stage") or "").strip(),
            applicable_signals=applicable_signals,
            contraindications=contraindications,
            intervention_moves=intervention_moves,
            workflow_steps=workflow_steps,
            triggers=triggers,
            constraints=constraints,
            cautions=cautions,
            output_contract=output_contract,
            examples=examples,
            risk_class=_coerce_risk_class(str(item.get("risk_class") or "")),
            confidence=clip_confidence(item.get("confidence"), default=0.75),
            support_ids=[support_id],
            metadata={
                "prompt": prompt,
                "tags": tags,
                "files": maybe_json_dict(item.get("files")),
                "resources": maybe_json_dict(item.get("resources")),
                "source_sections": [section_heading],
                "extraction_unit": unit_type,
                **dict(unit_metadata or {}),
            },
        )
        relation_type = _coerce_relation(str(item.get("relation_type") or "support"))
        support = SupportRecord(
            support_id=support_id,
            doc_id=record.doc_id,
            source_file=str((record.metadata or {}).get("source_file") or ""),
            section=section_heading,
            span=span,
            excerpt=str(unit_text or "").strip(),
            relation_type=relation_type,
            confidence=clip_confidence(item.get("confidence"), default=0.75),
            metadata={
                "document_title": record.title,
                "domain": record.domain,
                "extraction_unit": unit_type,
                "skill_name": name,
                "asset_type": draft.asset_type,
                "granularity": draft.granularity,
                "objective": draft.objective,
                "task_family": draft.task_family,
                "method_family": draft.method_family,
                "stage": draft.stage,
                **dict(unit_metadata or {}),
            },
        )
        return support, draft

    def _extract_from_windows(
        self,
        *,
        record: DocumentRecord,
        windows: List[StrictWindow],
    ) -> Tuple[List[SupportRecord], List[SkillDraft]]:
        supports: List[SupportRecord] = []
        drafts: List[SkillDraft] = []
        active_windows = list(windows or [])
        if self.max_units_per_document > 0:
            active_windows = active_windows[: self.max_units_per_document]
        for window in active_windows:
            raw_skills = self._extract_unit_skills(
                record=record,
                section_heading=window.section_heading,
                section_level=window.section_level,
                span=window.span,
                unit_text=window.text,
                unit_type="window",
            )
            for item in raw_skills:
                support, draft = self._build_support_and_draft(
                    record=record,
                    section_heading=window.section_heading,
                    span=window.span,
                    unit_text=window.text,
                    unit_type="window",
                    item=item,
                    unit_metadata={
                        "window_id": window.window_id,
                        "window_strategy": window.strategy,
                        "anchor_hits": list(window.anchor_hits or []),
                        "paragraph_start": window.paragraph_start,
                        "paragraph_end": window.paragraph_end,
                    },
                )
                if support is None or draft is None:
                    continue
                supports.append(support)
                drafts.append(draft)
        deduped_supports = {support.support_id: support for support in supports}
        deduped_drafts = {draft.draft_id: draft for draft in drafts}
        return list(deduped_supports.values()), list(deduped_drafts.values())

    def _extract_from_document(self, record: DocumentRecord) -> Tuple[List[SupportRecord], List[SkillDraft]]:
        supports: List[SupportRecord] = []
        drafts: List[SkillDraft] = []
        units_seen = 0
        ordered_sections = _ordered_sections_for_budget(
            record,
            max_units_per_document=self.max_units_per_document,
        )
        for section in ordered_sections:
            section_text = str(section.text or "").strip()
            if not section_text:
                continue
            extraction_units = _plan_section_units(
                record=record,
                section_text=section_text,
                section_start=int(section.span.start or 0),
                section_span=section.span,
                max_section_chars=self.max_section_chars,
                overlap_chars=self.overlap_chars,
            )
            for unit_text, span, unit_type in extraction_units:
                if self.max_units_per_document > 0 and units_seen >= self.max_units_per_document:
                    break
                units_seen += 1
                raw_skills = self._extract_unit_skills(
                    record=record,
                    section_heading=section.heading,
                    section_level=section.level,
                    span=span,
                    unit_text=unit_text,
                    unit_type=unit_type,
                )
                for item in raw_skills:
                    support, draft = self._build_support_and_draft(
                        record=record,
                        section_heading=section.heading,
                        span=span,
                        unit_text=unit_text,
                        unit_type=unit_type,
                        item=item,
                    )
                    if support is None or draft is None:
                        continue
                    supports.append(support)
                    drafts.append(draft)
            if self.max_units_per_document > 0 and units_seen >= self.max_units_per_document:
                break

        deduped_supports = {support.support_id: support for support in supports}
        deduped_drafts = {draft.draft_id: draft for draft in drafts}
        return list(deduped_supports.values()), list(deduped_drafts.values())

    def extract(
        self,
        *,
        documents: List[DocumentRecord],
        windows: Optional[List[StrictWindow]],
        logger: StageLogger,
        progress_callback: ExtractionProgressCallback = None,
    ) -> SkillExtractionResult:
        result = SkillExtractionResult(
            documents=list(documents or []),
            windows=list(windows or []),
            extractor_name="llm",
        )
        windows_by_doc: Dict[str, List[StrictWindow]] = {}
        for window in list(windows or []):
            doc_id = str(window.doc_id or "").strip()
            if doc_id:
                windows_by_doc.setdefault(doc_id, []).append(window)
        for record in documents or []:
            try:
                doc_windows = list(windows_by_doc.get(str(record.doc_id or "").strip(), []))
                emit_stage_log(
                    logger,
                    f"[extract_skills] start {document_progress_label(doc_id=record.doc_id, title=record.title, source_file=str((record.metadata or {}).get('source_file') or ''))}",
                )
                if doc_windows:
                    supports, drafts = self._extract_from_windows(record=record, windows=doc_windows)
                else:
                    supports, drafts = self._extract_from_document(record)
                result.support_records.extend(supports)
                result.skill_drafts.extend(drafts)
                if progress_callback is not None:
                    progress_callback(record, list(supports or []), list(drafts or []), result)
                emit_stage_log(
                    logger,
                    f"[extract_skills] done {document_progress_label(doc_id=record.doc_id, title=record.title, source_file=str((record.metadata or {}).get('source_file') or ''))} windows={len(doc_windows)} supports={len(supports)} drafts={len(drafts)} names={summarize_names([draft.name for draft in drafts])}",
                )
            except Exception as e:
                result.errors.append({"doc_id": record.doc_id, "error": str(e)})
                emit_stage_log(logger, f"[extract_skills] error doc={record.doc_id}: {e}")
        return result


HeuristicDocumentSkillExtractor = LLMDocumentSkillExtractor


def build_document_skill_extractor(
    kind: str = "llm",
    *,
    llm: Optional[LLM] = None,
    llm_config: Optional[Dict[str, object]] = None,
    max_section_chars: int = _DEFAULT_SECTION_CHARS,
    overlap_chars: int = _DEFAULT_CHUNK_OVERLAP_CHARS,
    max_candidates_per_unit: int = _DEFAULT_MAX_CANDIDATES_PER_UNIT,
    max_units_per_document: int = 0,
) -> DocumentSkillExtractor:
    """Builds a concrete document-to-skill extractor implementation."""

    name = str(kind or "").strip().lower() or "llm"
    if name in {"llm", "heuristic", "stub", "rule-based", "rule_based"}:
        return LLMDocumentSkillExtractor(
            llm=llm,
            llm_config=llm_config,
            max_section_chars=max_section_chars,
            overlap_chars=overlap_chars,
            max_candidates_per_unit=max_candidates_per_unit,
            max_units_per_document=max_units_per_document,
        )
    raise ValueError(f"unsupported document skill extractor: {kind}")


def extract_skills(
    *,
    documents: List[DocumentRecord],
    windows: Optional[List[StrictWindow]] = None,
    extractor: DocumentSkillExtractor | None = None,
    logger: StageLogger = None,
    progress_callback: ExtractionProgressCallback = None,
) -> SkillExtractionResult:
    """Public functional wrapper for the direct skill extraction stage."""

    impl = extractor or LLMDocumentSkillExtractor()
    return impl.extract(
        documents=list(documents or []),
        windows=list(windows or []),
        logger=logger,
        progress_callback=progress_callback,
    )
