#!/usr/bin/env python3
"""
AutoSkill OpenClaw plugin runtime entrypoint.

This service is NOT a chat model proxy. It exposes autoskill retrieval/evolution APIs
for OpenClaw to call with its own conversation data.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure local repository modules are importable without requiring `pip install -e .`.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.interactive import AutoSkillProxyConfig

from examples.interactive_chat import (
    _env,
    _pick_default_provider,
    build_embeddings_config,
    build_llm_config,
)
from service_runtime import OpenClawSkillRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AutoSkill OpenClaw skill service")
    parser.add_argument("--host", default=_env("AUTOSKILL_PROXY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(_env("AUTOSKILL_PROXY_PORT", "9100")))

    parser.add_argument(
        "--llm-provider",
        default=_pick_default_provider(),
        help="mock|generic|glm|internlm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=None)
    parser.add_argument(
        "--embeddings-provider",
        default="",
        help="hashing|none|generic|glm|dashscope|openai (default depends on llm)",
    )
    parser.add_argument("--embeddings-model", default=None)

    parser.add_argument("--store-dir", default=_env("AUTOSKILL_STORE_DIR", "SkillBank"))
    parser.add_argument("--user-id", default=_env("AUTOSKILL_USER_ID", "openclaw_user"))
    parser.add_argument("--skill-scope", default=_env("AUTOSKILL_SKILL_SCOPE", "all"), help="user|common|all")
    parser.add_argument("--rewrite-mode", default=_env("AUTOSKILL_REWRITE_MODE", "always"), help="never|auto|always")
    parser.add_argument("--min-score", type=float, default=float(_env("AUTOSKILL_MIN_SCORE", "0.4")))
    parser.add_argument("--top-k", type=int, default=int(_env("AUTOSKILL_TOP_K", "1")))
    parser.add_argument("--history-turns", type=int, default=int(_env("AUTOSKILL_HISTORY_TURNS", "100")))
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
        default=int(_env("AUTOSKILL_PROXY_EXTRACT_EVENT_MAX_MD_CHARS", "0")),
        help="Max SKILL.md chars included in extraction event details (0 means no truncation).",
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
    parser.add_argument(
        "--served-model",
        action="append",
        default=[],
        help="Model id exposed by /v1/models (repeat this flag for multiple models).",
    )
    parser.add_argument(
        "--served-models-json",
        default=_env("AUTOSKILL_PROXY_MODELS", ""),
        help="Optional JSON list for /v1/models.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
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
    served_models: list[dict[str, Any] | str] = []
    for mid in list(args.served_model or []):
        m = str(mid or "").strip()
        if m:
            served_models.append(m)
    raw_models_json = str(args.served_models_json or "").strip()
    if raw_models_json:
        try:
            parsed_models = json.loads(raw_models_json)
            if isinstance(parsed_models, list):
                served_models.extend(parsed_models)
        except Exception:
            print("[openclaw-plugin] warning: invalid --served-models-json / AUTOSKILL_PROXY_MODELS, ignored.")

    cfg = AutoSkillProxyConfig(
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
        served_models=served_models,
    ).normalize()

    runtime = OpenClawSkillRuntime(
        sdk=sdk,
        llm_config=llm_cfg,
        embeddings_config=emb_cfg,
        config=cfg,
    )
    server = runtime.create_server(host=str(args.host), port=int(args.port))
    host, port = server.server_address[:2]
    print(f"AutoSkill OpenClaw Skill Service: http://{host}:{port}")
    print(
        "Endpoints: /v1/models, /v1/autoskill/openclaw/turn, /v1/autoskill/retrieval/preview, "
        "/v1/autoskill/conversations/import, /v1/autoskill/extractions, /v1/autoskill/capabilities, /health"
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
