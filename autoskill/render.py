"""
Render retrieved Skills into a text block that can be injected into context.

Typical usage:
1) sdk.search(...) to find relevant skills
2) sdk.render_context(...) to build an injectable context snippet
3) concatenate into your system prompt / agent context
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from .models import Skill
from .utils.units import text_units, truncate_keep_head


def select_skills_for_context(
    skills: Iterable[Skill], *, query: Optional[str] = None, max_chars: int = 6_000
) -> List[Skill]:
    """
    Selects the subset of Skills that fit within `max_chars` using the same sizing logic as
    `render_skills_context`.
    """

    header = (
        "## AutoSkill Skills\n"
        "Instructions: Choose the most relevant skill and follow its prompt; ignore if none applies."
    )
    if query:
        header += f"\nQuery: {query}"

    parts: List[str] = [header]
    selected: List[Skill] = []
    used = text_units(header)
    for i, skill in enumerate(skills, start=1):
        remaining = max_chars - used
        if remaining <= 0:
            break
        block = _render_one(skill, index=i, max_chars=remaining)
        if not block.strip():
            continue
        block_units = text_units(block)
        if used + block_units > max_chars:
            continue
        parts.append(block)
        selected.append(skill)
        used += block_units
    return selected


def render_skills_context(
    skills: Iterable[Skill], *, query: Optional[str] = None, max_chars: int = 6_000
) -> str:
    """Run render skills context."""
    parts: List[str] = []
    header = (
        "## AutoSkill Skills\n"
        "Instructions: Choose the most relevant skill and follow its prompt; ignore if none applies."
    )
    if query:
        header += f"\nQuery: {query}"
    parts.append(header)
    used = text_units(header)

    for i, skill in enumerate(skills, start=1):
        remaining = max_chars - used
        if remaining <= 0:
            break
        block = _render_one(skill, index=i, max_chars=remaining)
        if not block.strip():
            continue
        block_units = text_units(block)
        if used + block_units > max_chars:
            continue
        parts.append(block)
        used += block_units

    return "\n\n".join(parts).strip() + "\n"


def _render_one(skill: Skill, *, index: int, max_chars: Optional[int] = None) -> str:
    """Run render one."""
    triggers = "\n".join(f"- {t}" for t in (skill.triggers or [])[:6])
    tags = ", ".join((skill.tags or [])[:10])
    lines = [
        f"### Skill {index}: {skill.name} (v{skill.version})",
        f"- Id: {skill.id}",
        f"- Description: {skill.description}",
    ]
    if tags:
        lines.append(f"- Tags: {tags}")
    if triggers:
        lines.append("- Triggers:")
        lines.append(triggers)
    lines.append("- Prompt:")
    base = "\n".join(lines).strip() + "\n"

    instr = (skill.instructions or "").strip()
    if max_chars is None:
        return (base + instr).strip()

    limit = max(0, int(max_chars))
    if limit == 0:
        return ""
    if text_units(base) >= limit:
        return truncate_keep_head(base, max_units=limit, marker="").strip()

    avail = limit - text_units(base)
    if text_units(instr) <= avail:
        return (base + instr).strip()

    instr2 = truncate_keep_head(instr, max_units=avail, marker="\n...[truncated]...")
    return (base + instr2).strip()
