"""Batch offline skill extraction for per-user OpenAI chat exports.

Loop through each user folder under `data/chat_messages_openai_by_user` and run
offline conversation extraction. The folder name is used as `user_id`.

Usage:
  python3 data/batch_extract_skills_by_user.py \
    --input-root data/chat_messages_openai_by_user \
    --llm-provider dashscope \
    --embeddings-provider dashscope
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


# Allow running this script without `pip install -e .`.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path
from autoskill.offline.conversation.extract import extract_from_conversation
from autoskill.offline.provider_config import (
    build_embeddings_config,
    build_llm_config,
    env,
    pick_default_provider,
)


def _none_if_empty(value: Any) -> Optional[str]:
    """Run none if empty."""
    s = str(value or "").strip()
    return s or None


def _default_input_root() -> str:
    """Run default input root."""
    p_plural = REPO_ROOT / "data" / "chat_messages_openai_by_user"
    p_singular = REPO_ROOT / "data" / "chat_message_openai_by_user"
    if p_plural.exists():
        return str(p_plural)
    if p_singular.exists():
        return str(p_singular)
    return str(p_plural)


def _find_user_dirs(root: Path) -> List[Path]:
    """Run find user dirs."""
    if not root.is_dir():
        raise ValueError(f"input root not found: {root}")
    out: List[Path] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        has_data = any(
            str(p.name).lower().endswith(".json") or str(p.name).lower().endswith(".jsonl")
            for p in child.rglob("*")
            if p.is_file()
        )
        if has_data:
            out.append(child)
    return out


def _build_sdk(args: argparse.Namespace) -> AutoSkill:
    """Run build sdk."""
    llm_provider = str(args.llm_provider or "mock").strip().lower() or "mock"

    llm_cfg = build_llm_config(
        str(args.llm_provider or ""),
        model=_none_if_empty(args.llm_model),
    )
    if str(args.llm_base_url or "").strip():
        llm_cfg["base_url"] = str(args.llm_base_url).strip()
    if str(args.llm_api_key or "").strip():
        llm_cfg["api_key"] = str(args.llm_api_key).strip()
    if str(args.auth_mode or "").strip():
        llm_cfg["auth_mode"] = str(args.auth_mode).strip()

    emb_cfg = build_embeddings_config(
        str(args.embeddings_provider or ""),
        model=_none_if_empty(args.embeddings_model),
        llm_provider=llm_provider,
    )
    if str(args.embeddings_base_url or "").strip():
        emb_cfg["base_url"] = str(args.embeddings_base_url).strip()
    if str(args.embeddings_api_key or "").strip():
        emb_cfg["api_key"] = str(args.embeddings_api_key).strip()
    if str(args.embeddings_auth_mode or "").strip():
        emb_cfg["auth_mode"] = str(args.embeddings_auth_mode).strip()
    dims = int(args.embeddings_dims or 0)
    provider_norm = str(emb_cfg.get("provider") or "").strip().lower()
    if provider_norm == "hashing":
        emb_cfg["dims"] = int(dims) if dims > 0 else int(emb_cfg.get("dims", 256) or 256)
    elif dims > 0 and provider_norm != "none":
        emb_cfg["dimensions"] = int(dims)
        emb_cfg["extra_body"] = {"dimensions": int(dims)}

    store_cfg: Dict[str, Any] = {"provider": "local", "path": str(args.store_path)}
    return AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings=emb_cfg,
            store=store_cfg,
            maintenance_strategy=("llm" if llm_provider != "mock" else "heuristic"),
        )
    )


def build_parser() -> argparse.ArgumentParser:
    """Run build parser."""
    p = argparse.ArgumentParser(
        description="Batch extract skills by looping over each user folder in chat_messages_openai_by_user."
    )
    p.add_argument(
        "--input-root",
        default=env("AUTOSKILL_OFFLINE_INPUT_ROOT", _default_input_root()),
        help="Root folder that contains per-user subfolders with OpenAI-format .json/.jsonl files.",
    )
    p.add_argument(
        "--store-path",
        default=env("AUTOSKILL_STORE_PATH", default_store_path()),
        help="Local SkillBank path.",
    )
    p.add_argument("--hint", default="", help="Optional extraction hint for all users.")
    p.add_argument(
        "--max-messages-per-conversation",
        type=int,
        default=int(env("AUTOSKILL_OFFLINE_MAX_MESSAGES", "0") or 0),
        help="0 means no clipping.",
    )
    p.add_argument(
        "--limit-users",
        type=int,
        default=0,
        help="Debug limit. 0 means all users.",
    )
    p.add_argument(
        "--user-id-contains",
        default="",
        help="Only process user ids containing this substring.",
    )
    p.add_argument(
        "--print-file-progress",
        default=env("AUTOSKILL_OFFLINE_PRINT_FILE_PROGRESS", "0"),
        help="Print per-conversation progress: 1|0.",
    )
    p.add_argument(
        "--report-json",
        default=env("AUTOSKILL_OFFLINE_REPORT_JSON", "data/offline_extract_by_user_report.json"),
        help="Write batch summary report to this JSON file.",
    )

    p.add_argument(
        "--llm-provider",
        default=env("AUTOSKILL_LLM_PROVIDER", pick_default_provider()),
        help="mock|generic|glm|internlm|dashscope|openai|anthropic",
    )
    p.add_argument("--llm-model", default=env("AUTOSKILL_LLM_MODEL", ""))
    p.add_argument("--llm-base-url", default=env("AUTOSKILL_LLM_BASE_URL", ""))
    p.add_argument("--llm-api-key", default=env("AUTOSKILL_LLM_API_KEY", ""))
    p.add_argument("--auth-mode", default=env("AUTOSKILL_LLM_AUTH_MODE", ""))

    p.add_argument(
        "--embeddings-provider",
        default=env("AUTOSKILL_EMBEDDINGS_PROVIDER", env("AUTOSKILL_EMBEDDING_PROVIDER", "")),
        help="hashing|none|openai|generic|dashscope|glm",
    )
    p.add_argument("--embeddings-model", default=env("AUTOSKILL_EMBEDDINGS_MODEL", ""))
    p.add_argument("--embeddings-base-url", default=env("AUTOSKILL_EMBEDDINGS_BASE_URL", ""))
    p.add_argument("--embeddings-api-key", default=env("AUTOSKILL_EMBEDDINGS_API_KEY", ""))
    p.add_argument("--embeddings-auth-mode", default=env("AUTOSKILL_EMBEDDINGS_AUTH_MODE", ""))
    p.add_argument(
        "--embeddings-dims",
        type=int,
        default=int(env("AUTOSKILL_EMBEDDINGS_DIMS", "0") or 0),
        help="Embedding dimensions override.",
    )
    return p


def _to_bool_text(v: Any, default: bool) -> bool:
    """Run to bool text."""
    s = str(v or "").strip().lower()
    if not s:
        return bool(default)
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def main() -> None:
    """Run main."""
    args = build_parser().parse_args()
    root = Path(str(args.input_root)).expanduser().resolve()
    sdk = _build_sdk(args)
    print_file_progress = _to_bool_text(args.print_file_progress, False)

    user_dirs = _find_user_dirs(root)
    contains = str(args.user_id_contains or "").strip()
    if contains:
        user_dirs = [p for p in user_dirs if contains in p.name]
    if int(args.limit_users or 0) > 0:
        user_dirs = user_dirs[: int(args.limit_users)]

    if not user_dirs:
        print(f"No user folders found under: {root}")
        return

    print(f"input_root={root}")
    print(f"users={len(user_dirs)}")

    batch_started = time.time()
    batch_upserted = 0
    user_reports: List[Dict[str, Any]] = []

    for i, user_dir in enumerate(user_dirs, start=1):
        user_id = str(user_dir.name).strip()
        started = time.time()

        def _on_progress(evt: Dict[str, Any]) -> None:
            """Run on progress."""
            if not print_file_progress:
                return
            idx = int(evt.get("index", 0)) + 1
            total = int(evt.get("total", 0))
            fname = str(evt.get("file_name") or "")
            status = str(evt.get("status") or "ok")
            if status == "error":
                print(f"  [{idx}/{total}] {fname} -> ERROR: {evt.get('error')}", flush=True)
                return
            skills = list(evt.get("skills") or [])
            names = [str(x.get("name") or "").strip() for x in skills if str(x.get("name") or "").strip()]
            if names:
                print(f"  [{idx}/{total}] {fname} -> skills: {', '.join(names)}", flush=True)
            else:
                print(f"  [{idx}/{total}] {fname} -> no skills", flush=True)

        try:
            result = extract_from_conversation(
                sdk=sdk,
                user_id=user_id,
                file_path=str(user_dir),
                hint=(str(args.hint).strip() or None),
                continue_on_error=True,
                max_messages_per_conversation=int(args.max_messages_per_conversation or 0),
                metadata={
                    "channel": "offline_extract_from_conversation",
                    "source_group": "chat_messages_openai_by_user",
                    "source_user_id": user_id,
                },
                progress_callback=_on_progress,
            )
            elapsed = round(time.time() - started, 3)
            upserted = int(result.get("upserted_count", 0) or 0)
            processed = int(result.get("processed", 0) or 0)
            failed = int(result.get("failed", 0) or 0)
            total_conversations = int(result.get("total_conversations", 0) or 0)
            batch_upserted += upserted
            print(
                f"[{i}/{len(user_dirs)}] user_id={user_id} "
                f"conversations={total_conversations} processed={processed} failed={failed} "
                f"upserted={upserted} elapsed_s={elapsed}"
            )
            user_reports.append(
                {
                    "user_id": user_id,
                    "status": "ok",
                    "source_dir": str(user_dir),
                    "total_conversations": total_conversations,
                    "processed": processed,
                    "failed": failed,
                    "upserted_count": upserted,
                    "skills": list(result.get("skills") or []),
                    "errors": list(result.get("errors") or []),
                    "elapsed_s": elapsed,
                }
            )
        except Exception as e:
            elapsed = round(time.time() - started, 3)
            print(f"[{i}/{len(user_dirs)}] user_id={user_id} ERROR: {e}")
            user_reports.append(
                {
                    "user_id": user_id,
                    "status": "error",
                    "source_dir": str(user_dir),
                    "error": str(e),
                    "elapsed_s": elapsed,
                }
            )

    batch_elapsed = round(time.time() - batch_started, 3)
    ok_users = sum(1 for r in user_reports if r.get("status") == "ok")
    payload = {
        "input_root": str(root),
        "total_users": len(user_dirs),
        "ok_users": ok_users,
        "error_users": len(user_dirs) - ok_users,
        "batch_upserted_count": int(batch_upserted),
        "elapsed_s": batch_elapsed,
        "users": user_reports,
    }

    report_path = Path(str(args.report_json)).expanduser().resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(
        f"Done. users={len(user_dirs)} ok={ok_users} "
        f"errors={len(user_dirs) - ok_users} upserted={batch_upserted} elapsed_s={batch_elapsed}"
    )
    print(f"report_json={report_path}")


if __name__ == "__main__":
    main()

