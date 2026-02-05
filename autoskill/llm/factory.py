"""
LLM factory: build a concrete provider from a config dict.

To stay compatible with external config files and env-based secrets, this factory uses dict configs and
providers may read environment variables internally.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from .anthropic import AnthropicLLM
from .base import LLM
from .glm import GLMChatLLM
from .mock import MockLLM
from .openai import OpenAIChatLLM


def build_llm(config: Dict[str, Any]) -> LLM:
    # Provider names are intentionally permissive for config migration (glm/bigmodel/zhipu -> same impl).
    provider = (config.get("provider") or "mock").lower()

    if provider == "mock":
        return MockLLM(response=str(config.get("response") or '{"skills": []}'))

    if provider == "openai":
        return OpenAIChatLLM(
            model=str(config.get("model", "gpt-4o-mini")),
            api_key=config.get("api_key"),
            base_url=str(config.get("base_url", "https://api.openai.com")),
            timeout_s=int(config.get("timeout_s", 60)),
            max_input_chars=int(config.get("max_input_chars", 10000)),
            max_tokens=int(config.get("max_tokens", 4096)),
        )

    if provider in {"dashscope", "qwen"}:
        # DashScope's "compatible-mode" is OpenAI Chat Completions compatible.
        return OpenAIChatLLM(
            model=str(config.get("model", "qwen-plus")),
            api_key=(config.get("api_key") or os.getenv("DASHSCOPE_API_KEY")),
            base_url=str(
                config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode")
            ),
            timeout_s=int(config.get("timeout_s", 60)),
            max_input_chars=int(config.get("max_input_chars", 10000)),
            max_tokens=int(config.get("max_tokens", 4096)),
        )

    if provider in {"glm", "bigmodel", "zhipu"}:
        return GLMChatLLM(
            model=str(config.get("model", "glm-4.7")),
            api_key=config.get("api_key"),
            api_key_id=config.get("api_key_id"),
            api_key_secret=config.get("api_key_secret"),
            base_url=str(config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")),
            timeout_s=int(config.get("timeout_s", 60)),
            max_tokens=int(config.get("max_tokens", 4096)),
            max_input_chars=int(config.get("max_input_chars", 10000)),
            token_ttl_s=int(config.get("token_ttl_s", 3600)),
            token_time_unit=str(config.get("token_time_unit", "ms")),
            auth_mode=str(config.get("auth_mode", "auto")),
            extra_body=(config.get("extra_body") or config.get("extra_payload")),
        )

    if provider == "anthropic":
        return AnthropicLLM(
            model=str(config.get("model", "claude-3-5-sonnet-latest")),
            api_key=config.get("api_key"),
            base_url=str(config.get("base_url", "https://api.anthropic.com")),
            timeout_s=int(config.get("timeout_s", 60)),
            max_input_chars=int(config.get("max_input_chars", 10000)),
            max_tokens=int(config.get("max_tokens", 4096)),
        )

    raise ValueError(f"Unknown LLM provider: {provider}")
