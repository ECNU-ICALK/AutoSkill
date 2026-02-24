"""
LLM connector factory with plugin-style registration.

Compatibility:
- Keeps `build_llm(config)` as the main entry point.
- Preserves existing built-in providers and aliases.
- Allows runtime registration of custom connectors via `register_llm_connector(...)`.
- Allows config-driven external builders via `connector_factory="module:function"`.
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Callable, Dict, List

from .anthropic import AnthropicLLM
from .base import LLM
from .generic import GenericChatLLM
from .glm import GLMChatLLM
from .internlm import InternLMChatLLM
from .mock import MockLLM
from .openai import OpenAIChatLLM

LLMBuilder = Callable[[Dict[str, Any]], LLM]

_LLM_BUILDERS: Dict[str, LLMBuilder] = {}
_LLM_ALIASES: Dict[str, str] = {
    # Generic OpenAI-compatible endpoints.
    "universal": "generic",
    "custom": "generic",
    "openai-compatible": "generic",
    "openai_compatible": "generic",
    # BigModel / GLM aliases.
    "bigmodel": "glm",
    "zhipu": "glm",
    # DashScope / Qwen aliases.
    "qwen": "dashscope",
    # InternLM aliases.
    "intern": "internlm",
    "intern-s1": "internlm",
    "intern-s1-pro": "internlm",
}


def _normalize_provider(name: Any) -> str:
    s = str(name or "mock").strip().lower()
    if not s:
        s = "mock"
    return _LLM_ALIASES.get(s, s)


def _load_builder_from_path(path: str) -> LLMBuilder:
    spec = str(path or "").strip()
    if not spec:
        raise ValueError("Empty connector_factory")
    if ":" in spec:
        module_name, attr = spec.split(":", 1)
    elif "." in spec:
        module_name, _, attr = spec.rpartition(".")
    else:
        raise ValueError(f"Invalid connector_factory path: {spec}")
    module_name = module_name.strip()
    attr = attr.strip()
    if not module_name or not attr:
        raise ValueError(f"Invalid connector_factory path: {spec}")
    module = importlib.import_module(module_name)
    builder = getattr(module, attr, None)
    if not callable(builder):
        raise ValueError(f"connector_factory is not callable: {spec}")
    return builder  # type: ignore[return-value]


def register_llm_connector(
    provider: str,
    builder: LLMBuilder,
    *,
    aliases: List[str] | None = None,
    override: bool = True,
) -> None:
    """
    Registers a connector builder for a provider name.

    Example:
        register_llm_connector("myllm", build_myllm, aliases=["my-llm"])
    """

    key = _normalize_provider(provider)
    if not key:
        raise ValueError("provider is required")
    if (not override) and key in _LLM_BUILDERS:
        return
    _LLM_BUILDERS[key] = builder
    for a in (aliases or []):
        alias = str(a or "").strip().lower()
        if alias:
            _LLM_ALIASES[alias] = key


def list_llm_connectors() -> List[str]:
    _ensure_builtins_registered()
    return sorted(_LLM_BUILDERS.keys())


def _build_mock(config: Dict[str, Any]) -> LLM:
    return MockLLM(response=str(config.get("response") or '{"skills": []}'))


def _build_openai(config: Dict[str, Any]) -> LLM:
    return OpenAIChatLLM(
        model=str(config.get("model", "gpt-4o-mini")),
        api_key=config.get("api_key"),
        base_url=str(config.get("base_url", "https://api.openai.com")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_input_chars=int(config.get("max_input_chars", 100000)),
        max_tokens=int(config.get("max_tokens", 30000)),
    )


def _build_generic(config: Dict[str, Any]) -> LLM:
    base_url = str(
        config.get("url")
        or config.get("base_url")
        or "http://35.220.164.252:3888/v1"
    )
    return GenericChatLLM(
        model=str(config.get("model", "gpt-5.2")),
        api_key=(config.get("api_key") or os.getenv("AUTOSKILL_GENERIC_API_KEY") or ""),
        base_url=base_url,
        timeout_s=int(config.get("timeout_s", 60)),
        max_input_chars=int(config.get("max_input_chars", 100000)),
        max_tokens=int(config.get("max_tokens", 30000)),
    )


def _build_dashscope(config: Dict[str, Any]) -> LLM:
    # DashScope's "compatible-mode" is OpenAI Chat Completions compatible.
    return OpenAIChatLLM(
        model=str(config.get("model", "qwen-plus")),
        api_key=(config.get("api_key") or os.getenv("DASHSCOPE_API_KEY")),
        base_url=str(config.get("base_url", "https://dashscope.aliyuncs.com/compatible-mode")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_input_chars=int(config.get("max_input_chars", 100000)),
        max_tokens=int(config.get("max_tokens", 30000)),
    )


def _build_internlm(config: Dict[str, Any]) -> LLM:
    return InternLMChatLLM(
        model=str(config.get("model", "intern-s1-pro")),
        api_key=(config.get("api_key") or os.getenv("INTERNLM_API_KEY")),
        base_url=str(config.get("base_url", "https://chat.intern-ai.org.cn/api/v1")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_input_chars=int(config.get("max_input_chars", 100000)),
        max_tokens=int(config.get("max_tokens", 30000)),
        extra_body=(config.get("extra_body") or config.get("extra_payload")),
        thinking_mode=config.get("thinking_mode", True),
    )


def _build_glm(config: Dict[str, Any]) -> LLM:
    return GLMChatLLM(
        model=str(config.get("model", "glm-4.7")),
        api_key=config.get("api_key"),
        api_key_id=config.get("api_key_id"),
        api_key_secret=config.get("api_key_secret"),
        base_url=str(config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_tokens=int(config.get("max_tokens", 30000)),
        max_input_chars=int(config.get("max_input_chars", 100000)),
        token_ttl_s=int(config.get("token_ttl_s", 3600)),
        token_time_unit=str(config.get("token_time_unit", "ms")),
        auth_mode=str(config.get("auth_mode", "auto")),
        extra_body=(config.get("extra_body") or config.get("extra_payload")),
    )


def _build_anthropic(config: Dict[str, Any]) -> LLM:
    return AnthropicLLM(
        model=str(config.get("model", "claude-3-5-sonnet-latest")),
        api_key=config.get("api_key"),
        base_url=str(config.get("base_url", "https://api.anthropic.com")),
        timeout_s=int(config.get("timeout_s", 60)),
        max_input_chars=int(config.get("max_input_chars", 100000)),
        max_tokens=int(config.get("max_tokens", 30000)),
    )


def _ensure_builtins_registered() -> None:
    if _LLM_BUILDERS:
        return
    register_llm_connector("mock", _build_mock)
    register_llm_connector("openai", _build_openai)
    register_llm_connector("generic", _build_generic, aliases=["openai-compatible", "openai_compatible", "universal", "custom"])
    register_llm_connector("dashscope", _build_dashscope, aliases=["qwen"])
    register_llm_connector("internlm", _build_internlm, aliases=["intern", "intern-s1", "intern-s1-pro"])
    register_llm_connector("glm", _build_glm, aliases=["bigmodel", "zhipu"])
    register_llm_connector("anthropic", _build_anthropic)


def build_llm(config: Dict[str, Any]) -> LLM:
    """
    Builds an LLM connector from config.

    Extra plugin options:
    - `connector_factory`: "module:function" returning an `LLM` instance.
    - runtime registration via `register_llm_connector(...)`.
    """

    _ensure_builtins_registered()
    cfg = dict(config or {})

    factory_path = str(
        cfg.get("connector_factory")
        or cfg.get("llm_connector_factory")
        or cfg.get("provider_factory")
        or ""
    ).strip()
    if factory_path:
        return _load_builder_from_path(factory_path)(cfg)

    provider = _normalize_provider(cfg.get("provider") or "mock")
    builder = _LLM_BUILDERS.get(provider)
    if builder is None:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Available: {', '.join(list_llm_connectors())}"
        )
    return builder(cfg)

