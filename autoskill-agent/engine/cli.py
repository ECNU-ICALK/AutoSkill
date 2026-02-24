from __future__ import annotations

import argparse
import json
import os
import time

from engine.core import env
from engine.runtime import AutoSkillAgentRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AutoSkill-Agent plugin for OpenClaw")
    parser.add_argument(
        "--workspace-dir",
        default=env("AUTOSKILL_AGENT_WORKSPACE_DIR", "~/.openclaw"),
        help="OpenClaw workspace root.",
    )
    parser.add_argument(
        "--skills-dir",
        default=env("AUTOSKILL_AGENT_SKILLS_DIR", "~/.openclaw/skills/autoskill-agent"),
        help="Target external skills directory for generated SKILL.md folders.",
    )
    parser.add_argument(
        "--state-dir",
        default=env("AUTOSKILL_AGENT_STATE_DIR", "~/.openclaw/autoskill-agent/state"),
        help="Runtime state directory.",
    )
    parser.add_argument(
        "--trajectory-log",
        default=env("AUTOSKILL_AGENT_TRAJECTORY_LOG", "~/.openclaw/autoskill-agent/success_trajectories.jsonl"),
        help="Path to successful trajectory jsonl log.",
    )
    parser.add_argument(
        "--official-llm-url",
        default=env("AUTOSKILL_AGENT_OFFICIAL_LLM_URL", ""),
        help="OpenClaw official OpenAI-compatible base URL without /v1.",
    )
    parser.add_argument(
        "--official-llm-model",
        default=env("AUTOSKILL_AGENT_OFFICIAL_LLM_MODEL", ""),
        help="OpenClaw official model id.",
    )
    parser.add_argument(
        "--official-llm-api-key",
        default=env("AUTOSKILL_AGENT_OFFICIAL_LLM_API_KEY", ""),
        help="OpenClaw official API key (optional).",
    )
    parser.add_argument(
        "--extra-llm-url",
        default=env("AUTOSKILL_AGENT_EXTRA_LLM_URL", ""),
        help="Additional OpenAI-compatible base URL without /v1.",
    )
    parser.add_argument(
        "--extra-llm-model",
        default=env("AUTOSKILL_AGENT_EXTRA_LLM_MODEL", ""),
        help="Additional model id for fallback/augmentation.",
    )
    parser.add_argument(
        "--extra-llm-api-key",
        default=env("AUTOSKILL_AGENT_EXTRA_LLM_API_KEY", ""),
        help="Additional API key (optional).",
    )
    parser.add_argument(
        "--llm-url",
        default=env("AUTOSKILL_AGENT_LLM_URL", ""),
        help="Legacy single-LLM base URL without /v1.",
    )
    parser.add_argument(
        "--llm-model",
        default=env("AUTOSKILL_AGENT_LLM_MODEL", ""),
        help="Legacy single-LLM model id.",
    )
    parser.add_argument(
        "--llm-api-key",
        default=env("AUTOSKILL_AGENT_LLM_API_KEY", ""),
        help="Legacy single-LLM API key.",
    )
    parser.add_argument(
        "--embedding-url",
        default=env("AUTOSKILL_AGENT_EMBEDDING_URL", ""),
        help="OpenAI-compatible embedding base URL without /v1.",
    )
    parser.add_argument(
        "--embedding-model",
        default=env("AUTOSKILL_AGENT_EMBEDDING_MODEL", ""),
        help="Embedding model id.",
    )
    parser.add_argument(
        "--embedding-api-key",
        default=env("AUTOSKILL_AGENT_EMBEDDING_API_KEY", ""),
        help="Embedding API key.",
    )
    parser.add_argument(
        "--embedding-top-k",
        type=int,
        default=int(env("AUTOSKILL_AGENT_EMBEDDING_TOP_K", "8")),
        help="Top-k similar skills from embedding retrieval.",
    )
    parser.add_argument(
        "--min-success-score",
        type=float,
        default=float(env("AUTOSKILL_AGENT_MIN_SUCCESS_SCORE", "0.65")),
        help="Success threshold for trajectory filtering.",
    )
    parser.add_argument(
        "--poll-interval-s",
        type=float,
        default=float(env("AUTOSKILL_AGENT_POLL_INTERVAL_S", "3")),
        help="Polling interval in seconds for continuous mode.",
    )
    parser.add_argument("--once", action="store_true", help="Run one scan cycle and exit.")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    runtime = AutoSkillAgentRuntime(
        workspace_dir=str(args.workspace_dir),
        skills_dir=str(args.skills_dir),
        state_dir=str(args.state_dir),
        trajectory_log_path=str(args.trajectory_log),
        official_llm_url=str(args.official_llm_url),
        official_llm_api_key=str(args.official_llm_api_key),
        official_llm_model=str(args.official_llm_model),
        extra_llm_url=str(args.extra_llm_url),
        extra_llm_api_key=str(args.extra_llm_api_key),
        extra_llm_model=str(args.extra_llm_model),
        llm_url=str(args.llm_url),
        llm_api_key=str(args.llm_api_key),
        llm_model=str(args.llm_model),
        embedding_url=str(args.embedding_url),
        embedding_api_key=str(args.embedding_api_key),
        embedding_model=str(args.embedding_model),
        embedding_top_k=int(args.embedding_top_k),
        min_success_score=float(args.min_success_score),
    )

    if args.once:
        result = runtime.run_once()
        print("[autoskill-agent] once:", json.dumps(result, ensure_ascii=False))
        return

    poll = max(0.5, float(args.poll_interval_s))
    print("[autoskill-agent] started.")
    print("[autoskill-agent] workspace:", os.path.abspath(os.path.expanduser(str(args.workspace_dir))))
    print("[autoskill-agent] skills_dir:", os.path.abspath(os.path.expanduser(str(args.skills_dir))))
    print("[autoskill-agent] trajectory_log:", os.path.abspath(os.path.expanduser(str(args.trajectory_log))))
    while True:
        result = runtime.run_once()
        if result.get("captured", 0):
            print("[autoskill-agent] cycle:", json.dumps(result, ensure_ascii=False))
        time.sleep(poll)
