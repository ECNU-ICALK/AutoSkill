"""
Core models for the skill-first offline document pipeline.

The current document pipeline is organized around:
- DocumentRecord: normalized source document
- SupportRecord: lightweight support/conflict trace attached to a skill
- SkillDraft: extracted executable draft before batch normalization
- SkillSpec: canonicalized skill ready for versioning and store upsert
- SkillLifecycle: lifecycle transition recorded in the document registry

The models stay domain-agnostic. Domain-specific hints should live in metadata
or external domain profiles rather than hard-coded branches here.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
import json
import re
from typing import Any, Dict, List, Optional, Type, TypeVar

from autoskill.models import SkillExample
from autoskill.utils.time import now_iso
from .common import refine_asset_shape

T = TypeVar("T", bound="SerializableModel")

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _to_plain_data(value: Any) -> Any:
    """Converts dataclasses, enums, and containers into JSON-safe plain data."""

    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        out: Dict[str, Any] = {}
        for f in fields(value):
            out[f.name] = _to_plain_data(getattr(value, f.name))
        return out
    if isinstance(value, dict):
        return {str(k): _to_plain_data(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_plain_data(v) for v in value]
    return value


def _yaml_scalar(value: Any) -> str:
    """Renders one YAML scalar without depending on PyYAML."""

    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if "\n" in s:
        return ""
    if not s:
        return '""'
    if re.search(r"[:#\[\]\{\},&*!|>'\"%@`]", s) or s.strip() != s:
        return json.dumps(s, ensure_ascii=False)
    low = s.lower()
    if low in {"true", "false", "null", "~"}:
        return json.dumps(s, ensure_ascii=False)
    return s


def _to_yaml_lines(value: Any, *, indent: int = 0) -> List[str]:
    """Serializes plain data to a small YAML subset."""

    space = " " * indent
    if isinstance(value, dict):
        lines: List[str] = []
        for key, item in value.items():
            key_s = str(key)
            if isinstance(item, str) and "\n" in item:
                lines.append(f"{space}{key_s}: |-")
                for ln in item.splitlines():
                    lines.append(f"{space}  {ln}")
                if not item.splitlines():
                    lines.append(f"{space}  ")
                continue
            if isinstance(item, (dict, list)):
                lines.append(f"{space}{key_s}:")
                lines.extend(_to_yaml_lines(item, indent=indent + 2))
                continue
            lines.append(f"{space}{key_s}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, str) and "\n" in item:
                lines.append(f"{space}- |-")
                for ln in item.splitlines():
                    lines.append(f"{space}  {ln}")
                if not item.splitlines():
                    lines.append(f"{space}  ")
                continue
            if isinstance(item, (dict, list)):
                lines.append(f"{space}-")
                lines.extend(_to_yaml_lines(item, indent=indent + 2))
                continue
            lines.append(f"{space}- {_yaml_scalar(item)}")
        return lines
    return [f"{space}{_yaml_scalar(value)}"]


def _coerce_str_list(raw: Any) -> List[str]:
    """Normalizes arbitrary list-like content into stripped string lists."""

    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        return [str(v).strip() for v in raw if str(v).strip()]
    s = str(raw).strip()
    return [s] if s else []


def _coerce_str_dict(raw: Any) -> Dict[str, Any]:
    """Normalizes arbitrary mapping-like content into a mutable dict."""

    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items()}
    return {}


def _coerce_skill_examples(raw: Any) -> List[SkillExample]:
    """Normalizes example payloads into SkillExample objects."""

    if raw is None:
        return []
    items = list(raw) if isinstance(raw, (list, tuple)) else [raw]
    out: List[SkillExample] = []
    for item in items:
        if isinstance(item, SkillExample):
            if str(item.input or "").strip():
                out.append(
                    SkillExample(
                        input=str(item.input or "").strip(),
                        output=str(item.output or "").strip() or None,
                        notes=str(item.notes or "").strip() or None,
                    )
                )
            continue
        if isinstance(item, dict):
            input_text = str(item.get("input") or item.get("client") or item.get("scenario") or "").strip()
            output_text = str(item.get("output") or item.get("therapist") or "").strip() or None
            notes_text = str(item.get("notes") or item.get("rationale") or "").strip() or None
        else:
            input_text = str(item or "").strip()
            output_text = None
            notes_text = None
        if not input_text:
            continue
        out.append(SkillExample(input=input_text, output=output_text, notes=notes_text))
    return out


def _validate_semver(version: str, *, field_name: str) -> None:
    """Checks a semver-like string in MAJOR.MINOR.PATCH form."""

    if not _SEMVER_RE.match(str(version or "").strip()):
        raise ValueError(f"{field_name} must use semantic version format like 0.1.0")


def _validate_confidence(confidence: float, *, field_name: str = "confidence") -> None:
    """Checks that confidence scores stay within [0.0, 1.0]."""

    value = float(confidence)
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0")


class SerializableModel:
    """Small mixin for dataclass-backed JSON/YAML serialization."""

    def to_dict(self) -> Dict[str, Any]:
        """Returns a recursive plain-data representation."""

        return _to_plain_data(self)

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        """Serializes the model to a JSON string."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, sort_keys=False)

    def to_yaml(self) -> str:
        """Serializes the model to a YAML string without external dependencies."""

        return "\n".join(_to_yaml_lines(self.to_dict())) + "\n"

    @classmethod
    def from_json(cls: Type[T], text: str) -> T:
        """Deserializes the model from a JSON string."""

        obj = json.loads(str(text or "").strip() or "{}")
        if not isinstance(obj, dict):
            raise ValueError("JSON payload must decode into an object")
        return cls.from_dict(obj)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Builds the model from a plain dict."""

        raise NotImplementedError

    def validate(self) -> None:
        """Runs local invariants. Subclasses should override."""

        return None


class VersionState(str, Enum):
    """Lifecycle state for compiled skills and registry records."""

    CANDIDATE = "candidate"
    DRAFT = "draft"
    EVALUATING = "evaluating"
    ACTIVE = "active"
    WATCHLIST = "watchlist"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


def _coerce_version_state(value: Any, *, default: VersionState) -> VersionState:
    """Parses lifecycle state strings into VersionState values."""

    if isinstance(value, VersionState):
        return value
    raw = str(value or "").strip().lower()
    if not raw:
        return default
    try:
        return VersionState(raw)
    except ValueError as e:
        raise ValueError(f"invalid lifecycle state: {value}") from e


class SupportRelation(str, Enum):
    """Relationship between one document excerpt and a skill."""

    SUPPORT = "support"
    CONFLICT = "conflict"
    CONSTRAINT = "constraint"
    CASE_VARIANT = "case_variant"


def _coerce_support_relation(value: Any, *, default: SupportRelation) -> SupportRelation:
    """Parses support relation strings into SupportRelation values."""

    if isinstance(value, SupportRelation):
        return value
    raw = str(value or "").strip().lower()
    if not raw:
        return default
    try:
        return SupportRelation(raw)
    except ValueError as e:
        raise ValueError(f"invalid support relation: {value}") from e


_DEFAULT_ASSET_TYPE = "session_skill"
_DEFAULT_GRANULARITY = "session"

_ASSET_TYPE_ALIASES = {
    "macro_protocol": "macro_protocol",
    "protocol": "macro_protocol",
    "macro": "macro_protocol",
    "session_skill": "session_skill",
    "session": "session_skill",
    "skill": "session_skill",
    "micro_skill": "micro_skill",
    "micro": "micro_skill",
    "micro_intervention": "micro_skill",
    "safety_rule": "safety_rule",
    "safety": "safety_rule",
    "policy": "safety_rule",
    "risk_rule": "safety_rule",
    "knowledge_reference": "knowledge_reference",
    "knowledge": "knowledge_reference",
    "reference": "knowledge_reference",
}

_ASSET_TYPE_DEFAULT_GRANULARITY = {
    "macro_protocol": "macro",
    "session_skill": "session",
    "micro_skill": "micro",
    "safety_rule": "session",
    "knowledge_reference": "session",
}

_GRANULARITY_ALIASES = {
    "macro": "macro",
    "protocol": "macro",
    "session": "session",
    "default": "session",
    "micro": "micro",
    "atomic": "micro",
}


def _coerce_asset_type(value: Any) -> str:
    """Normalizes one asset type label into a stable closed-set value."""

    raw = str(value or "").strip().lower()
    if not raw:
        return _DEFAULT_ASSET_TYPE
    return _ASSET_TYPE_ALIASES.get(raw, _DEFAULT_ASSET_TYPE)


def _coerce_granularity(value: Any, *, asset_type: str) -> str:
    """Normalizes one granularity label with asset-type-aware defaults."""

    raw = str(value or "").strip().lower()
    if raw:
        return _GRANULARITY_ALIASES.get(raw, _ASSET_TYPE_DEFAULT_GRANULARITY.get(asset_type, _DEFAULT_GRANULARITY))
    return _ASSET_TYPE_DEFAULT_GRANULARITY.get(asset_type, _DEFAULT_GRANULARITY)


def _has_execution_content(
    *,
    workflow_steps: List[str],
    intervention_moves: List[str],
    constraints: List[str],
    cautions: List[str],
) -> bool:
    """Checks whether one skill carries enough executable or safety guidance."""

    return bool(workflow_steps or intervention_moves or constraints or cautions)


@dataclass
class TextSpan(SerializableModel):
    """Inclusive-exclusive text span describing a segment within a document."""

    start: int = 0
    end: int = 0

    def __post_init__(self) -> None:
        """Normalizes and validates numeric span boundaries."""

        self.start = int(self.start or 0)
        self.end = int(self.end or 0)
        self.validate()

    def validate(self) -> None:
        """Ensures span offsets are non-negative and ordered."""

        if self.start < 0 or self.end < 0:
            raise ValueError("span offsets must be non-negative")
        if self.end < self.start:
            raise ValueError("span.end must be greater than or equal to span.start")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextSpan":
        """Builds a TextSpan from a plain dict."""

        return cls(start=int(data.get("start", 0) or 0), end=int(data.get("end", 0) or 0))


@dataclass
class DocumentSection(SerializableModel):
    """Named document section used to preserve structure after import."""

    heading: str
    text: str
    level: int = 1
    span: TextSpan = field(default_factory=TextSpan)

    def __post_init__(self) -> None:
        """Normalizes section fields and validates them."""

        self.heading = str(self.heading or "").strip()
        self.text = str(self.text or "")
        self.level = int(self.level or 1)
        if not isinstance(self.span, TextSpan):
            self.span = TextSpan.from_dict(_coerce_str_dict(self.span))
        self.validate()

    def validate(self) -> None:
        """Ensures sections keep a heading, body, and valid source span."""

        if not self.heading:
            raise ValueError("section.heading must not be empty")
        if not self.text.strip():
            raise ValueError("section.text must not be empty")
        if self.level <= 0:
            raise ValueError("section.level must be positive")
        self.span.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentSection":
        """Builds a DocumentSection from a plain dict."""

        return cls(
            heading=str(data.get("heading") or "").strip(),
            text=str(data.get("text") or ""),
            level=int(data.get("level", 1) or 1),
            span=TextSpan.from_dict(_coerce_str_dict(data.get("span"))),
        )


@dataclass
class DocumentRecord(SerializableModel):
    """Normalized offline document payload and its import metadata."""

    doc_id: str
    source_type: str
    title: str
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    domain: str = ""
    raw_text: str = ""
    sections: List[DocumentSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    content_hash: str = ""
    imported_at: str = ""

    def __post_init__(self) -> None:
        """Normalizes document fields and fills stable defaults."""

        self.doc_id = str(self.doc_id or "").strip()
        self.source_type = str(self.source_type or "").strip()
        self.title = str(self.title or "").strip()
        self.authors = _coerce_str_list(self.authors)
        self.year = int(self.year) if self.year is not None and str(self.year).strip() else None
        self.domain = str(self.domain or "").strip()
        self.raw_text = str(self.raw_text or "")
        self.sections = [
            sec if isinstance(sec, DocumentSection) else DocumentSection.from_dict(_coerce_str_dict(sec))
            for sec in list(self.sections or [])
        ]
        self.metadata = _coerce_str_dict(self.metadata)
        self.checksum = str(self.checksum or "").strip()
        self.content_hash = str(self.content_hash or "").strip()
        if self.checksum and not self.content_hash:
            self.content_hash = self.checksum
        if self.content_hash and not self.checksum:
            self.checksum = self.content_hash
        self.imported_at = str(self.imported_at or "").strip() or now_iso()
        self.validate()

    def validate(self) -> None:
        """Ensures imported document records contain enough identity and content."""

        if not self.doc_id:
            raise ValueError("doc_id must not be empty")
        if not self.source_type:
            raise ValueError("source_type must not be empty")
        if not self.title:
            raise ValueError("title must not be empty")
        if self.year is not None and (self.year < 0 or self.year > 9999):
            raise ValueError("year must be between 0 and 9999")
        if not self.raw_text.strip() and not self.sections:
            raise ValueError("document must contain raw_text or at least one section")
        if not self.content_hash:
            raise ValueError("content_hash/checksum must not be empty")
        for section in self.sections:
            section.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentRecord":
        """Builds a DocumentRecord from a plain dict."""

        return cls(
            doc_id=str(data.get("doc_id") or "").strip(),
            source_type=str(data.get("source_type") or "").strip(),
            title=str(data.get("title") or "").strip(),
            authors=_coerce_str_list(data.get("authors")),
            year=data.get("year"),
            domain=str(data.get("domain") or "").strip(),
            raw_text=str(data.get("raw_text") or ""),
            sections=[
                DocumentSection.from_dict(_coerce_str_dict(item))
                for item in list(data.get("sections") or [])
            ],
            metadata=_coerce_str_dict(data.get("metadata")),
            checksum=str(data.get("checksum") or "").strip(),
            content_hash=str(data.get("content_hash") or "").strip(),
            imported_at=str(data.get("imported_at") or "").strip(),
        )


@dataclass
class SupportRecord(SerializableModel):
    """Lightweight support/conflict trace grounding one skill in source text."""

    support_id: str
    doc_id: str
    skill_id: str = ""
    source_file: str = ""
    section: str = ""
    span: TextSpan = field(default_factory=TextSpan)
    excerpt: str = ""
    relation_type: SupportRelation = SupportRelation.SUPPORT
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self) -> None:
        """Normalizes support fields and validates core provenance invariants."""

        self.support_id = str(self.support_id or "").strip()
        self.doc_id = str(self.doc_id or "").strip()
        self.skill_id = str(self.skill_id or "").strip()
        self.source_file = str(self.source_file or "").strip()
        self.section = str(self.section or "").strip()
        if not isinstance(self.span, TextSpan):
            self.span = TextSpan.from_dict(_coerce_str_dict(self.span))
        self.excerpt = str(self.excerpt or "").strip()
        self.relation_type = _coerce_support_relation(self.relation_type, default=SupportRelation.SUPPORT)
        self.confidence = float(self.confidence or 0.0)
        self.metadata = _coerce_str_dict(self.metadata)
        self.created_at = str(self.created_at or "").strip() or now_iso()
        self.validate()

    def validate(self) -> None:
        """Ensures support records remain traceable to concrete source text."""

        if not self.support_id:
            raise ValueError("support_id must not be empty")
        if not self.doc_id:
            raise ValueError("doc_id must not be empty")
        if not self.excerpt:
            raise ValueError("excerpt must not be empty")
        if not self.source_file and not self.section:
            raise ValueError("support record must include source_file or section")
        _validate_confidence(self.confidence)
        self.span.validate()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SupportRecord":
        """Builds a SupportRecord from a plain dict."""

        return cls(
            support_id=str(data.get("support_id") or "").strip(),
            doc_id=str(data.get("doc_id") or "").strip(),
            skill_id=str(data.get("skill_id") or "").strip(),
            source_file=str(data.get("source_file") or "").strip(),
            section=str(data.get("section") or "").strip(),
            span=TextSpan.from_dict(_coerce_str_dict(data.get("span"))),
            excerpt=str(data.get("excerpt") or "").strip(),
            relation_type=data.get("relation_type") or SupportRelation.SUPPORT.value,
            confidence=float(data.get("confidence", 0.0) or 0.0),
            metadata=_coerce_str_dict(data.get("metadata")),
            created_at=str(data.get("created_at") or "").strip(),
        )


@dataclass
class SkillDraft(SerializableModel):
    """Executable skill draft extracted directly from one document or batch slice."""

    draft_id: str
    doc_id: str
    name: str
    description: str
    asset_type: str = _DEFAULT_ASSET_TYPE
    granularity: str = _DEFAULT_GRANULARITY
    objective: str = ""
    domain: str = ""
    task_family: str = ""
    method_family: str = ""
    stage: str = ""
    applicable_signals: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    intervention_moves: List[str] = field(default_factory=list)
    workflow_steps: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    cautions: List[str] = field(default_factory=list)
    output_contract: List[str] = field(default_factory=list)
    examples: List[SkillExample] = field(default_factory=list)
    risk_class: str = ""
    confidence: float = 0.0
    support_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalizes draft fields and validates extraction-level invariants."""

        self.draft_id = str(self.draft_id or "").strip()
        self.doc_id = str(self.doc_id or "").strip()
        self.name = str(self.name or "").strip()
        self.description = str(self.description or "").strip()
        self.asset_type = _coerce_asset_type(self.asset_type)
        self.granularity = _coerce_granularity(self.granularity, asset_type=self.asset_type)
        self.objective = str(self.objective or "").strip() or self.description
        self.domain = str(self.domain or "").strip()
        self.task_family = str(self.task_family or "").strip()
        self.method_family = str(self.method_family or "").strip()
        self.stage = str(self.stage or "").strip()
        self.applicable_signals = _coerce_str_list(self.applicable_signals)
        self.contraindications = _coerce_str_list(self.contraindications)
        self.intervention_moves = _coerce_str_list(self.intervention_moves)
        self.workflow_steps = _coerce_str_list(self.workflow_steps)
        self.triggers = _coerce_str_list(self.triggers)
        self.constraints = _coerce_str_list(self.constraints)
        self.cautions = _coerce_str_list(self.cautions)
        self.output_contract = _coerce_str_list(self.output_contract)
        self.examples = _coerce_skill_examples(self.examples)
        self.risk_class = str(self.risk_class or "").strip()
        self.confidence = float(self.confidence or 0.0)
        self.support_ids = _coerce_str_list(self.support_ids)
        self.metadata = _coerce_str_dict(self.metadata)
        self.asset_type, self.granularity = refine_asset_shape(
            asset_type=self.asset_type,
            granularity=self.granularity,
            name=self.name,
            description=self.description,
            objective=self.objective,
            prompt=str((self.metadata or {}).get("prompt") or ""),
            risk_class=self.risk_class,
            task_family=self.task_family,
            stage=self.stage,
            intervention_moves=self.intervention_moves,
            workflow_steps=self.workflow_steps,
        )
        self.validate()

    def validate(self) -> None:
        """Ensures drafts stay executable and source-grounded."""

        if not self.draft_id:
            raise ValueError("draft_id must not be empty")
        if not self.doc_id:
            raise ValueError("doc_id must not be empty")
        if not self.name:
            raise ValueError("skill draft name must not be empty")
        if not self.description:
            raise ValueError("skill draft description must not be empty")
        if not self.objective:
            raise ValueError("skill draft objective must not be empty")
        if not _has_execution_content(
            workflow_steps=self.workflow_steps,
            intervention_moves=self.intervention_moves,
            constraints=self.constraints,
            cautions=self.cautions,
        ):
            raise ValueError(
                "skill draft must include workflow_steps, intervention_moves, constraints, or cautions"
            )
        if not self.support_ids:
            raise ValueError("skill draft must reference at least one support record")
        _validate_confidence(self.confidence)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillDraft":
        """Builds a SkillDraft from a plain dict."""

        return cls(
            draft_id=str(data.get("draft_id") or "").strip(),
            doc_id=str(data.get("doc_id") or "").strip(),
            name=str(data.get("name") or "").strip(),
            description=str(data.get("description") or "").strip(),
            asset_type=str(data.get("asset_type") or "").strip(),
            granularity=str(data.get("granularity") or "").strip(),
            objective=str(data.get("objective") or "").strip(),
            domain=str(data.get("domain") or "").strip(),
            task_family=str(data.get("task_family") or "").strip(),
            method_family=str(data.get("method_family") or "").strip(),
            stage=str(data.get("stage") or "").strip(),
            applicable_signals=_coerce_str_list(data.get("applicable_signals")),
            contraindications=_coerce_str_list(data.get("contraindications")),
            intervention_moves=_coerce_str_list(data.get("intervention_moves")),
            workflow_steps=_coerce_str_list(data.get("workflow_steps")),
            triggers=_coerce_str_list(data.get("triggers")),
            constraints=_coerce_str_list(data.get("constraints")),
            cautions=_coerce_str_list(data.get("cautions")),
            output_contract=_coerce_str_list(data.get("output_contract")),
            examples=_coerce_skill_examples(data.get("examples")),
            risk_class=str(data.get("risk_class") or "").strip(),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            support_ids=_coerce_str_list(data.get("support_ids")),
            metadata=_coerce_str_dict(data.get("metadata")),
        )


@dataclass
class SkillSpec(SerializableModel):
    """Canonical skill representation ready for versioning and store upsert."""

    skill_id: str
    name: str
    description: str
    skill_body: str
    asset_type: str = _DEFAULT_ASSET_TYPE
    granularity: str = _DEFAULT_GRANULARITY
    objective: str = ""
    domain: str = ""
    task_family: str = ""
    method_family: str = ""
    stage: str = ""
    applicable_signals: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    intervention_moves: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    workflow_steps: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    cautions: List[str] = field(default_factory=list)
    output_contract: List[str] = field(default_factory=list)
    examples: List[SkillExample] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    support_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "0.1.0"
    status: VersionState = VersionState.DRAFT

    def __post_init__(self) -> None:
        """Normalizes skill fields and validates state."""

        self.skill_id = str(self.skill_id or "").strip()
        self.name = str(self.name or "").strip()
        self.description = str(self.description or "").strip()
        self.skill_body = str(self.skill_body or "")
        self.asset_type = _coerce_asset_type(self.asset_type)
        self.granularity = _coerce_granularity(self.granularity, asset_type=self.asset_type)
        self.objective = str(self.objective or "").strip() or self.description
        self.domain = str(self.domain or "").strip()
        self.task_family = str(self.task_family or "").strip()
        self.method_family = str(self.method_family or "").strip()
        self.stage = str(self.stage or "").strip()
        self.applicable_signals = _coerce_str_list(self.applicable_signals)
        self.contraindications = _coerce_str_list(self.contraindications)
        self.intervention_moves = _coerce_str_list(self.intervention_moves)
        self.triggers = _coerce_str_list(self.triggers)
        self.workflow_steps = _coerce_str_list(self.workflow_steps)
        self.constraints = _coerce_str_list(self.constraints)
        self.cautions = _coerce_str_list(self.cautions)
        self.output_contract = _coerce_str_list(self.output_contract)
        self.examples = _coerce_skill_examples(self.examples)
        self.tags = _coerce_str_list(self.tags)
        self.support_ids = _coerce_str_list(self.support_ids)
        self.metadata = _coerce_str_dict(self.metadata)
        self.version = str(self.version or "").strip() or "0.1.0"
        self.status = _coerce_version_state(self.status, default=VersionState.DRAFT)
        self.asset_type, self.granularity = refine_asset_shape(
            asset_type=self.asset_type,
            granularity=self.granularity,
            name=self.name,
            description=self.description,
            objective=self.objective,
            prompt=self.skill_body,
            risk_class=str((self.metadata or {}).get("risk_class") or ""),
            task_family=self.task_family,
            stage=self.stage,
            intervention_moves=self.intervention_moves,
            workflow_steps=self.workflow_steps,
        )
        self.validate()

    def validate(self) -> None:
        """Ensures skills retain identity, execution content, and version state."""

        if not self.skill_id:
            raise ValueError("skill_id must not be empty")
        if not self.name:
            raise ValueError("skill name must not be empty")
        if not self.description:
            raise ValueError("skill description must not be empty")
        if not self.skill_body.strip():
            raise ValueError("skill_body must not be empty")
        if not self.objective:
            raise ValueError("skill objective must not be empty")
        if not _has_execution_content(
            workflow_steps=self.workflow_steps,
            intervention_moves=self.intervention_moves,
            constraints=self.constraints,
            cautions=self.cautions,
        ):
            raise ValueError(
                "skill must include workflow_steps, intervention_moves, constraints, or cautions"
            )
        _validate_semver(self.version, field_name="version")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillSpec":
        """Builds a SkillSpec from a plain dict."""

        return cls(
            skill_id=str(data.get("skill_id") or "").strip(),
            name=str(data.get("name") or "").strip(),
            description=str(data.get("description") or "").strip(),
            skill_body=str(data.get("skill_body") or ""),
            asset_type=str(data.get("asset_type") or "").strip(),
            granularity=str(data.get("granularity") or "").strip(),
            objective=str(data.get("objective") or "").strip(),
            domain=str(data.get("domain") or "").strip(),
            task_family=str(data.get("task_family") or "").strip(),
            method_family=str(data.get("method_family") or "").strip(),
            stage=str(data.get("stage") or "").strip(),
            applicable_signals=_coerce_str_list(data.get("applicable_signals")),
            contraindications=_coerce_str_list(data.get("contraindications")),
            intervention_moves=_coerce_str_list(data.get("intervention_moves")),
            triggers=_coerce_str_list(data.get("triggers")),
            workflow_steps=_coerce_str_list(data.get("workflow_steps")),
            constraints=_coerce_str_list(data.get("constraints")),
            cautions=_coerce_str_list(data.get("cautions")),
            output_contract=_coerce_str_list(data.get("output_contract")),
            examples=_coerce_skill_examples(data.get("examples")),
            tags=_coerce_str_list(data.get("tags")),
            support_ids=_coerce_str_list(data.get("support_ids")),
            metadata=_coerce_str_dict(data.get("metadata")),
            version=str(data.get("version") or "0.1.0"),
            status=data.get("status") or VersionState.DRAFT.value,
        )


@dataclass
class SkillLifecycle(SerializableModel):
    """Lifecycle transition for a canonical skill within the offline registry."""

    lifecycle_id: str
    skill_id: str
    from_state: Optional[VersionState] = None
    to_state: VersionState = VersionState.CANDIDATE
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    changed_at: str = ""

    def __post_init__(self) -> None:
        """Normalizes transition fields and validates state changes."""

        self.lifecycle_id = str(self.lifecycle_id or "").strip()
        self.skill_id = str(self.skill_id or "").strip()
        if self.from_state is not None:
            self.from_state = _coerce_version_state(self.from_state, default=VersionState.CANDIDATE)
        self.to_state = _coerce_version_state(self.to_state, default=VersionState.CANDIDATE)
        self.reason = str(self.reason or "").strip()
        self.metadata = _coerce_str_dict(self.metadata)
        self.changed_at = str(self.changed_at or "").strip() or now_iso()
        self.validate()

    def validate(self) -> None:
        """Ensures lifecycle entries identify a target skill and a valid transition."""

        if not self.lifecycle_id:
            raise ValueError("lifecycle_id must not be empty")
        if not self.skill_id:
            raise ValueError("lifecycle must reference a skill_id")
        if self.from_state is not None and self.from_state == self.to_state:
            raise ValueError("lifecycle transition must change state when from_state is set")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillLifecycle":
        """Builds a SkillLifecycle from a plain dict."""

        raw_from = data.get("from_state")
        return cls(
            lifecycle_id=str(data.get("lifecycle_id") or "").strip(),
            skill_id=str(data.get("skill_id") or "").strip(),
            from_state=(
                _coerce_version_state(raw_from, default=VersionState.CANDIDATE)
                if raw_from is not None and str(raw_from).strip()
                else None
            ),
            to_state=data.get("to_state") or VersionState.CANDIDATE.value,
            reason=str(data.get("reason") or "").strip(),
            metadata=_coerce_str_dict(data.get("metadata")),
            changed_at=str(data.get("changed_at") or "").strip(),
        )
