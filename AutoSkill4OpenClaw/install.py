#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import Optional

ADAPTER_PLUGIN_ID = "autoskill-openclaw-adapter"


def _write_text(path: Path, content: str, executable: bool = False) -> None:
    """Run write text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _default_repo_dir() -> Path:
    # AutoSkill4OpenClaw/install.py -> repo root is parent directory.
    """Run default repo dir."""
    return Path(__file__).resolve().parents[1]


def _default_adapter_dir(workspace_dir: Path) -> Path:
    """Run default adapter dir."""
    return (workspace_dir / "extensions" / ADAPTER_PLUGIN_ID).resolve()


def _sync_tree(src: Path, dst: Path) -> None:
    """Run sync tree."""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _load_json_dict(path: Path) -> dict:
    """Run load json dict."""
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Invalid JSON file: {path}. Please fix it before installation.") from e
    return obj if isinstance(obj, dict) else {}


def _save_json(path: Path, data: dict) -> None:
    """Run save json."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert_openclaw_plugin_config(
    *,
    workspace_dir: Path,
    adapter_dir: Path,
    proxy_port: int,
) -> Path:
    """Run upsert openclaw plugin config."""
    conf_path = (workspace_dir / "openclaw.json").resolve()
    root = _load_json_dict(conf_path)
    plugins = root.get("plugins")
    if not isinstance(plugins, dict):
        plugins = {}
        root["plugins"] = plugins

    load = plugins.get("load")
    if not isinstance(load, dict):
        load = {}
        plugins["load"] = load
    paths = load.get("paths")
    if not isinstance(paths, list):
        paths = []
        load["paths"] = paths
    adapter_dir_s = str(adapter_dir)
    if adapter_dir_s not in [str(x) for x in paths]:
        paths.append(adapter_dir_s)

    entries = plugins.get("entries")
    if not isinstance(entries, dict):
        entries = {}
        plugins["entries"] = entries
    entry = entries.get(ADAPTER_PLUGIN_ID)
    if not isinstance(entry, dict):
        entry = {}
    # One-click behavior: always enable adapter after installation.
    entry["enabled"] = True
    cfg = entry.get("config")
    if not isinstance(cfg, dict):
        cfg = {}
    cfg.setdefault("baseUrl", f"http://127.0.0.1:{int(proxy_port)}/v1")
    cfg.setdefault("runtimeMode", "embedded")
    cfg.setdefault("openclawSkillInstallMode", "openclaw_mirror")
    cfg.setdefault("skillScope", "all")
    cfg.setdefault("topK", 3)
    cfg.setdefault("minScore", 0.4)
    embedded_cfg = cfg.get("embedded")
    if not isinstance(embedded_cfg, dict):
        embedded_cfg = {}
    autoskill_dir = (workspace_dir / "autoskill").resolve()
    embedded_cfg.setdefault("skillBankDir", str((autoskill_dir / "SkillBank").resolve()))
    embedded_cfg.setdefault("openclawSkillsDir", str((workspace_dir / "workspace" / "skills").resolve()))
    embedded_cfg.setdefault("sessionArchiveDir", str((autoskill_dir / "embedded_sessions").resolve()))
    embedded_cfg.setdefault("sessionMaxTurns", 20)
    cfg["embedded"] = embedded_cfg
    skill_retrieval = cfg.get("skillRetrieval")
    if not isinstance(skill_retrieval, dict):
        skill_retrieval = {}
    skill_retrieval.setdefault("topK", 3)
    skill_retrieval.setdefault("maxChars", 1500)
    skill_retrieval.setdefault("minScore", 0.4)
    skill_retrieval.setdefault("injectionMode", "appendSystemContext")
    cfg["skillRetrieval"] = skill_retrieval
    cfg.setdefault("extractOnAgentEnd", True)
    cfg.setdefault("successOnly", True)
    entry["config"] = cfg
    entries[ADAPTER_PLUGIN_ID] = entry

    _save_json(conf_path, root)
    return conf_path


def _env_template(args: argparse.Namespace, *, repo_dir: Path, workspace_dir: Path) -> str:
    """Run env template."""
    store_dir = Path(str(args.store_dir or "")).expanduser()
    if not str(store_dir).strip():
        store_dir = workspace_dir / "autoskill" / "SkillBank"
    openclaw_skills_dir = (workspace_dir / "workspace" / "skills").resolve()
    conversation_archive_dir = (workspace_dir / "autoskill" / "conversations").resolve()
    return (
        "# AutoSkill4OpenClaw env\n"
        f"AUTOSKILL_REPO_DIR={repo_dir}\n"
        f"AUTOSKILL_PYTHON={args.python_bin}\n"
        "AUTOSKILL_PROXY_HOST=127.0.0.1\n"
        f"AUTOSKILL_PROXY_PORT={args.proxy_port}\n"
        "AUTOSKILL_BASE_URL=\n"
        "AUTOSKILL_PROXY_BASE_URL=\n"
        "AUTOSKILL_DOTENV=\n"
        f"AUTOSKILL_STORE_DIR={store_dir}\n"
        "AUTOSKILL_USER_ID=\n"
        "AUTOSKILL_SKILL_SCOPE=all\n"
        "AUTOSKILL_REWRITE_MODE=always\n"
        "AUTOSKILL_MIN_SCORE=0.4\n"
        "AUTOSKILL_TOP_K=3\n"
        "AUTOSKILL_MAX_INJECTED_CHARS=1500\n"
        "AUTOSKILL_SKILL_RETRIEVAL_ENABLED=\n"
        "AUTOSKILL_SKILL_RETRIEVAL_TOP_K=3\n"
        "AUTOSKILL_SKILL_RETRIEVAL_MAX_CHARS=1500\n"
        "AUTOSKILL_SKILL_RETRIEVAL_MIN_SCORE=0.4\n"
        "AUTOSKILL_SKILL_RETRIEVAL_INJECTION_MODE=appendSystemContext\n"
        "AUTOSKILL_HISTORY_TURNS=100\n"
        "AUTOSKILL_INGEST_WINDOW=6\n"
        "AUTOSKILL_OPENCLAW_INGEST_WINDOW=6\n"
        "AUTOSKILL_EXTRACT_ENABLED=1\n"
        "AUTOSKILL_MAX_BG_EXTRACT_JOBS=2\n"
        "AUTOSKILL_PROXY_EXTRACT_EVENT_DETAILS=1\n"
        "AUTOSKILL_PROXY_EXTRACT_EVENT_MAX_MD_CHARS=0\n"
        "AUTOSKILL_LIBRARY_DIRS=\n"
        "AUTOSKILL_OPENCLAW_MAIN_TURN_EXTRACT=1\n"
        "AUTOSKILL_OPENCLAW_AGENT_END_EXTRACT=\n"
        "AUTOSKILL_OPENCLAW_PROXY_TARGET_BASE_URL=\n"
        "AUTOSKILL_OPENCLAW_PROXY_TARGET_API_KEY=\n"
        "AUTOSKILL_OPENCLAW_PROXY_CONNECT_TIMEOUT_S=20\n"
        "AUTOSKILL_OPENCLAW_PROXY_READ_TIMEOUT_S=600\n"
        "AUTOSKILL_OPENCLAW_CONVERSATION_ARCHIVE_ENABLED=1\n"
        f"AUTOSKILL_OPENCLAW_CONVERSATION_ARCHIVE_DIR={conversation_archive_dir}\n"
        "AUTOSKILL_OPENCLAW_SESSION_IDLE_TIMEOUT_S=0\n"
        "AUTOSKILL_OPENCLAW_SESSION_MAX_TURNS=20\n"
        "AUTOSKILL_OPENCLAW_RUNTIME_MODE=embedded\n"
        "AUTOSKILL_OPENCLAW_NO_SIDECAR=\n"
        "AUTOSKILL_OPENCLAW_HOME=\n"
        "AUTOSKILL_OPENCLAW_SKILL_INSTALL_MODE=openclaw_mirror\n"
        f"AUTOSKILL_OPENCLAW_SKILLS_DIR={openclaw_skills_dir}\n"
        "AUTOSKILL_OPENCLAW_INSTALL_USER_ID=\n"
        f"AUTOSKILL_OPENCLAW_EMBEDDED_SESSION_DIR={(workspace_dir / 'autoskill' / 'embedded_sessions').resolve()}\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_SESSION_MAX_TURNS=20\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_BM25_TOP_K=8\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_MODES=openclaw-runtime,openclaw-runtime-subagent,openclaw-config-resolve,manual\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_TIMEOUT_MS=20000\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_MODEL_RETRIES=1\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_OPENCLAW_HOME=\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_BASE_URL=\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_API_KEY=\n"
        "AUTOSKILL_OPENCLAW_EMBEDDED_MANUAL_MODEL=\n"
        "AUTOSKILL_OPENCLAW_USAGE_TRACKING_ENABLED=1\n"
        "AUTOSKILL_OPENCLAW_USAGE_INFER_ENABLED=1\n"
        "AUTOSKILL_OPENCLAW_USAGE_INFER_FROM_SELECTED_IDS=1\n"
        "AUTOSKILL_OPENCLAW_USAGE_INFER_FROM_MESSAGE_MENTIONS=1\n"
        "AUTOSKILL_OPENCLAW_USAGE_INFER_MAX_MESSAGE_CHARS=6000\n"
        "AUTOSKILL_OPENCLAW_USAGE_INFER_MANIFEST_PATH=\n"
        "AUTOSKILL_OPENCLAW_USAGE_PRUNE_ENABLED=0\n"
        "AUTOSKILL_OPENCLAW_USAGE_PRUNE_REQUIRE_EXPLICIT_USED_SIGNAL=1\n"
        "AUTOSKILL_OPENCLAW_USAGE_PRUNE_MIN_RETRIEVED=40\n"
        "AUTOSKILL_OPENCLAW_USAGE_PRUNE_MAX_USED=0\n"
        "AUTOSKILL_OPENCLAW_USAGE_MAX_HITS_PER_TURN=8\n"
        "AUTOSKILL_OPENCLAW_USAGE_MAX_PENDING_SESSIONS=4096\n"
        "AUTOSKILL_OPENCLAW_USAGE_PENDING_TTL_S=21600\n"
        "AUTOSKILL_OPENCLAW_PROMPT_PACK_PATH=\n"
        f"AUTOSKILL_SKILLBANK_DIR={store_dir}\n"
        "AUTOSKILL_REPO_SKILLBANK_DIR=\n"
        f"AUTOSKILL_PROXY_MODELS={args.served_models_json}\n"
        f"AUTOSKILL_LLM_PROVIDER={args.llm_provider}\n"
        f"AUTOSKILL_LLM_MODEL={args.llm_model}\n"
        f"AUTOSKILL_EMBEDDINGS_PROVIDER={args.embeddings_provider}\n"
        f"AUTOSKILL_EMBEDDINGS_MODEL={args.embeddings_model}\n"
        f"AUTOSKILL_PROXY_MODELS_JSON={args.served_models_json}\n"
        "AUTOSKILL_PROXY_API_KEY=\n"
        "INTERNLM_API_KEY=\n"
        "DASHSCOPE_API_KEY=\n"
        "OPENAI_API_KEY=\n"
        "GLM_API_KEY=\n"
        "AUTOSKILL_GENERIC_API_KEY=\n"
    )


def _run_sh() -> str:
    """Run run sh."""
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi
exec "${AUTOSKILL_PYTHON:-python3}" "${AUTOSKILL_REPO_DIR}/AutoSkill4OpenClaw/run_proxy.py"
"""


def _start_sh() -> str:
    """Run start sh."""
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/autoskill-openclaw-plugin.pid"
LOG_FILE="$ROOT_DIR/autoskill-openclaw-plugin.log"

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE" || true)"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    echo "[autoskill-openclaw-plugin] already running pid=$PID"
    exit 0
  fi
fi

nohup "$ROOT_DIR/run.sh" >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"
echo "[autoskill-openclaw-plugin] started pid=$(cat "$PID_FILE") log=$LOG_FILE"
"""


def _stop_sh() -> str:
    """Run stop sh."""
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/autoskill-openclaw-plugin.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "[autoskill-openclaw-plugin] not running"
  exit 0
fi
PID="$(cat "$PID_FILE" || true)"
if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
  kill "$PID" || true
  sleep 0.5
fi
rm -f "$PID_FILE"
echo "[autoskill-openclaw-plugin] stopped"
"""


def _status_sh() -> str:
    """Run status sh."""
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/autoskill-openclaw-plugin.pid"
if [ ! -f "$PID_FILE" ]; then
  echo "[autoskill-openclaw-plugin] status=stopped"
  exit 0
fi
PID="$(cat "$PID_FILE" || true)"
if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
  echo "[autoskill-openclaw-plugin] status=running pid=$PID"
else
  echo "[autoskill-openclaw-plugin] status=stopped"
fi
"""


def build_parser() -> argparse.ArgumentParser:
    """Run build parser."""
    parser = argparse.ArgumentParser(description="Install AutoSkill4OpenClaw plugin runtime and adapter.")
    parser.add_argument("--workspace-dir", default="~/.openclaw")
    parser.add_argument("--install-dir", default="~/.openclaw/plugins/autoskill-openclaw-plugin")
    parser.add_argument(
        "--adapter-dir",
        default="",
        help="OpenClaw adapter install dir (default: <workspace>/extensions/autoskill-openclaw-adapter).",
    )
    parser.add_argument("--repo-dir", default="", help="AutoSkill repository root directory.")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--proxy-port", type=int, default=9100)
    parser.add_argument("--store-dir", default="", help="Default: <workspace>/autoskill/SkillBank")
    parser.add_argument("--llm-provider", default="internlm")
    parser.add_argument("--llm-model", default="intern-s1-pro")
    parser.add_argument("--embeddings-provider", default="qwen")
    parser.add_argument("--embeddings-model", default="text-embedding-v4")
    parser.add_argument(
        "--served-models-json",
        default='[{"id":"intern-s1-pro","object":"model","owned_by":"internlm"}]',
        help="JSON list exposed by /v1/models",
    )
    parser.add_argument(
        "--skip-openclaw-config-update",
        action="store_true",
        help="Do not write plugin load/config into ~/.openclaw/openclaw.json.",
    )
    parser.add_argument("--start", action="store_true")
    return parser


def main() -> None:
    """Run main."""
    args = build_parser().parse_args()
    workspace_dir = Path(os.path.expanduser(str(args.workspace_dir))).resolve()
    install_dir = Path(os.path.expanduser(str(args.install_dir))).resolve()
    repo_dir = (
        Path(os.path.expanduser(str(args.repo_dir))).resolve()
        if str(args.repo_dir).strip()
        else _default_repo_dir().resolve()
    )
    adapter_dir = (
        Path(os.path.expanduser(str(args.adapter_dir))).resolve()
        if str(args.adapter_dir).strip()
        else _default_adapter_dir(workspace_dir)
    )

    if not (repo_dir / "AutoSkill4OpenClaw" / "run_proxy.py").exists():
        raise SystemExit(f"Invalid repo dir, missing AutoSkill4OpenClaw/run_proxy.py: {repo_dir}")
    if not (repo_dir / "AutoSkill4OpenClaw" / "service_runtime.py").exists():
        raise SystemExit(f"Invalid repo dir, missing AutoSkill4OpenClaw/service_runtime.py: {repo_dir}")
    if not (repo_dir / "examples" / "interactive_chat.py").exists():
        raise SystemExit(f"Invalid repo dir, missing examples/interactive_chat.py: {repo_dir}")
    adapter_src = (repo_dir / "AutoSkill4OpenClaw" / "adapter").resolve()
    if not (adapter_src / "index.js").exists():
        raise SystemExit(f"Invalid repo dir, missing AutoSkill4OpenClaw/adapter/index.js: {repo_dir}")
    if not (adapter_src / "openclaw.plugin.json").exists():
        raise SystemExit(f"Invalid repo dir, missing AutoSkill4OpenClaw/adapter/openclaw.plugin.json: {repo_dir}")
    if not (adapter_src / "package.json").exists():
        raise SystemExit(f"Invalid repo dir, missing AutoSkill4OpenClaw/adapter/package.json: {repo_dir}")

    install_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "autoskill" / "SkillBank").mkdir(parents=True, exist_ok=True)
    (workspace_dir / "autoskill" / "embedded_sessions").mkdir(parents=True, exist_ok=True)
    (workspace_dir / "workspace" / "skills").mkdir(parents=True, exist_ok=True)

    env_path = install_dir / ".env"
    env_txt = _env_template(args, repo_dir=repo_dir, workspace_dir=workspace_dir)
    if not env_path.exists():
        _write_text(env_path, env_txt)
    _write_text(install_dir / ".env.example", env_txt)
    _write_text(install_dir / "run.sh", _run_sh(), executable=True)
    _write_text(install_dir / "start.sh", _start_sh(), executable=True)
    _write_text(install_dir / "stop.sh", _stop_sh(), executable=True)
    _write_text(install_dir / "status.sh", _status_sh(), executable=True)
    _sync_tree(adapter_src, adapter_dir)

    conf_path: Optional[Path] = None
    if not bool(args.skip_openclaw_config_update):
        conf_path = _upsert_openclaw_plugin_config(
            workspace_dir=workspace_dir,
            adapter_dir=adapter_dir,
            proxy_port=int(args.proxy_port),
        )

    print("[autoskill-openclaw-plugin] installed")
    print("[autoskill-openclaw-plugin] install_dir:", install_dir)
    print("[autoskill-openclaw-plugin] adapter_dir:", adapter_dir)
    print("[autoskill-openclaw-plugin] env:", env_path)
    print("[autoskill-openclaw-plugin] start:", install_dir / "start.sh")
    print("[autoskill-openclaw-plugin] stop:", install_dir / "stop.sh")
    print("[autoskill-openclaw-plugin] status:", install_dir / "status.sh")
    if conf_path is not None:
        print("[autoskill-openclaw-plugin] openclaw config updated:", conf_path)
    print("")
    print("AutoSkill service endpoints (used in sidecar mode or optional proxy mode):")
    print(f"  base_url: http://127.0.0.1:{int(args.proxy_port)}/v1")
    print("  hook API: POST /v1/autoskill/openclaw/hooks/before_agent_start")
    print("  hook API: POST /v1/autoskill/openclaw/hooks/agent_end")
    print("  compat API: POST /v1/autoskill/openclaw/turn")
    print("  mirror API: POST /v1/autoskill/openclaw/skills/sync")
    print("  api_key : <AUTOSKILL_PROXY_API_KEY or empty>")
    print("")
    print("Adapter plugin id:")
    print(f"  {ADAPTER_PLUGIN_ID}")
    print("")
    if conf_path is None:
        print("Note: --skip-openclaw-config-update was used.")
        print("      Please add adapter path and plugin entry into openclaw.json manually.")

    if args.start:
        subprocess.run([str(install_dir / "start.sh")], check=False)


if __name__ == "__main__":
    main()
