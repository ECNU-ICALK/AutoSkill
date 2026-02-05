"""
LLM provider layer.

To keep the SDK lightweight, providers are implemented with urllib:
- openai / anthropic: minimal chat completion clients
- dashscope: Aliyun DashScope Qwen (OpenAI-compatible mode)
- glm: BigModel GLM client (supports jwt/api_key/auto auth)
"""

from .base import LLM
from .factory import build_llm

__all__ = ["LLM", "build_llm"]
