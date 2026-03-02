"""
Shared provider config builders for offline extractors.

These mirror example runtime behavior:
- provider/model defaults
- provider-specific API key envs via `export`
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def env(name: str, default: str = "") -> str:
    """Run env."""
    value = os.getenv(name)
    return value if value is not None and value.strip() else default


def env_bool(name: str, default: bool) -> bool:
    """Run env bool."""
    value = os.getenv(name)
    if value is None or not value.strip():
        return bool(default)
    s = value.strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def env_json(name: str) -> Optional[Dict[str, Any]]:
    """Run env json."""
    raw = os.getenv(name)
    if not raw or not raw.strip():
        return None
    try:
        obj = json.loads(raw)
    except Exception as e:
        raise SystemExit(f"Invalid JSON in env {name}: {e}")
    if obj is None:
        return None
    if not isinstance(obj, dict):
        raise SystemExit(f"Invalid JSON in env {name}: expected object, got {type(obj).__name__}")
    return obj


def pick_default_provider() -> str:
    """Run pick default provider."""
    if os.getenv("AUTOSKILL_GENERIC_LLM_URL"):
        return "generic"
    if os.getenv("DASHSCOPE_API_KEY"):
        return "dashscope"
    if os.getenv("ZHIPUAI_API_KEY") or os.getenv("BIGMODEL_API_KEY"):
        return "glm"
    if os.getenv("INTERNLM_API_KEY") or os.getenv("INTERN_API_KEY"):
        return "internlm"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "mock"


def _require_key(env_name: str) -> str:
    """Run require key."""
    v = os.getenv(env_name)
    if not v or not v.strip():
        raise SystemExit(f"Missing env var {env_name}.")
    return v


def _bigmodel_key() -> str:
    """Run bigmodel key."""
    v = os.getenv("ZHIPUAI_API_KEY") or os.getenv("BIGMODEL_API_KEY")
    if not v or not v.strip():
        raise SystemExit("Missing API key. Set ZHIPUAI_API_KEY or BIGMODEL_API_KEY to 'id.secret'.")
    return v


def _internlm_key() -> str:
    """Run internlm key."""
    v = os.getenv("INTERNLM_API_KEY") or os.getenv("INTERN_API_KEY") or os.getenv("INTERNLM_TOKEN")
    if not v or not v.strip():
        raise SystemExit("Missing API key. Set INTERNLM_API_KEY (or INTERN_API_KEY).")
    return v


def build_llm_config(provider: str, *, model: Optional[str]) -> Dict[str, Any]:
    """Run build llm config."""
    provider = (provider or "mock").lower()
    if provider == "mock":
        return {"provider": "mock"}

    timeout_s = int(env("AUTOSKILL_TIMEOUT_S", "120"))

    if provider in {"dashscope", "qwen"}:
        return {
            "provider": "dashscope",
            "model": model or env("DASHSCOPE_MODEL", "qwen-plus"),
            "api_key": _require_key("DASHSCOPE_API_KEY"),
            "base_url": env("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode"),
            "timeout_s": timeout_s,
        }

    if provider in {"internlm", "intern", "intern-s1", "intern-s1-pro"}:
        return {
            "provider": "internlm",
            "model": model or env("INTERNLM_MODEL", "intern-s1-pro"),
            "api_key": _internlm_key(),
            "base_url": env("INTERNLM_BASE_URL", "https://chat.intern-ai.org.cn/api/v1"),
            "thinking_mode": env_bool("INTERNLM_THINKING_MODE", True),
            "max_tokens": int(env("INTERNLM_MAX_TOKENS", "30000")),
            "extra_body": env_json("INTERNLM_LLM_EXTRA_BODY"),
            "timeout_s": timeout_s,
        }

    if provider == "openai":
        return {
            "provider": "openai",
            "model": model or env("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            "api_key": _require_key("OPENAI_API_KEY"),
            "base_url": env("OPENAI_BASE_URL", "https://api.openai.com"),
            "timeout_s": timeout_s,
        }

    if provider in {"generic", "universal", "custom"}:
        url = env("AUTOSKILL_GENERIC_LLM_URL", "http://35.220.164.252:3888/v1")
        return {
            "provider": "generic",
            "model": model or env("AUTOSKILL_GENERIC_LLM_MODEL", "gpt-5.2"),
            "api_key": env("AUTOSKILL_GENERIC_API_KEY", ""),
            "url": url,
            "base_url": url,
            "timeout_s": timeout_s,
        }

    if provider == "anthropic":
        return {
            "provider": "anthropic",
            "model": model or env("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            "api_key": _require_key("ANTHROPIC_API_KEY"),
            "base_url": env("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "timeout_s": timeout_s,
        }

    if provider in {"glm", "bigmodel", "zhipu"}:
        return {
            "provider": "glm",
            "model": model or env("BIGMODEL_GLM_MODEL", "glm-4.7"),
            "api_key": _bigmodel_key(),
            "auth_mode": env("BIGMODEL_AUTH_MODE", "auto"),
            "token_time_unit": env("BIGMODEL_TOKEN_TIME_UNIT", "ms"),
            "base_url": env("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            "max_tokens": int(env("BIGMODEL_MAX_TOKENS", "30000")),
            "extra_body": env_json("BIGMODEL_LLM_EXTRA_BODY"),
            "timeout_s": timeout_s,
        }

    raise SystemExit(f"Unknown LLM provider: {provider}")


def build_embeddings_config(provider: str, *, model: Optional[str], llm_provider: str) -> Dict[str, Any]:
    """Run build embeddings config."""
    provider = (provider or "").strip().lower()
    if not provider:
        if llm_provider in {"glm", "bigmodel", "zhipu"}:
            provider = "glm"
        elif llm_provider in {"internlm", "intern", "intern-s1", "intern-s1-pro"}:
            provider = "hashing"
        elif llm_provider in {"dashscope", "qwen"}:
            provider = "dashscope"
        elif llm_provider == "openai":
            provider = "openai"
        elif llm_provider in {"generic", "universal", "custom"}:
            provider = "generic"
        elif llm_provider == "anthropic":
            provider = "openai" if os.getenv("OPENAI_API_KEY") else "hashing"
        else:
            provider = "hashing"

    if provider == "hashing":
        return {"provider": "hashing", "dims": 256}
    if provider in {"none", "off", "disabled", "null", "no_embedding", "no-embedding"}:
        return {"provider": "none"}

    timeout_s = int(env("AUTOSKILL_TIMEOUT_S", "120"))

    if provider == "openai":
        return {
            "provider": "openai",
            "model": model or env("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
            "api_key": _require_key("OPENAI_API_KEY"),
            "base_url": env("OPENAI_BASE_URL", "https://api.openai.com"),
            "timeout_s": timeout_s,
            "extra_body": env_json("OPENAI_EMB_EXTRA_BODY"),
        }

    if provider in {"generic", "universal", "custom"}:
        url = env(
            "AUTOSKILL_GENERIC_EMBED_URL",
            "http://s-20260204155338-p8gv8.ailab-evalservice.pjh-service.org.cn/v1",
        )
        return {
            "provider": "generic",
            "model": model or env("AUTOSKILL_GENERIC_EMBED_MODEL", "embd_qwen3vl8b"),
            "api_key": env("AUTOSKILL_GENERIC_API_KEY", ""),
            "url": url,
            "base_url": url,
            "timeout_s": timeout_s,
            "extra_body": env_json("AUTOSKILL_GENERIC_EMB_EXTRA_BODY"),
        }

    if provider in {"dashscope", "qwen"}:
        return {
            "provider": "dashscope",
            "model": model or env("DASHSCOPE_EMBED_MODEL", "text-embedding-v4"),
            "api_key": _require_key("DASHSCOPE_API_KEY"),
            "base_url": env("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode"),
            "timeout_s": timeout_s,
            "max_text_chars": int(env("DASHSCOPE_EMB_MAX_TEXT_CHARS", "10000")),
            "extra_body": env_json("DASHSCOPE_EMB_EXTRA_BODY"),
        }

    if provider in {"glm", "bigmodel", "zhipu"}:
        return {
            "provider": "glm",
            "model": model or env("BIGMODEL_EMBED_MODEL", "embedding-3"),
            "api_key": _bigmodel_key(),
            "auth_mode": env("BIGMODEL_AUTH_MODE", "auto"),
            "token_time_unit": env("BIGMODEL_TOKEN_TIME_UNIT", "ms"),
            "base_url": env("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            "extra_body": env_json("BIGMODEL_EMB_EXTRA_BODY"),
            "max_text_chars": int(env("BIGMODEL_EMB_MAX_TEXT_CHARS", "10000")),
            "min_text_chars": int(env("BIGMODEL_EMB_MIN_TEXT_CHARS", "512")),
            "timeout_s": timeout_s,
        }

    raise SystemExit(f"Unknown embeddings provider: {provider}")
