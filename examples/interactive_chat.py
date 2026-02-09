"""
Interactive chat demo.

This is a thin wrapper around the reusable interactive module:
`autoskill.interactive`.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, Optional

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path
from autoskill.interactive import (
    ConsoleIO,
    InteractiveChatApp,
    InteractiveConfig,
    LLMQueryRewriter,
    LLMSkillSelector,
)
from autoskill.llm.factory import build_llm


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value is not None and value.strip() else default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or not value.strip():
        return bool(default)
    s = value.strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _env_json(name: str) -> Optional[Dict[str, Any]]:
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


def _pick_default_provider() -> str:
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
    v = os.getenv(env_name)
    if not v or not v.strip():
        raise SystemExit(f"Missing env var {env_name}.")
    return v


def _bigmodel_key() -> str:
    v = os.getenv("ZHIPUAI_API_KEY") or os.getenv("BIGMODEL_API_KEY")
    if not v or not v.strip():
        raise SystemExit("Missing API key. Set ZHIPUAI_API_KEY or BIGMODEL_API_KEY to 'id.secret'.")
    return v


def _internlm_key() -> str:
    v = os.getenv("INTERNLM_API_KEY") or os.getenv("INTERN_API_KEY") or os.getenv("INTERNLM_TOKEN")
    if not v or not v.strip():
        raise SystemExit("Missing API key. Set INTERNLM_API_KEY (or INTERN_API_KEY).")
    return v


def build_llm_config(provider: str, *, model: Optional[str]) -> Dict[str, Any]:
    provider = (provider or "mock").lower()
    if provider == "mock":
        return {"provider": "mock"}

    timeout_s = int(_env("AUTOSKILL_TIMEOUT_S", "120"))

    if provider in {"dashscope", "qwen"}:
        return {
            "provider": "dashscope",
            "model": model or _env("DASHSCOPE_MODEL", "qwen-plus"),
            "api_key": _require_key("DASHSCOPE_API_KEY"),
            "base_url": _env(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode",
            ),
            "timeout_s": timeout_s,
        }

    if provider in {"internlm", "intern", "intern-s1", "intern-s1-pro"}:
        return {
            "provider": "internlm",
            "model": model or _env("INTERNLM_MODEL", "intern-s1-pro"),
            "api_key": _internlm_key(),
            "base_url": _env("INTERNLM_BASE_URL", "https://chat.intern-ai.org.cn/api/v1"),
            # Intern-S1 defaults to think mode; disable by setting INTERNLM_THINKING_MODE=0.
            "thinking_mode": _env_bool("INTERNLM_THINKING_MODE", True),
            "max_tokens": int(_env("INTERNLM_MAX_TOKENS", "30000")),
            "extra_body": _env_json("INTERNLM_LLM_EXTRA_BODY"),
            "timeout_s": timeout_s,
        }

    if provider == "openai":
        return {
            "provider": "openai",
            "model": model or _env("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            "api_key": _require_key("OPENAI_API_KEY"),
            "base_url": _env("OPENAI_BASE_URL", "https://api.openai.com"),
            "timeout_s": timeout_s,
        }

    if provider == "anthropic":
        return {
            "provider": "anthropic",
            "model": model or _env("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            "api_key": _require_key("ANTHROPIC_API_KEY"),
            "base_url": _env("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "timeout_s": timeout_s,
        }

    if provider in {"glm", "bigmodel", "zhipu"}:
        return {
            "provider": "glm",
            "model": model or _env("BIGMODEL_GLM_MODEL", "glm-4.7"),
            "api_key": _bigmodel_key(),
            "auth_mode": _env("BIGMODEL_AUTH_MODE", "auto"),
            "token_time_unit": _env("BIGMODEL_TOKEN_TIME_UNIT", "ms"),
            "base_url": _env("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            "max_tokens": int(_env("BIGMODEL_MAX_TOKENS", "30000")),
            "extra_body": _env_json("BIGMODEL_LLM_EXTRA_BODY"),
            "timeout_s": timeout_s,
        }

    raise SystemExit(f"Unknown LLM provider: {provider}")


def build_embeddings_config(provider: str, *, model: Optional[str], llm_provider: str) -> Dict[str, Any]:
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
        elif llm_provider == "anthropic":
            provider = "openai" if os.getenv("OPENAI_API_KEY") else "hashing"
        else:
            provider = "hashing"

    if provider == "hashing":
        return {"provider": "hashing", "dims": 256}

    timeout_s = int(_env("AUTOSKILL_TIMEOUT_S", "120"))

    if provider == "openai":
        return {
            "provider": "openai",
            "model": model or _env("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
            "api_key": _require_key("OPENAI_API_KEY"),
            "base_url": _env("OPENAI_BASE_URL", "https://api.openai.com"),
            "timeout_s": timeout_s,
            "extra_body": _env_json("OPENAI_EMB_EXTRA_BODY"),
        }

    if provider in {"dashscope", "qwen"}:
        return {
            "provider": "dashscope",
            "model": model or _env("DASHSCOPE_EMBED_MODEL", "text-embedding-v4"),
            "api_key": _require_key("DASHSCOPE_API_KEY"),
            "base_url": _env(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode",
            ),
            "timeout_s": timeout_s,
            "max_text_chars": int(_env("DASHSCOPE_EMB_MAX_TEXT_CHARS", "10000")),
            "extra_body": _env_json("DASHSCOPE_EMB_EXTRA_BODY"),
        }

    if provider in {"glm", "bigmodel", "zhipu"}:
        return {
            "provider": "glm",
            "model": model or _env("BIGMODEL_EMBED_MODEL", "embedding-3"),
            "api_key": _bigmodel_key(),
            "auth_mode": _env("BIGMODEL_AUTH_MODE", "auto"),
            "token_time_unit": _env("BIGMODEL_TOKEN_TIME_UNIT", "ms"),
            "base_url": _env("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            "extra_body": _env_json("BIGMODEL_EMB_EXTRA_BODY"),
            "max_text_chars": int(_env("BIGMODEL_EMB_MAX_TEXT_CHARS", "10000")),
            "min_text_chars": int(_env("BIGMODEL_EMB_MIN_TEXT_CHARS", "512")),
            "timeout_s": timeout_s,
        }

    raise SystemExit(f"Unknown embeddings provider: {provider}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoSkill interactive chat")
    parser.add_argument(
        "--llm-provider",
        default=_pick_default_provider(),
        help="mock|glm|internlm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=None)
    parser.add_argument(
        "--embeddings-provider",
        default="",
        help="hashing|glm|dashscope|openai (default depends on llm)",
    )
    parser.add_argument("--embeddings-model", default=None)
    default_store_dir = _env(
        "AUTOSKILL_STORE_DIR",
        _env("AUTOSKILL_STORE_PATH", default_store_path()),
    )
    parser.add_argument("--store-dir", dest="store_dir", default=default_store_dir)
    parser.add_argument(
        "--store-path",
        dest="store_dir",
        default=default_store_dir,
        help="Deprecated alias of --store-dir (directory-based store).",
    )
    parser.add_argument("--user-id", default=_env("AUTOSKILL_USER_ID", "u1"))
    parser.add_argument(
        "--skill-scope",
        default=_env("AUTOSKILL_SKILL_SCOPE", "all"),
        help="Which skills to retrieve/use: user|common|all (common==shared library).",
    )
    parser.add_argument(
        "--rewrite-mode",
        default=_env("AUTOSKILL_REWRITE_MODE", "always"),
        help="Rewrite query before retrieval: auto|always|never.",
    )
    parser.add_argument(
        "--rewrite-history-turns",
        type=int,
        default=int(_env("AUTOSKILL_REWRITE_HISTORY_TURNS", "6")),
        help="How many recent turns to include in query rewriting.",
    )
    parser.add_argument(
        "--rewrite-history-chars",
        type=int,
        default=int(_env("AUTOSKILL_REWRITE_HISTORY_CHARS", "4090")),
        help="Max history units for query rewriting (CJK chars + English words).",
    )
    parser.add_argument(
        "--rewrite-max-query-chars",
        type=int,
        default=int(_env("AUTOSKILL_REWRITE_MAX_QUERY_CHARS", "256")),
        help="Max query units for rewritten query (CJK chars + English words).",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=float(_env("AUTOSKILL_MIN_SCORE", "0.4")),
        help="Minimum similarity score for retrieved skills (post-search filter).",
    )
    parser.add_argument(
        "--library-dir",
        action="append",
        default=[],
        help="Additional read-only library root (can be passed multiple times).",
    )
    parser.add_argument("--top-k", type=int, default=int(_env("AUTOSKILL_TOP_K", "1")))
    parser.add_argument("--history-turns", type=int, default=int(_env("AUTOSKILL_HISTORY_TURNS", "20")))
    parser.add_argument("--ingest-window", type=int, default=int(_env("AUTOSKILL_INGEST_WINDOW", "6")))
    parser.add_argument(
        "--extract-turn-limit",
        type=int,
        default=int(_env("AUTOSKILL_EXTRACT_TURN_LIMIT", "1")),
        help="In auto mode, attempt extraction once every N turns (N=extract_turn_limit).",
    )
    parser.add_argument("--extract-mode", default=_env("AUTOSKILL_EXTRACT_MODE", "auto"), help="auto|always|never")
    parser.add_argument(
        "--gating-mode",
        default=_env("AUTOSKILL_GATING_MODE", "llm"),
        help="Deprecated (extraction gating is integrated into the extractor).",
    )
    parser.add_argument(
        "--assistant-temperature",
        type=float,
        default=float(_env("AUTOSKILL_ASSISTANT_TEMPERATURE", "0.2")),
    )
    args = parser.parse_args()

    interactive_cfg = InteractiveConfig(
        store_dir=str(args.store_dir),
        user_id=str(args.user_id),
        skill_scope=str(args.skill_scope),
        rewrite_mode=str(args.rewrite_mode),
        rewrite_history_turns=int(args.rewrite_history_turns),
        rewrite_history_chars=int(args.rewrite_history_chars),
        rewrite_max_query_chars=int(args.rewrite_max_query_chars),
        min_score=float(args.min_score),
        top_k=int(args.top_k),
        history_turns=int(args.history_turns),
        ingest_window=int(args.ingest_window),
        extract_turn_limit=int(args.extract_turn_limit),
        extract_mode=str(args.extract_mode),
        assistant_temperature=float(args.assistant_temperature),
    ).normalize()

    llm_provider = str(args.llm_provider or "mock").lower()
    llm_cfg = build_llm_config(llm_provider, model=args.llm_model)
    emb_cfg = build_embeddings_config(
        str(args.embeddings_provider),
        model=args.embeddings_model,
        llm_provider=llm_provider,
    )

    env_libs = _env("AUTOSKILL_LIBRARY_DIRS", "").strip()
    library_dirs = list(args.library_dir or [])
    if env_libs:
        library_dirs.extend([p.strip() for p in env_libs.split(",") if p.strip()])

    store_cfg: Dict[str, Any] = {"provider": "local", "path": interactive_cfg.store_dir}
    if library_dirs:
        store_cfg["libraries"] = library_dirs

    sdk = AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings=emb_cfg,
            store=store_cfg,
            maintenance_strategy=("llm" if llm_provider != "mock" else "heuristic"),
        )
    )

    chat_llm = None if llm_provider == "mock" else build_llm(llm_cfg)

    query_rewriter = None
    if llm_provider != "mock":
        rewrite_cfg = dict(llm_cfg)
        if str(rewrite_cfg.get("provider") or "").lower() in {"glm", "bigmodel", "zhipu"}:
            try:
                rewrite_cfg["max_tokens"] = min(int(rewrite_cfg.get("max_tokens", 30000)), 30000)
            except Exception:
                rewrite_cfg["max_tokens"] = 30000
        query_rewriter = LLMQueryRewriter(
            build_llm(rewrite_cfg),
            max_history_turns=int(interactive_cfg.rewrite_history_turns),
            max_history_chars=int(interactive_cfg.rewrite_history_chars),
            max_query_chars=int(interactive_cfg.rewrite_max_query_chars),
        )

    skill_selector = None
    # if llm_provider != "mock":
    #     select_cfg = dict(llm_cfg)
    #     if str(select_cfg.get("provider") or "").lower() in {"glm", "bigmodel", "zhipu"}:
    #         try:
    #             select_cfg["max_tokens"] = min(int(select_cfg.get("max_tokens", 4096)), 4096)
    #         except Exception:
    #             select_cfg["max_tokens"] = 4096
    #     skill_selector = LLMSkillSelector(build_llm(select_cfg))

    # print("skill_selector", skill_selector)
    # print("query_rewriter", query_rewriter)
    app = InteractiveChatApp(
        sdk=sdk,
        config=interactive_cfg,
        io=ConsoleIO(),
        chat_llm=chat_llm,
        query_rewriter=query_rewriter,
        skill_selector=skill_selector,
    )
    app.run()


if __name__ == "__main__":
    main()
