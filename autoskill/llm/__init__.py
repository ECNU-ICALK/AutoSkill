"""
LLM provider layer.

To keep the SDK lightweight, providers are implemented with urllib:
- openai / anthropic: minimal chat completion clients
- generic: OpenAI-compatible custom endpoint (optional API key)
- dashscope: Aliyun DashScope Qwen (OpenAI-compatible mode)
- internlm: InternLM API (OpenAI-compatible mode)
- glm: BigModel GLM client (supports jwt/api_key/auto auth)
"""

from .base import LLM, LLMConnector
from .factory import (
    build_llm,
    list_llm_connectors,
    register_llm_connector,
)

__all__ = [
    "LLM",
    "LLMConnector",
    "build_llm",
    "register_llm_connector",
    "list_llm_connectors",
]
