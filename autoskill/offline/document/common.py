"""
Common helpers for the offline document pipeline.

These utilities intentionally stay small and dependency-free so stage modules
can share the same naming and behavior without reimplementing the same text and
logging helpers.
"""

from __future__ import annotations

import re
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

StageLogger = Optional[Callable[[str], None]]


def emit_stage_log(logger: StageLogger, message: str) -> None:
    """Emits one stage log line when a logger callback is configured."""

    if logger is not None:
        logger(str(message))


def normalize_text(text: str, *, lower: bool = False) -> str:
    """Collapses whitespace while preserving token order."""

    normalized = re.sub(r"\s+", " ", str(text or "").strip())
    return normalized.lower() if lower else normalized


def dedupe_strings(
    items: Iterable[str],
    *,
    lower: bool = True,
) -> List[str]:
    """Deduplicates strings while preserving their first-seen order."""

    out: List[str] = []
    seen = set()
    for item in items:
        value = str(item or "").strip()
        if not value:
            continue
        key = normalize_text(value, lower=lower)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


_SAFETY_HINTS = (
    "自杀",
    "自伤",
    "他伤",
    "伤人",
    "危机",
    "安全计划",
    "安全承诺",
    "不自杀承诺",
    "紧急热线",
    "suicide",
    "self-harm",
    "crisis",
    "safety plan",
    "safety commitment",
    "hotline",
    "violence",
    "homicide",
)

_MACRO_SCOPE_HINTS = (
    "三阶段",
    "多阶段",
    "分阶段",
    "全过程",
    "全程",
    "完整流程",
    "阶段化",
    "phase 1",
    "phase 2",
    "phase 3",
    "multi-stage",
    "end-to-end",
    "from intake to closing",
)

_SESSION_SCOPE_HINTS = (
    "会谈结构",
    "session structure",
    "session flow",
    "结构化会谈",
    "固定环节",
    "agenda",
    "homework review",
    "summary and feedback",
    "组合包",
    "技术集",
    "toolkit",
    "bundle",
    "package",
)

_MICRO_SCOPE_HINTS = (
    "微干预",
    "引导",
    "识别",
    "命名",
    "提问",
    "反映",
    "镜映",
    "重评",
    "prompting",
    "naming",
    "reflection",
    "reframing",
)


def _contains_any(text: str, markers: Sequence[str]) -> bool:
    normalized = normalize_text(text, lower=True)
    return any(str(marker or "").strip().lower() in normalized for marker in markers if str(marker or "").strip())


def refine_asset_shape(
    *,
    asset_type: str,
    granularity: str,
    name: str,
    description: str,
    objective: str,
    prompt: str,
    risk_class: str,
    task_family: str,
    stage: str,
    intervention_moves: Sequence[str],
    workflow_steps: Sequence[str],
) -> Tuple[str, str]:
    """Corrects asset_type/granularity drift using lightweight scope and safety rules."""

    text = "\n".join(
        [
            str(name or ""),
            str(description or ""),
            str(objective or ""),
            str(task_family or ""),
            str(stage or ""),
        ]
    )
    move_count = len([x for x in intervention_moves if str(x or "").strip()])
    step_count = len([x for x in workflow_steps if str(x or "").strip()])
    task_family_s = str(task_family or "").strip().lower()
    stage_s = str(stage or "").strip().lower()
    risk_class_s = str(risk_class or "").strip().lower()
    asset_type_s = str(asset_type or "").strip() or "session_skill"
    granularity_s = str(granularity or "").strip() or "session"

    has_safety = (
        risk_class_s == "high"
        or task_family_s in {"risk_screening", "de_escalation", "crisis", "crisis_intervention"}
        or stage_s == "crisis"
        or _contains_any(text, _SAFETY_HINTS)
    )
    if has_safety:
        if step_count <= 2 and move_count <= 2 and _contains_any(text, _MICRO_SCOPE_HINTS):
            return "safety_rule", "micro"
        return "safety_rule", "session"

    if asset_type_s == "knowledge_reference":
        return "knowledge_reference", "session"

    if _contains_any(text, _MACRO_SCOPE_HINTS):
        return "macro_protocol", "macro"

    if asset_type_s == "macro_protocol":
        return "macro_protocol", "macro"

    if asset_type_s == "micro_skill":
        if _contains_any(text, _SESSION_SCOPE_HINTS):
            return "session_skill", "session"
        if step_count >= 6 and move_count >= 4:
            return "session_skill", "session"
        return "micro_skill", "micro"

    if asset_type_s == "session_skill":
        if _contains_any(text, _MICRO_SCOPE_HINTS) and not _contains_any(text, _SESSION_SCOPE_HINTS):
            if step_count <= 5 and move_count <= 3:
                return "micro_skill", "micro"
        return "session_skill", "session"

    return asset_type_s, granularity_s
