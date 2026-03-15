from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "AutoSkill4OpenClaw"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from install import _env_template, _upsert_openclaw_plugin_config  # noqa: E402


class OpenClawInstallTest(unittest.TestCase):
    def test_upsert_openclaw_plugin_config_writes_embedded_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            adapter_dir = workspace / "extensions" / "autoskill-openclaw-adapter"
            path = _upsert_openclaw_plugin_config(
                workspace_dir=workspace,
                adapter_dir=adapter_dir,
                proxy_port=9100,
            )
            data = json.loads(path.read_text(encoding="utf-8"))
            entry = data["plugins"]["entries"]["autoskill-openclaw-adapter"]
            cfg = entry["config"]
            embedded = cfg["embedded"]

            self.assertEqual(entry["enabled"], True)
            self.assertIn(str(adapter_dir), data["plugins"]["load"]["paths"])
            self.assertEqual(cfg["baseUrl"], "http://127.0.0.1:9100/v1")
            self.assertEqual(cfg["runtimeMode"], "embedded")
            self.assertEqual(cfg["openclawSkillInstallMode"], "openclaw_mirror")
            self.assertEqual(embedded["sessionMaxTurns"], 20)
            self.assertEqual(embedded["skillBankDir"], str((workspace / "autoskill" / "SkillBank").resolve()))
            self.assertEqual(embedded["openclawSkillsDir"], str((workspace / "workspace" / "skills").resolve()))
            self.assertEqual(
                embedded["sessionArchiveDir"],
                str((workspace / "autoskill" / "embedded_sessions").resolve()),
            )

    def test_upsert_openclaw_plugin_config_preserves_existing_runtime_choices(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            conf_path = workspace / "openclaw.json"
            conf_path.write_text(
                json.dumps(
                    {
                        "plugins": {
                            "entries": {
                                "autoskill-openclaw-adapter": {
                                    "enabled": True,
                                    "config": {
                                        "runtimeMode": "sidecar",
                                        "openclawSkillInstallMode": "store_only",
                                        "embedded": {"sessionMaxTurns": 99},
                                    },
                                }
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            _upsert_openclaw_plugin_config(
                workspace_dir=workspace,
                adapter_dir=workspace / "extensions" / "autoskill-openclaw-adapter",
                proxy_port=9100,
            )
            data = json.loads(conf_path.read_text(encoding="utf-8"))
            cfg = data["plugins"]["entries"]["autoskill-openclaw-adapter"]["config"]

            self.assertEqual(cfg["runtimeMode"], "sidecar")
            self.assertEqual(cfg["openclawSkillInstallMode"], "store_only")
            self.assertEqual(cfg["embedded"]["sessionMaxTurns"], 99)

    def test_env_template_contains_long_session_turn_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = _env_template(
                argparse.Namespace(
                    store_dir="",
                    python_bin="python3",
                    proxy_port=9100,
                    llm_provider="internlm",
                    llm_model="intern-s1-pro",
                    embeddings_provider="qwen",
                    embeddings_model="text-embedding-v4",
                    served_models_json='[{"id":"intern-s1-pro","object":"model","owned_by":"internlm"}]',
                ),
                repo_dir=Path(tmp),
                workspace_dir=Path(tmp) / ".openclaw",
            )
            self.assertIn("AUTOSKILL_OPENCLAW_SESSION_MAX_TURNS=20", text)

    def test_adapter_manifest_embedded_schema_stays_in_sync(self) -> None:
        manifest_path = _REPO_ROOT / "AutoSkill4OpenClaw" / "adapter" / "openclaw.plugin.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        embedded = data["configSchema"]["properties"]["embedded"]["properties"]
        self.assertIn("sessionMaxTurns", embedded)
        self.assertIn("promptPackPath", embedded)

    def test_env_example_covers_run_proxy_env_keys(self) -> None:
        env_source_paths = [
            _REPO_ROOT / "AutoSkill4OpenClaw" / "run_proxy.py",
            _REPO_ROOT / "AutoSkill4OpenClaw" / "adapter" / "index.js",
            _REPO_ROOT / "AutoSkill4OpenClaw" / "adapter" / "embedded_runtime.js",
        ]
        env_example_path = _REPO_ROOT / "AutoSkill4OpenClaw" / ".env.example"
        env_example_text = env_example_path.read_text(encoding="utf-8")
        env_example_keys = set(re.findall(r"^([A-Z0-9_]+)=", env_example_text, re.MULTILINE))
        env_keys = set()
        for path in env_source_paths:
            text = path.read_text(encoding="utf-8")
            env_keys.update(re.findall(r'_env\("([A-Z0-9_]+)"', text))
            env_keys.update(re.findall(r'env\.([A-Z0-9_]+)', text))
            env_keys.update(re.findall(r'process\.env\.([A-Z0-9_]+)', text))
        missing = sorted(key for key in env_keys if key.startswith("AUTOSKILL_") and key not in env_example_keys)
        self.assertEqual(missing, [])

    def test_install_cli_help_smoke(self) -> None:
        path = _REPO_ROOT / "AutoSkill4OpenClaw" / "install.py"
        proc = subprocess.run(
            [sys.executable, str(path), "--help"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("Install AutoSkill4OpenClaw plugin runtime and adapter.", proc.stdout)

    def test_run_proxy_cli_help_smoke(self) -> None:
        path = _REPO_ROOT / "AutoSkill4OpenClaw" / "run_proxy.py"
        proc = subprocess.run(
            [sys.executable, str(path), "--help"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("AutoSkill OpenClaw skill service", proc.stdout)


if __name__ == "__main__":
    unittest.main()
