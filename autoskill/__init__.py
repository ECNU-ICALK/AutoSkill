"""
AutoSkill SDK top-level package.

Main exports:
- `AutoSkill`: SDK entrypoint (ingest/search/render/export, etc.)
- `AutoSkillConfig`: unified config (LLM / embeddings / store / maintenance strategy)
"""

from .client import AutoSkill
from .config import AutoSkillConfig
from .models import Skill, SkillHit, SkillStatus

__all__ = ["AutoSkill", "AutoSkillConfig", "Skill", "SkillHit", "SkillStatus"]
