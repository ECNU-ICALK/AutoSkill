"""
OpenAI-compatible reverse proxy entrypoint.

Expose AutoSkill through a standard API surface:
- POST /v1/chat/completions
- POST /v1/embeddings
- GET  /v1/models

Typical usage:
  python3 -m examples.openai_proxy --llm-provider dashscope --embeddings-provider dashscope
"""

from __future__ import annotations

import argparse
from typing import Any, Dict

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path
from autoskill.proxy import AutoSkillProxyConfig, AutoSkillProxyRuntime

from .interactive_chat import (
    _env,
    _pick_default_provider,
    build_embeddings_config,
    build_llm_config,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoSkill OpenAI-compatible proxy")
    parser.add_argument("--host", default=_env("AUTOSKILL_PROXY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(_env("AUTOSKILL_PROXY_PORT", "9000")))

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
    parser.add_argument("--user-id", default=_env("AUTOSKILL_USER_ID", "u1"))
    parser.add_argument("--skill-scope", default=_env("AUTOSKILL_SKILL_SCOPE", "all"), help="user|common|all")
    parser.add_argument("--rewrite-mode", default=_env("AUTOSKILL_REWRITE_MODE", "always"), help="never|auto|always")
    parser.add_argument("--min-score", type=float, default=float(_env("AUTOSKILL_MIN_SCORE", "0.4")))
    parser.add_argument("--top-k", type=int, default=int(_env("AUTOSKILL_TOP_K", "1")))
    parser.add_argument("--history-turns", type=int, default=int(_env("AUTOSKILL_HISTORY_TURNS", "20")))
    parser.add_argument("--ingest-window", type=int, default=int(_env("AUTOSKILL_INGEST_WINDOW", "6")))
    parser.add_argument("--extract-enabled", default=_env("AUTOSKILL_EXTRACT_ENABLED", "1"), help="1|0")
    parser.add_argument(
        "--max-bg-extract-jobs",
        type=int,
        default=int(_env("AUTOSKILL_MAX_BG_EXTRACT_JOBS", "2")),
    )
    parser.add_argument(
        "--extract-event-details",
        default=_env("AUTOSKILL_PROXY_EXTRACT_EVENT_DETAILS", "1"),
        help="Include detailed extracted skills in extraction events: 1|0",
    )
    parser.add_argument(
        "--extract-event-max-md-chars",
        type=int,
        default=int(_env("AUTOSKILL_PROXY_EXTRACT_EVENT_MAX_MD_CHARS", "3000")),
        help="Max SKILL.md chars included in extraction event details.",
    )
    parser.add_argument(
        "--proxy-api-key",
        default=_env("AUTOSKILL_PROXY_API_KEY", ""),
        help="Optional API key checked against Authorization: Bearer <key>",
    )
    parser.add_argument(
        "--library-dir",
        action="append",
        default=[],
        help="Additional read-only library root (can be passed multiple times).",
    )
    args = parser.parse_args()

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

    store_cfg: Dict[str, Any] = {"provider": "local", "path": str(args.store_dir)}
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

    extract_enabled = str(args.extract_enabled or "1").strip().lower() not in {"0", "false", "no"}
    extract_event_details = str(args.extract_event_details or "1").strip().lower() not in {
        "0",
        "false",
        "no",
    }

    proxy_cfg = AutoSkillProxyConfig(
        user_id=str(args.user_id),
        skill_scope=str(args.skill_scope),
        rewrite_mode=str(args.rewrite_mode),
        min_score=float(args.min_score),
        top_k=int(args.top_k),
        history_turns=int(args.history_turns),
        extract_enabled=bool(extract_enabled),
        ingest_window=int(args.ingest_window),
        max_bg_extract_jobs=int(args.max_bg_extract_jobs),
        extract_event_include_skill_details=bool(extract_event_details),
        extract_event_max_md_chars=int(args.extract_event_max_md_chars),
        proxy_api_key=(str(args.proxy_api_key).strip() or None),
    ).normalize()

    runtime = AutoSkillProxyRuntime(
        sdk=sdk,
        llm_config=llm_cfg,
        embeddings_config=emb_cfg,
        config=proxy_cfg,
    )
    server = runtime.create_server(host=str(args.host), port=int(args.port))
    host, port = server.server_address[:2]
    print(f"AutoSkill OpenAI Proxy: http://{host}:{port}")
    print("Endpoints: /v1/chat/completions, /v1/embeddings, /v1/models, /v1/autoskill/capabilities, /health")
    server.serve_forever()


if __name__ == "__main__":
    main()
