"""
BigModel GLM + embedding-3 + LocalSkillStore (persistent online demo).

What it does:
- load existing skills/vectors from a local skill directory store
- ingest new messages (LLM skill extraction)
- persist updated skills/vectors back to disk (one skill folder per skill)
- search and export matched SKILL.md

Environment variables:
- `ZHIPUAI_API_KEY` / `BIGMODEL_API_KEY`: "id.secret"
- `AUTOSKILL_STORE_DIR`: default <repo_root>/Skills
- `BIGMODEL_AUTH_MODE`: auto/jwt/api_key (default: auto)
- `BIGMODEL_TOKEN_TIME_UNIT`: ms/s (default: ms)
- `BIGMODEL_BASE_URL`: default https://open.bigmodel.cn/api/paas/v4
- `BIGMODEL_GLM_MODEL`: default glm-4.7
- `BIGMODEL_EMBED_MODEL`: default embedding-3
- `BIGMODEL_MAX_TOKENS`: default 30000
- `BIGMODEL_LLM_EXTRA_BODY` / `BIGMODEL_EMB_EXTRA_BODY`: extra request body passthrough (JSON string)
"""

from __future__ import annotations

import json
import os

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path


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


def _env_json(name: str):
    raw = os.getenv(name)
    if not raw or not raw.strip():
        return None
    try:
        return json.loads(raw)
    except Exception as e:
        raise SystemExit(f"Invalid JSON in env {name}: {e}")


def main() -> None:
    api_key = _require_api_key()

    store_dir = _env(
        "AUTOSKILL_STORE_DIR",
        _env("AUTOSKILL_STORE_PATH", default_store_path()),
    )
    timeout_s = int(_env("AUTOSKILL_TIMEOUT_S", "120"))
    base_url = _env("BIGMODEL_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    auth_mode = _env("BIGMODEL_AUTH_MODE", "auto")
    token_time_unit = _env("BIGMODEL_TOKEN_TIME_UNIT", "ms")
    glm_model = _env("BIGMODEL_GLM_MODEL", "glm-4.7")
    emb_model = _env("BIGMODEL_EMBED_MODEL", "embedding-3")
    max_tokens = int(_env("BIGMODEL_MAX_TOKENS", "30000"))
    llm_extra = _env_json("BIGMODEL_LLM_EXTRA_BODY")
    emb_extra = _env_json("BIGMODEL_EMB_EXTRA_BODY")

    sdk = AutoSkill(
        AutoSkillConfig(
            llm={
                "provider": "glm",
                "model": glm_model,
                "api_key": api_key,
                "auth_mode": auth_mode,
                "token_time_unit": token_time_unit,
                "base_url": base_url,
                "max_tokens": max_tokens,
                "extra_body": llm_extra,
                "timeout_s": timeout_s,
            },
            embeddings={
                "provider": "glm",
                "model": emb_model,
                "api_key": api_key,
                "auth_mode": auth_mode,
                "token_time_unit": token_time_unit,
                "base_url": base_url,
                "extra_body": emb_extra,
                "timeout_s": timeout_s,
            },
            store={"provider": "local", "path": store_dir},
            maintenance_strategy="llm",
        )
    )

    user_id = "u1"
    print("Store dir:", store_dir)
    print("Existing skills:", len(sdk.list(user_id=user_id)))

    sdk.ingest(
        user_id=user_id,
        messages=[
            {
                "role": "user",
                "content": "Before each release: regression -> canary -> monitor -> full rollout.",
            },
            {"role": "assistant", "content": "Understood."},
        ],
        metadata={"channel": "bigmodel-persistent-demo"},
    )

    print("Skills after ingest:", len(sdk.list(user_id=user_id)))

    query = "How should I do a release?"
    hits = sdk.search(query, user_id=user_id, limit=3)
    for h in hits:
        print(f"{h.score:.3f} - {h.skill.name}")

    if hits:
        print("\n--- SKILL.md ---")
        print(sdk.export_skill_md(hits[0].skill.id) or "")


if __name__ == "__main__":
    main()
