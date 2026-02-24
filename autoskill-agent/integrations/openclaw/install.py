#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import stat
import subprocess
from pathlib import Path


def _default_source_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_text(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _render_env(args: argparse.Namespace, source_dir: Path, workspace_dir: Path) -> str:
    return (
        f"AUTOSKILL_AGENT_SOURCE_DIR={source_dir}\n"
        f"AUTOSKILL_AGENT_PYTHON={args.python_bin}\n"
        f"AUTOSKILL_AGENT_WORKSPACE_DIR={workspace_dir}\n"
        f"AUTOSKILL_AGENT_SKILLS_DIR={workspace_dir / 'skills' / 'autoskill-agent'}\n"
        f"AUTOSKILL_AGENT_STATE_DIR={workspace_dir / 'autoskill-agent' / 'state'}\n"
        f"AUTOSKILL_AGENT_TRAJECTORY_LOG={workspace_dir / 'autoskill-agent' / 'success_trajectories.jsonl'}\n"
        f"AUTOSKILL_AGENT_OFFICIAL_LLM_URL={args.official_llm_url}\n"
        f"AUTOSKILL_AGENT_OFFICIAL_LLM_MODEL={args.official_llm_model}\n"
        f"AUTOSKILL_AGENT_OFFICIAL_LLM_API_KEY={args.official_llm_api_key}\n"
        f"AUTOSKILL_AGENT_EXTRA_LLM_URL={args.extra_llm_url}\n"
        f"AUTOSKILL_AGENT_EXTRA_LLM_MODEL={args.extra_llm_model}\n"
        f"AUTOSKILL_AGENT_EXTRA_LLM_API_KEY={args.extra_llm_api_key}\n"
        f"AUTOSKILL_AGENT_EMBEDDING_URL={args.embedding_url}\n"
        f"AUTOSKILL_AGENT_EMBEDDING_MODEL={args.embedding_model}\n"
        f"AUTOSKILL_AGENT_EMBEDDING_API_KEY={args.embedding_api_key}\n"
        f"AUTOSKILL_AGENT_EMBEDDING_TOP_K={args.embedding_top_k}\n"
        f"AUTOSKILL_AGENT_MIN_SUCCESS_SCORE={args.min_success_score}\n"
        f"AUTOSKILL_AGENT_POLL_INTERVAL_S={args.poll_interval_s}\n"
    )


def _render_run_sh() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$ROOT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

if [ -z "${AUTOSKILL_AGENT_SOURCE_DIR:-}" ]; then
  echo "[autoskill-agent] AUTOSKILL_AGENT_SOURCE_DIR is empty."
  exit 1
fi

exec "${AUTOSKILL_AGENT_PYTHON:-python3}" "${AUTOSKILL_AGENT_SOURCE_DIR}/plugin.py" \
  --workspace-dir "${AUTOSKILL_AGENT_WORKSPACE_DIR:-$HOME/.openclaw}" \
  --skills-dir "${AUTOSKILL_AGENT_SKILLS_DIR:-$HOME/.openclaw/skills/autoskill-agent}" \
  --state-dir "${AUTOSKILL_AGENT_STATE_DIR:-$HOME/.openclaw/autoskill-agent/state}" \
  --trajectory-log "${AUTOSKILL_AGENT_TRAJECTORY_LOG:-$HOME/.openclaw/autoskill-agent/success_trajectories.jsonl}" \
  --official-llm-url "${AUTOSKILL_AGENT_OFFICIAL_LLM_URL:-}" \
  --official-llm-model "${AUTOSKILL_AGENT_OFFICIAL_LLM_MODEL:-}" \
  --official-llm-api-key "${AUTOSKILL_AGENT_OFFICIAL_LLM_API_KEY:-}" \
  --extra-llm-url "${AUTOSKILL_AGENT_EXTRA_LLM_URL:-}" \
  --extra-llm-model "${AUTOSKILL_AGENT_EXTRA_LLM_MODEL:-}" \
  --extra-llm-api-key "${AUTOSKILL_AGENT_EXTRA_LLM_API_KEY:-}" \
  --llm-url "${AUTOSKILL_AGENT_LLM_URL:-}" \
  --llm-model "${AUTOSKILL_AGENT_LLM_MODEL:-}" \
  --llm-api-key "${AUTOSKILL_AGENT_LLM_API_KEY:-}" \
  --embedding-url "${AUTOSKILL_AGENT_EMBEDDING_URL:-}" \
  --embedding-model "${AUTOSKILL_AGENT_EMBEDDING_MODEL:-}" \
  --embedding-api-key "${AUTOSKILL_AGENT_EMBEDDING_API_KEY:-}" \
  --embedding-top-k "${AUTOSKILL_AGENT_EMBEDDING_TOP_K:-8}" \
  --min-success-score "${AUTOSKILL_AGENT_MIN_SUCCESS_SCORE:-0.65}" \
  --poll-interval-s "${AUTOSKILL_AGENT_POLL_INTERVAL_S:-3}"
"""


def _render_start_sh() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/autoskill-agent.pid"
LOG_FILE="$ROOT_DIR/autoskill-agent.log"

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" || true)"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    echo "[autoskill-agent] already running, pid=$PID"
    exit 0
  fi
fi

nohup "$ROOT_DIR/run.sh" >"$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "[autoskill-agent] started, pid=$(cat "$PID_FILE"), log=$LOG_FILE"
"""


def _render_stop_sh() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/autoskill-agent.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "[autoskill-agent] not running."
  exit 0
fi
PID="$(cat "$PID_FILE" || true)"
if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
  kill "$PID" || true
  sleep 0.5
fi
rm -f "$PID_FILE"
echo "[autoskill-agent] stopped."
"""


def _render_status_sh() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/autoskill-agent.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "[autoskill-agent] status=stopped"
  exit 0
fi
PID="$(cat "$PID_FILE" || true)"
if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
  echo "[autoskill-agent] status=running pid=$PID"
else
  echo "[autoskill-agent] status=stopped"
fi
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install AutoSkill-Agent as an OpenClaw external plugin.")
    parser.add_argument("--workspace-dir", default="~/.openclaw", help="OpenClaw workspace directory.")
    parser.add_argument("--install-dir", default="~/.openclaw/plugins/autoskill-agent", help="Plugin install folder.")
    parser.add_argument("--source-dir", default="", help="Path to autoskill-agent source directory.")
    parser.add_argument("--python-bin", default="python3", help="Python executable to run plugin.")
    parser.add_argument("--official-llm-url", default="", help="Official OpenAI-compatible base URL.")
    parser.add_argument("--official-llm-model", default="", help="Official LLM model name.")
    parser.add_argument("--official-llm-api-key", default="", help="Official LLM API key.")
    parser.add_argument("--extra-llm-url", default="", help="Extra OpenAI-compatible base URL.")
    parser.add_argument("--extra-llm-model", default="", help="Extra LLM model name.")
    parser.add_argument("--extra-llm-api-key", default="", help="Extra LLM API key.")
    parser.add_argument("--embedding-url", default="", help="Embedding OpenAI-compatible base URL.")
    parser.add_argument("--embedding-model", default="", help="Embedding model name.")
    parser.add_argument("--embedding-api-key", default="", help="Embedding API key.")
    parser.add_argument("--embedding-top-k", type=int, default=8, help="Top-k for embedding retrieval.")
    parser.add_argument("--min-success-score", type=float, default=0.65)
    parser.add_argument("--poll-interval-s", type=float, default=3.0)
    parser.add_argument("--start", action="store_true", help="Start service immediately after install.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    workspace_dir = Path(os.path.expanduser(str(args.workspace_dir))).resolve()
    install_dir = Path(os.path.expanduser(str(args.install_dir))).resolve()
    source_dir = (
        Path(os.path.expanduser(str(args.source_dir))).resolve()
        if str(args.source_dir).strip()
        else _default_source_dir().resolve()
    )

    if not (source_dir / "plugin.py").exists():
        raise SystemExit(f"Invalid source dir, missing plugin.py: {source_dir}")

    install_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "skills" / "autoskill-agent").mkdir(parents=True, exist_ok=True)
    (workspace_dir / "autoskill-agent" / "state").mkdir(parents=True, exist_ok=True)

    env_path = install_dir / ".env"
    if not env_path.exists():
        _write_text(env_path, _render_env(args, source_dir=source_dir, workspace_dir=workspace_dir))

    _write_text(install_dir / ".env.example", _render_env(args, source_dir=source_dir, workspace_dir=workspace_dir))
    _write_text(install_dir / "run.sh", _render_run_sh(), executable=True)
    _write_text(install_dir / "start.sh", _render_start_sh(), executable=True)
    _write_text(install_dir / "stop.sh", _render_stop_sh(), executable=True)
    _write_text(install_dir / "status.sh", _render_status_sh(), executable=True)

    print("[autoskill-agent] installed.")
    print("[autoskill-agent] install_dir:", install_dir)
    print("[autoskill-agent] workspace_dir:", workspace_dir)
    print("[autoskill-agent] env:", env_path)
    print("[autoskill-agent] start:", install_dir / "start.sh")
    print("[autoskill-agent] stop:", install_dir / "stop.sh")
    print("[autoskill-agent] status:", install_dir / "status.sh")

    if args.start:
        subprocess.run([str(install_dir / "start.sh")], check=False)


if __name__ == "__main__":
    main()
