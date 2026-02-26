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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _default_repo_dir() -> Path:
    # OpenClaw-Plugin/install.py -> repo root is parent directory.
    return Path(__file__).resolve().parents[1]


def _default_adapter_dir(workspace_dir: Path) -> Path:
    return (workspace_dir / "extensions" / ADAPTER_PLUGIN_ID).resolve()


def _sync_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _load_json_dict(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Invalid JSON file: {path}. Please fix it before installation.") from e
    return obj if isinstance(obj, dict) else {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert_openclaw_plugin_config(
    *,
    workspace_dir: Path,
    adapter_dir: Path,
    proxy_port: int,
) -> Path:
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
    cfg.setdefault("skillScope", "all")
    cfg.setdefault("topK", 1)
    cfg.setdefault("minScore", 0.4)
    cfg.setdefault("recallEnabled", True)
    cfg.setdefault("extractOnAgentEnd", True)
    cfg.setdefault("successOnly", True)
    entry["config"] = cfg
    entries[ADAPTER_PLUGIN_ID] = entry

    _save_json(conf_path, root)
    return conf_path


def _env_template(args: argparse.Namespace, *, repo_dir: Path, workspace_dir: Path) -> str:
    store_dir = Path(str(args.store_dir or "")).expanduser()
    if not str(store_dir).strip():
        store_dir = workspace_dir / "autoskill" / "SkillBank"
    return (
        "# AutoSkill OpenClaw Plugin env\n"
        f"AUTOSKILL_REPO_DIR={repo_dir}\n"
        f"AUTOSKILL_PYTHON={args.python_bin}\n"
        "AUTOSKILL_PROXY_HOST=127.0.0.1\n"
        f"AUTOSKILL_PROXY_PORT={args.proxy_port}\n"
        f"AUTOSKILL_STORE_DIR={store_dir}\n"
        "AUTOSKILL_USER_ID=openclaw_user\n"
        "AUTOSKILL_SKILL_SCOPE=all\n"
        "AUTOSKILL_REWRITE_MODE=always\n"
        "AUTOSKILL_MIN_SCORE=0.4\n"
        "AUTOSKILL_TOP_K=1\n"
        "AUTOSKILL_HISTORY_TURNS=100\n"
        "AUTOSKILL_INGEST_WINDOW=6\n"
        "AUTOSKILL_EXTRACT_ENABLED=1\n"
        "AUTOSKILL_MAX_BG_EXTRACT_JOBS=2\n"
        f"AUTOSKILL_LLM_PROVIDER={args.llm_provider}\n"
        f"AUTOSKILL_LLM_MODEL={args.llm_model}\n"
        f"AUTOSKILL_EMBEDDINGS_PROVIDER={args.embeddings_provider}\n"
        f"AUTOSKILL_EMBEDDINGS_MODEL={args.embeddings_model}\n"
        f"AUTOSKILL_PROXY_MODELS={args.served_models_json}\n"
        f"AUTOSKILL_PROXY_MODELS_JSON={args.served_models_json}\n"
        "AUTOSKILL_PROXY_API_KEY=\n"
        "INTERNLM_API_KEY=\n"
        "DASHSCOPE_API_KEY=\n"
        "OPENAI_API_KEY=\n"
        "GLM_API_KEY=\n"
        "AUTOSKILL_GENERIC_API_KEY=\n"
    )


def _run_sh() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi
exec "${AUTOSKILL_PYTHON:-python3}" "${AUTOSKILL_REPO_DIR}/OpenClaw-Plugin/run_proxy.py"
"""


def _start_sh() -> str:
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
    parser = argparse.ArgumentParser(description="Install AutoSkill OpenClaw plugin sidecar.")
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

    if not (repo_dir / "OpenClaw-Plugin" / "run_proxy.py").exists():
        raise SystemExit(f"Invalid repo dir, missing OpenClaw-Plugin/run_proxy.py: {repo_dir}")
    if not (repo_dir / "OpenClaw-Plugin" / "service_runtime.py").exists():
        raise SystemExit(f"Invalid repo dir, missing OpenClaw-Plugin/service_runtime.py: {repo_dir}")
    if not (repo_dir / "examples" / "interactive_chat.py").exists():
        raise SystemExit(f"Invalid repo dir, missing examples/interactive_chat.py: {repo_dir}")
    adapter_src = (repo_dir / "OpenClaw-Plugin" / "adapter").resolve()
    if not (adapter_src / "index.js").exists():
        raise SystemExit(f"Invalid repo dir, missing OpenClaw-Plugin/adapter/index.js: {repo_dir}")
    if not (adapter_src / "openclaw.plugin.json").exists():
        raise SystemExit(f"Invalid repo dir, missing OpenClaw-Plugin/adapter/openclaw.plugin.json: {repo_dir}")
    if not (adapter_src / "package.json").exists():
        raise SystemExit(f"Invalid repo dir, missing OpenClaw-Plugin/adapter/package.json: {repo_dir}")

    install_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "autoskill" / "SkillBank").mkdir(parents=True, exist_ok=True)

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
    print("OpenClaw plugin endpoints:")
    print(f"  base_url: http://127.0.0.1:{int(args.proxy_port)}/v1")
    print("  hook API: POST /v1/autoskill/openclaw/hooks/before_agent_start")
    print("  hook API: POST /v1/autoskill/openclaw/hooks/agent_end")
    print("  compat API: POST /v1/autoskill/openclaw/turn")
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
