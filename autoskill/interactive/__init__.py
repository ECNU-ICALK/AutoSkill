"""
Interactive module.

This package contains the interactive "chat + retrieve + optional extract" loop.
It is designed as a reusable module (not only as an example script).
"""

from .app import InteractiveChatApp
from .config import InteractiveConfig
from .io import ConsoleIO, IO
from .rewriting import LLMQueryRewriter
from .selection import LLMSkillSelector

__all__ = [
    "ConsoleIO",
    "IO",
    "InteractiveChatApp",
    "InteractiveConfig",
    "LLMQueryRewriter",
    "LLMSkillSelector",
]
