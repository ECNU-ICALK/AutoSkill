"""
Batch import OpenAI-format conversations and auto-extract skills.

Usage:
  python3 -m examples.import_openai_conversations \
    --file ./data/dialogues.jsonl \
    --user-id u1 \
    --llm-provider generic \
    --llm-model gpt-5.2 \
    --llm-base-url http://127.0.0.1:9000/v1
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

from autoskill import AutoSkill, AutoSkillConfig


def _env(name: str, default: str = "") -> str:
    val = os.getenv(name)
    return val if val is not None and val.strip() else default


def _build_llm_config(args: argparse.Namespace) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {"provider": str(args.llm_provider or "mock").strip()}
    if str(args.llm_model or "").strip():
        cfg["model"] = str(args.llm_model).strip()
    if str(args.llm_base_url or "").strip():
        cfg["base_url"] = str(args.llm_base_url).strip()
    if str(args.llm_api_key or "").strip():
        cfg["api_key"] = str(args.llm_api_key).strip()
    if str(args.auth_mode or "").strip():
        cfg["auth_mode"] = str(args.auth_mode).strip()
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="Import OpenAI-format conversations and extract skills.")
    parser.add_argument("--file", required=True, help="Path to .json or .jsonl OpenAI-format conversation file.")
    parser.add_argument("--user-id", default="u1", help="Target user id.")
    parser.add_argument("--hint", default="", help="Optional extraction hint.")
    parser.add_argument("--max-messages-per-conversation", type=int, default=0, help="0 means no clipping.")
    parser.add_argument(
        "--llm-provider",
        default=_env("AUTOSKILL_LLM_PROVIDER", "mock"),
        help="mock|generic|glm|internlm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=_env("AUTOSKILL_LLM_MODEL", ""), help="LLM model id.")
    parser.add_argument("--llm-base-url", default=_env("AUTOSKILL_LLM_BASE_URL", ""), help="LLM base URL.")
    parser.add_argument("--llm-api-key", default=_env("AUTOSKILL_LLM_API_KEY", ""), help="LLM API key.")
    parser.add_argument("--auth-mode", default=_env("AUTOSKILL_LLM_AUTH_MODE", ""), help="Optional auth mode.")
    parser.add_argument(
        "--store-path",
        default=_env("AUTOSKILL_STORE_PATH", ""),
        help="Optional local SkillBank path. Empty means config default.",
    )
    args = parser.parse_args()

    llm_cfg = _build_llm_config(args)
    store_cfg: Dict[str, Any] = {"provider": "local"}
    if str(args.store_path or "").strip():
        store_cfg["path"] = str(args.store_path).strip()

    sdk = AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings={"provider": "hashing", "dims": 256},
            store=store_cfg,
        )
    )

    result = sdk.import_openai_conversations(
        user_id=str(args.user_id).strip() or "u1",
        file_path=str(args.file),
        hint=(str(args.hint).strip() or None),
        continue_on_error=True,
        max_messages_per_conversation=int(args.max_messages_per_conversation or 0),
        metadata={"channel": "example_import_openai_conversations"},
    )

    print("Import completed.")
    print(
        f"conversations={result.get('total_conversations', 0)} "
        f"processed={result.get('processed', 0)} "
        f"failed={result.get('failed', 0)} "
        f"upserted={result.get('upserted_count', 0)}"
    )
    skills = list(result.get("skills") or [])
    for i, s in enumerate(skills, start=1):
        print(f"{i}. {s.get('name', '')} ({s.get('version', '')})")
    errors = list(result.get("errors") or [])
    if errors:
        print("Errors:")
        for e in errors[:20]:
            print(f"- #{e.get('index')}: {e.get('error')}")


if __name__ == "__main__":
    main()
