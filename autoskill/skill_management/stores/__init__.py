"""
SkillStore abstractions and default implementations.

Currently provided:
- inmemory: in-memory vector search (good for demos / single-process)
- local: filesystem-backed store with `Users/<user_id>/...` and optional shared `Common/...` (one skill directory per skill; stores SKILL.md + resources; caches vectors in a persistent on-disk index)
"""

from .base import SkillStore
from .factory import build_store

__all__ = ["SkillStore", "build_store"]
