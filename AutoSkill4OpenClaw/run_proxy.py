#!/usr/bin/env python3
"""
AutoSkill OpenClaw plugin runtime entrypoint.

This service exposes AutoSkill retrieval/evolution APIs and can optionally act as an
OpenAI-compatible main-turn chat proxy for OpenClaw.
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

from agentic_prompt_profile import (
    OpenClawTrajectorySkillExtractor,
    install_openclaw_agentic_prompt_profile,
)
from examples.interactive_chat import (
    _env,
    _pick_default_provider,
    build_embeddings_config,
    build_llm_config,
)
from service_runtime import OpenClawSkillRuntime
from openclaw_conversation_archive import OpenClawConversationArchiveConfig
from openclaw_main_turn_proxy import OpenClawMainTurnProxyConfig
from openclaw_skill_mirror import OpenClawSkillInstallConfig
from openclaw_usage_tracking import OpenClawUsageTrackingConfig


def _cli_flag_present(flag: str) -> bool:
    needle = str(flag or "").strip()
    if not needle:
        return False
    for raw in sys.argv[1:]:
        arg = str(raw or "").strip()
        if arg == needle or arg.startswith(needle + "="):
            return True
    return False


def _is_truthy(raw: Any, *, default: bool) -> bool:
    value = str(raw or "").strip().lower()
    if not value:
        return bool(default)
    return value not in {"0", "false", "no", "off"}


def _resolve_agent_end_extract_enabled(
    *,
    main_turn_enabled: bool,
    target_configured: bool,
    raw_value: Any,
    explicit: bool,
) -> bool:
    if explicit:
        return _is_truthy(raw_value, default=True)
    if main_turn_enabled and target_configured:
        return False
    return True


def build_parser() -> argparse.ArgumentParser:
    """Run build parser."""
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
    parser.add_argument("--user-id", default=_env("AUTOSKILL_USER_ID", ""))
    parser.add_argument("--skill-scope", default=_env("AUTOSKILL_SKILL_SCOPE", "all"), help="user|common|all")
    parser.add_argument("--rewrite-mode", default=_env("AUTOSKILL_REWRITE_MODE", "always"), help="never|auto|always")
    parser.add_argument("--min-score", type=float, default=float(_env("AUTOSKILL_MIN_SCORE", "0.4")))
    parser.add_argument("--top-k", type=int, default=int(_env("AUTOSKILL_TOP_K", "1")))
    parser.add_argument("--history-turns", type=int, default=int(_env("AUTOSKILL_HISTORY_TURNS", "100")))
    parser.add_argument(
        "--ingest-window",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_INGEST_WINDOW", _env("AUTOSKILL_INGEST_WINDOW", "6"))),
    )
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
    parser.add_argument(
        "--openclaw-main-turn-extract",
        default=_env("AUTOSKILL_OPENCLAW_MAIN_TURN_EXTRACT", "1"),
        help="Enable main-turn sampling on proxied /v1/chat/completions: 1|0",
    )
    parser.add_argument(
        "--openclaw-agent-end-extract",
        default=_env("AUTOSKILL_OPENCLAW_AGENT_END_EXTRACT", ""),
        help="Keep legacy agent_end extraction hook enabled: 1|0",
    )
    parser.add_argument(
        "--openclaw-proxy-target-base-url",
        default=_env("AUTOSKILL_OPENCLAW_PROXY_TARGET_BASE_URL", ""),
        help="Real OpenAI-compatible backend base_url; can end with or without /v1.",
    )
    parser.add_argument(
        "--openclaw-proxy-target-api-key",
        default=_env("AUTOSKILL_OPENCLAW_PROXY_TARGET_API_KEY", ""),
        help="Optional API key injected into proxied chat requests.",
    )
    parser.add_argument(
        "--openclaw-proxy-connect-timeout-s",
        type=float,
        default=float(_env("AUTOSKILL_OPENCLAW_PROXY_CONNECT_TIMEOUT_S", "20")),
    )
    parser.add_argument(
        "--openclaw-proxy-read-timeout-s",
        type=float,
        default=float(_env("AUTOSKILL_OPENCLAW_PROXY_READ_TIMEOUT_S", "600")),
    )
    parser.add_argument(
        "--openclaw-skill-install-mode",
        default=_env("AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE", "openclaw_mirror"),
        help="store_only|openclaw_mirror",
    )
    parser.add_argument(
        "--openclaw-skills-dir",
        default=_env("AUTOSKILL_OPENCLAW_SKILLS_DIR", ""),
        help="Target OpenClaw skills directory. Empty uses the detected default.",
    )
    parser.add_argument(
        "--openclaw-install-user-id",
        default=_env("AUTOSKILL_OPENCLAW_INSTALL_USER_ID", ""),
        help="Optional user id filter for mirroring skills into OpenClaw.",
    )
    parser.add_argument(
        "--openclaw-conversation-archive-enabled",
        default=_env("AUTOSKILL_OPENCLAW_CONVERSATION_ARCHIVE_ENABLED", "1"),
        help="Persist received OpenClaw conversations locally for replay/offline use: 1|0",
    )
    parser.add_argument(
        "--openclaw-conversation-archive-dir",
        default=_env("AUTOSKILL_OPENCLAW_CONVERSATION_ARCHIVE_DIR", ""),
        help="Local directory for archived OpenClaw conversations (JSONL).",
    )
    parser.add_argument(
        "--openclaw-session-idle-timeout-s",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_SESSION_IDLE_TIMEOUT_S", "0")),
        help="Optional idle timeout (seconds) to auto-close active sessions for extraction fallback. 0 disables.",
    )
    parser.add_argument(
        "--openclaw-session-max-turns",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_SESSION_MAX_TURNS", "20")),
        help="Auto-close long-lived sessions after N archived turns even if session_id never changes. 0 disables.",
    )
    parser.add_argument(
        "--openclaw-usage-tracking-enabled",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_TRACKING_ENABLED", "1"),
        help="Track per-skill retrieval/usage counters in OpenClaw plugin flow: 1|0",
    )
    parser.add_argument(
        "--openclaw-usage-infer-enabled",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_INFER_ENABLED", "1"),
        help="Enable inferred usage counters (separate from explicit counters): 1|0",
    )
    parser.add_argument(
        "--openclaw-usage-infer-from-selected-ids",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_INFER_FROM_SELECTED_IDS", "1"),
        help="Infer used skills from selected_for_use/context ids when explicit signal is absent: 1|0",
    )
    parser.add_argument(
        "--openclaw-usage-infer-from-message-mentions",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_INFER_FROM_MESSAGE_MENTIONS", "1"),
        help="Infer used skills by matching retrieval hit ids/names in assistant/tool messages: 1|0",
    )
    parser.add_argument(
        "--openclaw-usage-infer-max-message-chars",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_USAGE_INFER_MAX_MESSAGE_CHARS", "6000")),
        help="Maximum assistant/tool message chars scanned for inferred usage per turn.",
    )
    parser.add_argument(
        "--openclaw-usage-infer-manifest-path",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_INFER_MANIFEST_PATH", ""),
        help="Optional JSON path for inferred usage counters persistence.",
    )
    parser.add_argument(
        "--openclaw-usage-prune-enabled",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_PRUNE_ENABLED", "0"),
        help="Enable stale-skill auto-pruning driven by usage counters: 1|0",
    )
    parser.add_argument(
        "--openclaw-usage-prune-require-explicit-used-signal",
        default=_env("AUTOSKILL_OPENCLAW_USAGE_PRUNE_REQUIRE_EXPLICIT_USED_SIGNAL", "1"),
        help="Allow prune only when current payload carries explicit used_skill_ids: 1|0",
    )
    parser.add_argument(
        "--openclaw-usage-prune-min-retrieved",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_USAGE_PRUNE_MIN_RETRIEVED", "40")),
        help="Auto-prune threshold: minimum retrieved count before a skill is eligible for pruning.",
    )
    parser.add_argument(
        "--openclaw-usage-prune-max-used",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_USAGE_PRUNE_MAX_USED", "0")),
        help="Auto-prune threshold: prune when used <= this value once min retrieved threshold is reached.",
    )
    parser.add_argument(
        "--openclaw-usage-max-hits-per-turn",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_USAGE_MAX_HITS_PER_TURN", "8")),
        help="Maximum tracked retrieval hits per turn for usage accounting.",
    )
    parser.add_argument(
        "--openclaw-usage-max-pending-sessions",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_USAGE_MAX_PENDING_SESSIONS", "4096")),
        help="Maximum in-memory pending session retrieval snapshots.",
    )
    parser.add_argument(
        "--openclaw-usage-pending-ttl-s",
        type=int,
        default=int(_env("AUTOSKILL_OPENCLAW_USAGE_PENDING_TTL_S", str(6 * 3600))),
        help="TTL in seconds for pending retrieval snapshots.",
    )
    return parser


def main() -> None:
    """Run main."""
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

    autoskill_cfg = AutoSkillConfig(
        llm=llm_cfg,
        embeddings=emb_cfg,
        store=store_cfg,
        maintenance_strategy=("llm" if llm_provider != "mock" else "heuristic"),
    )
    # OpenClaw plugin uses its own prompt profile for agentic trajectory extraction/maintenance.
    install_openclaw_agentic_prompt_profile()
    sdk = AutoSkill(
        autoskill_cfg,
        extractor=OpenClawTrajectorySkillExtractor(autoskill_cfg),
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

    main_turn_enabled = _is_truthy(args.openclaw_main_turn_extract, default=False)
    target_base_url = str(args.openclaw_proxy_target_base_url or "").strip()
    agent_end_raw = str(args.openclaw_agent_end_extract or "").strip()
    agent_end_explicit = bool(agent_end_raw) or bool(_env("AUTOSKILL_OPENCLAW_AGENT_END_EXTRACT", "").strip()) or _cli_flag_present(
        "--openclaw-agent-end-extract"
    )
    agent_end_extract_enabled = _resolve_agent_end_extract_enabled(
        main_turn_enabled=bool(main_turn_enabled),
        target_configured=bool(target_base_url),
        raw_value=agent_end_raw,
        explicit=bool(agent_end_explicit),
    )
    main_turn_proxy_cfg = OpenClawMainTurnProxyConfig(
        enabled=bool(main_turn_enabled),
        target_base_url=target_base_url,
        target_api_key=(str(args.openclaw_proxy_target_api_key or "").strip() or None),
        ingest_window=int(args.ingest_window),
        connect_timeout_s=float(args.openclaw_proxy_connect_timeout_s),
        read_timeout_s=float(args.openclaw_proxy_read_timeout_s),
        agent_end_extract_enabled=bool(agent_end_extract_enabled),
    ).normalize()
    skill_install_cfg = OpenClawSkillInstallConfig(
        mode=str(args.openclaw_skill_install_mode or "openclaw_mirror"),
        skills_dir=str(args.openclaw_skills_dir or ""),
        install_user_id=str(args.openclaw_install_user_id or ""),
    ).normalize()
    conversation_archive_cfg = OpenClawConversationArchiveConfig(
        enabled=_is_truthy(args.openclaw_conversation_archive_enabled, default=True),
        archive_dir=str(args.openclaw_conversation_archive_dir or ""),
        session_idle_timeout_seconds=int(args.openclaw_session_idle_timeout_s),
        session_max_turns=int(args.openclaw_session_max_turns),
    ).normalize()
    usage_tracking_cfg = OpenClawUsageTrackingConfig(
        enabled=_is_truthy(args.openclaw_usage_tracking_enabled, default=True),
        infer_enabled=_is_truthy(args.openclaw_usage_infer_enabled, default=True),
        infer_from_selected_ids=_is_truthy(args.openclaw_usage_infer_from_selected_ids, default=True),
        infer_from_message_mentions=_is_truthy(args.openclaw_usage_infer_from_message_mentions, default=True),
        infer_max_message_chars=int(args.openclaw_usage_infer_max_message_chars),
        infer_manifest_path=str(args.openclaw_usage_infer_manifest_path or ""),
        prune_enabled=_is_truthy(args.openclaw_usage_prune_enabled, default=False),
        prune_require_explicit_used_signal=_is_truthy(
            args.openclaw_usage_prune_require_explicit_used_signal,
            default=True,
        ),
        prune_min_retrieved=int(args.openclaw_usage_prune_min_retrieved),
        prune_max_used=int(args.openclaw_usage_prune_max_used),
        max_hits_per_turn=int(args.openclaw_usage_max_hits_per_turn),
        max_pending_sessions=int(args.openclaw_usage_max_pending_sessions),
        pending_ttl_seconds=int(args.openclaw_usage_pending_ttl_s),
    ).normalize()

    runtime = OpenClawSkillRuntime(
        sdk=sdk,
        llm_config=llm_cfg,
        embeddings_config=emb_cfg,
        config=cfg,
        main_turn_proxy_config=main_turn_proxy_cfg,
        skill_install_config=skill_install_cfg,
        conversation_archive_config=conversation_archive_cfg,
        usage_tracking_config=usage_tracking_cfg,
    )
    server = runtime.create_server(host=str(args.host), port=int(args.port))
    host, port = server.server_address[:2]
    print(f"AutoSkill OpenClaw Skill Service: http://{host}:{port}")
    endpoints = [
        "/v1/models",
        "/v1/autoskill/openclaw/hooks/before_agent_start",
        "/v1/autoskill/openclaw/hooks/agent_end",
        "/v1/autoskill/openclaw/turn",
        "/v1/autoskill/openclaw/skills/sync",
        "/v1/autoskill/openclaw/usage/stats",
        "/v1/autoskill/retrieval/preview",
        "/v1/autoskill/conversations/import",
        "/v1/autoskill/extractions",
        "/v1/autoskill/capabilities",
        "/health",
    ]
    if main_turn_proxy_cfg.chat_endpoint_enabled:
        endpoints.insert(1, "/v1/chat/completions")
    print("Endpoints: " + ", ".join(endpoints))
    if main_turn_proxy_cfg.enabled and not main_turn_proxy_cfg.chat_endpoint_enabled:
        print(
            "[openclaw-plugin] warning: AUTOSKILL_OPENCLAW_MAIN_TURN_EXTRACT=1 but "
            "AUTOSKILL_OPENCLAW_PROXY_TARGET_BASE_URL is empty; /v1/chat/completions will return 503."
        )
    print(
        "[openclaw-plugin] extraction routing: "
        f"main_turn_enabled={int(bool(main_turn_proxy_cfg.enabled))} "
        f"chat_proxy={int(bool(main_turn_proxy_cfg.chat_endpoint_enabled))} "
        f"agent_end_extract={int(bool(main_turn_proxy_cfg.agent_end_extract_enabled))}"
    )
    if (
        main_turn_proxy_cfg.enabled
        and main_turn_proxy_cfg.chat_endpoint_enabled
        and main_turn_proxy_cfg.agent_end_extract_enabled
    ):
        print(
            "[openclaw-plugin] warning: both main-turn proxy extraction and agent_end extraction are enabled; "
            "this can cause duplicate extraction/maintenance events. Prefer keeping agent_end extraction disabled "
            "when proxy target is configured."
        )
    if conversation_archive_cfg.enabled:
        print(
            "[openclaw-plugin] conversation archive enabled: "
            f"dir={conversation_archive_cfg.archive_dir} "
            f"idle_timeout_s={conversation_archive_cfg.session_idle_timeout_seconds} "
            f"max_turns={conversation_archive_cfg.session_max_turns}"
        )
    if skill_install_cfg.enabled:
        print(
            "[openclaw-plugin] skill install mirror enabled: "
            f"dir={skill_install_cfg.skills_dir} "
            f"user={skill_install_cfg.install_user_id or '<dynamic>'}"
        )
    if usage_tracking_cfg.enabled:
        print(
            "[openclaw-plugin] usage tracking enabled: "
            f"infer={int(bool(usage_tracking_cfg.infer_enabled))} "
            f"prune={int(bool(usage_tracking_cfg.prune_enabled))} "
            f"prune_require_used={int(bool(usage_tracking_cfg.prune_require_explicit_used_signal))} "
            f"min_retrieved={usage_tracking_cfg.prune_min_retrieved} "
            f"max_used={usage_tracking_cfg.prune_max_used}"
        )
    server.serve_forever()


if __name__ == "__main__":
    main()
