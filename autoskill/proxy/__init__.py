"""
OpenAI-compatible reverse proxy for AutoSkill.

This package exposes a small HTTP server that wraps standard LLM API calls and
injects AutoSkill retrieval/evolution logic transparently.
"""

from .server import AutoSkillProxyConfig, AutoSkillProxyRuntime

__all__ = ["AutoSkillProxyConfig", "AutoSkillProxyRuntime"]

