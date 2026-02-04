"""
Core data models for AutoSkill.

Skill: a reusable, executable capability unit (can be materialized as an Agent Skill directory artifact).
SkillHit: a vector-search hit (skill + score).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SkillStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class SkillExample:
    input: str
    output: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Skill:
    """
    An Agent Skill representation (minimal subset).
    """

    id: str
    user_id: str

    name: str
    description: str
    instructions: str

    triggers: List[str] = field(default_factory=list)
    examples: List[SkillExample] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    version: str = "0.1.0"
    status: SkillStatus = SkillStatus.ACTIVE

    files: Dict[str, str] = field(default_factory=dict)
    source: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass(frozen=True)
class SkillHit:
    skill: Skill
    score: float
