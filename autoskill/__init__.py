"""
AutoSkill SDK top-level package.

Main exports:
- `AutoSkill`: SDK entrypoint (ingest/search/render/export, etc.)
- `AutoSkillConfig`: unified config (LLM / embeddings / store / maintenance strategy)
"""

import sys

# Avoid writing .pyc files during local development runs.
sys.dont_write_bytecode = True

from .client import AutoSkill
from .config import AutoSkillConfig
from .interactive.unified import AutoSkillRuntime
from .models import Skill, SkillHit, SkillStatus

__all__ = ["AutoSkill", "AutoSkillConfig", "AutoSkillRuntime", "Skill", "SkillHit", "SkillStatus"]
