"""
Skill management.

This package contains the core "skill layer" implementation:
- extraction: convert conversations/events into Skill candidates
- maintenance: dedupe/merge/version skills and persist to a store
- retrieval: vector-search relevant skills (store implementations)
- artifacts: import/export skill directory artifacts (SKILL.md + optional resources)
"""

from .extraction import (
    HeuristicSkillExtractor,
    LLMSkillExtractor,
    SkillCandidate,
    SkillExtractor,
    build_default_extractor,
)
from .maintenance import SkillMaintainer
from .artifacts import export_skill_dir, export_skill_md, write_skill_dir, write_skill_dirs
from .importer import import_agent_skill_dirs
from .stores import SkillStore, build_store
from .stores.inmemory import InMemorySkillStore
from .stores.local import LocalSkillStore
from .vectors import FlatFileVectorIndex, VectorIndex

__all__ = [
    "SkillCandidate",
    "SkillExtractor",
    "build_default_extractor",
    "HeuristicSkillExtractor",
    "LLMSkillExtractor",
    "SkillMaintainer",
    "export_skill_dir",
    "export_skill_md",
    "write_skill_dir",
    "write_skill_dirs",
    "import_agent_skill_dirs",
    "SkillStore",
    "build_store",
    "InMemorySkillStore",
    "LocalSkillStore",
    "VectorIndex",
    "FlatFileVectorIndex",
]
