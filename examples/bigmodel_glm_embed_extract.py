"""
Online BigModel test: embedding-3 + GLM-4.7 (embed + extract + persist).

What it does:
- calls embedding-3 to embed a few texts
- ingests a single chat turn (LLM skill extraction + maintenance + vector upsert)
  - optionally pass a `--hint` to focus extraction on the desired skill
- searches the local skill set and prints top hits

Environment variables:
- `ZHIPUAI_API_KEY` / `BIGMODEL_API_KEY`: "id.secret"
- `AUTOSKILL_STORE_DIR`: default <repo_root>/Skills
- `BIGMODEL_AUTH_MODE`: auto/jwt/api_key (default: auto)
- `BIGMODEL_TOKEN_TIME_UNIT`: ms/s (default: ms)
- `BIGMODEL_BASE_URL`: default https://open.bigmodel.cn/api/paas/v4
- `BIGMODEL_GLM_MODEL`: default glm-4.7
- `BIGMODEL_EMBED_MODEL`: default embedding-3
- `BIGMODEL_MAX_TOKENS`: default 4096
- `BIGMODEL_LLM_EXTRA_BODY` / `BIGMODEL_EMB_EXTRA_BODY`: extra request body passthrough (JSON string)
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, Optional

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path
from autoskill.embeddings.factory import build_embeddings


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value is not None and value.strip() else default


def _require_api_key() -> str:
    key = os.getenv("ZHIPUAI_API_KEY") or os.getenv("BIGMODEL_API_KEY")
    if not key:
        raise SystemExit(
            "Missing API key. Set env var ZHIPUAI_API_KEY or BIGMODEL_API_KEY to your 'id.secret'."
        )
    return key


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


def main() -> None:
    parser = argparse.ArgumentParser(description="BigModel embedding + skill extraction test")
    parser.add_argument(
        "--user-message",
        default=_env(
            "AUTOSKILL_USER_MESSAGE",
            "Before each release: regression tests -> canary rollout -> monitor -> full rollout.",
        ),
    )
    parser.add_argument(
        "--assistant-message",
        default=_env("AUTOSKILL_ASSISTANT_MESSAGE", "Understood."),
    )
    parser.add_argument(
        "--query",
        default=_env("AUTOSKILL_QUERY", "How should I do a release?"),
    )
    parser.add_argument(
        "--hint",
        default=_env("AUTOSKILL_EXTRACT_HINT", ""),
        help="Optional extraction hint to focus on the desired reusable Skill.",
    )
    parser.add_argument(
        "--store-dir",
        default=_env(
            "AUTOSKILL_STORE_DIR",
            _env("AUTOSKILL_STORE_PATH", default_store_path()),
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Raise if the LLM fails to output parseable JSON for extraction/repair.",
    )
    args = parser.parse_args()

    api_key = _require_api_key()
    timeout_s = int(_env("AUTOSKILL_TIMEOUT_S", "120"))
    base_url = _env("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    auth_mode = _env("BIGMODEL_AUTH_MODE", "auto")
    token_time_unit = _env("BIGMODEL_TOKEN_TIME_UNIT", "ms")
    glm_model = _env("BIGMODEL_GLM_MODEL", "glm-4.7")
    emb_model = _env("BIGMODEL_EMBED_MODEL", "embedding-3")
    max_tokens = int(_env("BIGMODEL_MAX_TOKENS", "4096"))
    llm_extra = _env_json("BIGMODEL_LLM_EXTRA_BODY")
    emb_extra = _env_json("BIGMODEL_EMB_EXTRA_BODY")

    llm_cfg: Dict[str, Any] = {
        "provider": "glm",
        "model": glm_model,
        "api_key": api_key,
        "auth_mode": auth_mode,
        "token_time_unit": token_time_unit,
        "base_url": base_url,
        "max_tokens": max_tokens,
        "extra_body": llm_extra,
        "timeout_s": timeout_s,
    }
    emb_cfg: Dict[str, Any] = {
        "provider": "glm",
        "model": emb_model,
        "api_key": api_key,
        "auth_mode": auth_mode,
        "token_time_unit": token_time_unit,
        "base_url": base_url,
        "extra_body": emb_extra,
        "timeout_s": timeout_s,
    }

    embeddings = build_embeddings(emb_cfg)
    vectors = embeddings.embed([args.user_message, args.query])
    print("Embedding model:", emb_model)
    print("Embedding dims:", len(vectors[0]) if vectors else 0)

    sdk = AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings=emb_cfg,
            store={"provider": "local", "path": str(args.store_dir)},
            maintenance_strategy="llm",
            extra={"raise_on_llm_extract_error": bool(args.strict)} if args.strict else None,
        )
    )

    user_id = _env("AUTOSKILL_USER_ID", "u1")
    print("Store dir:", args.store_dir)
    print("Existing skills:", len(sdk.list(user_id=user_id)))

    sdk.ingest(
        user_id=user_id,
        messages=[
            {"role": "user", "content": str(args.user_message)},
            {"role": "assistant", "content": str(args.assistant_message)},
        ],
        metadata={"channel": "bigmodel-embed-extract"},
        hint=(str(args.hint).strip() or None),
    )

    skills = sdk.list(user_id=user_id)
    print("Skills after ingest:", len(skills))

    hits = sdk.search(str(args.query), user_id=user_id, limit=5)
    for h in hits:
        print(f"{h.score:.3f} - {h.skill.name}")

    if hits:
        print("\n--- SKILL.md ---")
        print(sdk.export_skill_md(hits[0].skill.id) or "")


if __name__ == "__main__":
    main()
