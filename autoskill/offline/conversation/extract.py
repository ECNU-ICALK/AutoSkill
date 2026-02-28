"""
Offline conversation extraction from OpenAI-format datasets.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Callable, Dict, List, Optional

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.client import _extract_openai_conversations, _load_openai_data_from_file
from ..prompt_runtime import activate_offline_prompt_runtime


def extract_from_conversation(
    *,
    sdk: AutoSkill,
    user_id: str,
    data: Optional[Any] = None,
    file_path: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
    continue_on_error: bool = True,
    max_messages_per_conversation: int = 0,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Runs offline extraction from archived OpenAI-format conversations.
    """

    units: List[Dict[str, Any]] = []
    abs_input = ""
    if data is not None:
        units = _units_from_openai_data(data, source_file="")
    elif str(file_path or "").strip():
        units, abs_input = _units_from_openai_path(str(file_path))
    else:
        raise ValueError("extract_from_conversation requires data or file_path")
    if not units:
        return {
            "total_conversations": 0,
            "processed": 0,
            "failed": 0,
            "upserted_count": 0,
            "skills": [],
            "errors": [],
            "source_file": abs_input or None,
        }

    user = str(user_id or "").strip() or "u1"
    limit_msgs = max(0, int(max_messages_per_conversation or 0))
    base_md = dict(metadata or {})
    base_md.setdefault("channel", "offline_extract_from_conversation")
    base_md.setdefault("source_type", "conversation")
    if abs_input:
        base_md.setdefault("source_file", abs_input)

    processed = 0
    failed = 0
    errors: List[Dict[str, Any]] = []
    upserted_by_id: Dict[str, Any] = {}

    with activate_offline_prompt_runtime(sdk=sdk, channel="offline_extract_from_conversation"):
        for idx, unit in enumerate(units):
            unit_messages = list(unit.get("messages") or [])
            if not unit_messages:
                failed += 1
                errors.append({"index": idx, "error": "empty openai messages"})
                continue
            window = list(unit_messages[-limit_msgs:]) if limit_msgs > 0 else list(unit_messages)
            user_questions = _collect_user_questions(window)
            full_context = _format_full_conversation(window)
            msg = _build_conversation_message(
                title=str(unit.get("title") or "").strip() or f"conversation_{idx + 1}",
                user_questions=user_questions,
                full_conversation=full_context,
            )
            window = [{"role": "user", "content": msg}]
            if limit_msgs > 0:
                window = list(window[-limit_msgs:])
            if not window:
                failed += 1
                errors.append({"index": idx, "error": "empty conversation after normalization"})
                continue
            md = dict(base_md)
            md["import_index"] = int(idx)
            unit_source_file = str(unit.get("source_file") or "").strip()
            md["conversation_index"] = int(unit.get("conversation_index", 0))
            unit_title = str(unit.get("title") or "").strip() or f"conversation_{idx + 1}"
            file_name = os.path.basename(unit_source_file) if unit_source_file else unit_title
            if unit_source_file:
                md["source_file"] = unit_source_file
            try:
                updated = sdk.ingest(
                    user_id=user,
                    messages=window,
                    events=None,
                    metadata=md,
                    hint=(str(hint).strip() or None),
                )
                processed += 1
                for s in (updated or []):
                    sid = str(getattr(s, "id", "") or "")
                    if sid:
                        upserted_by_id[sid] = s
                if progress_callback is not None:
                    progress_callback(
                        {
                            "index": int(idx),
                            "total": int(len(units)),
                            "file_name": file_name,
                            "file_path": unit_source_file or None,
                            "status": "ok",
                            "skills": _skills_compact_list(updated),
                        }
                    )
            except Exception as e:
                failed += 1
                errors.append({"index": idx, "error": str(e)})
                if progress_callback is not None:
                    progress_callback(
                        {
                            "index": int(idx),
                            "total": int(len(units)),
                            "file_name": file_name,
                            "file_path": unit_source_file or None,
                            "status": "error",
                            "error": str(e),
                            "skills": [],
                        }
                    )
                if not continue_on_error:
                    raise

    return {
        "total_conversations": len(units),
        "processed": processed,
        "failed": failed,
        "upserted_count": len(upserted_by_id),
        "skills": [_skill_to_plain_dict(s) for s in upserted_by_id.values()],
        "errors": errors,
        "source_file": abs_input or None,
    }


def _build_conversation_message(
    *,
    title: str,
    user_questions: str,
    full_conversation: str,
) -> str:
    return (
        "Offline OpenAI-format conversation source.\n"
        f"Title: {title}\n"
        "Use the user questions below as the PRIMARY extraction evidence.\n"
        "Use the full conversation below as SECONDARY context reference.\n"
        "In the full conversation section, assistant/model replies are reference-only and not skill evidence.\n\n"
        "Primary User Questions (main evidence):\n"
        f"{user_questions}\n\n"
        "Full Conversation (context reference):\n"
        f"{full_conversation}"
    )


def _units_from_openai_data(data: Any, *, source_file: str) -> List[Dict[str, Any]]:
    conversations = _extract_openai_conversations(data)
    out: List[Dict[str, Any]] = []
    base = os.path.basename(source_file) if source_file else "inline"
    for i, conv in enumerate(conversations):
        out.append(
            {
                "title": f"{base}#conv_{i + 1}",
                "source_file": source_file,
                "conversation_index": i,
                "messages": list(conv),
            }
        )
    return out


def _units_from_openai_path(path: str) -> tuple[List[Dict[str, Any]], str]:
    abs_path = os.path.abspath(os.path.expanduser(str(path or "").strip()))
    if not abs_path:
        return [], ""
    if os.path.isfile(abs_path):
        data = _load_openai_data_from_file(abs_path)
        return _units_from_openai_data(data, source_file=abs_path), abs_path
    if not os.path.isdir(abs_path):
        raise ValueError(f"path not found: {abs_path}")

    out: List[Dict[str, Any]] = []
    for p in _iter_openai_dataset_files(abs_path):
        try:
            data = _load_openai_data_from_file(p)
        except Exception:
            continue
        out.extend(_units_from_openai_data(data, source_file=p))
    return out, abs_path


def _iter_openai_dataset_files(root: str) -> List[str]:
    files: List[str] = []
    for dirpath, _, names in os.walk(root):
        for name in names:
            low = str(name).lower()
            if low.endswith(".json") or low.endswith(".jsonl"):
                p = os.path.join(dirpath, name)
                if os.path.isfile(p):
                    files.append(p)
    files.sort()
    return files


def _collect_user_questions(messages: List[Dict[str, str]]) -> str:
    parts: List[str] = []
    for m in list(messages or []):
        role = str(m.get("role") or "").strip().lower()
        if role != "user":
            continue
        txt = str(m.get("content") or "").strip()
        if not txt:
            continue
        parts.append(txt)
    if not parts:
        return "(none)"
    return "\n\n".join(parts)


def _format_full_conversation(messages: List[Dict[str, str]]) -> str:
    out: List[str] = []
    for m in list(messages or []):
        role = str(m.get("role") or "").strip().lower() or "user"
        txt = str(m.get("content") or "").strip()
        if not txt:
            continue
        out.append(f"[{role}] {txt}")
    return "\n\n".join(out).strip() or "(empty)"


def _skill_to_plain_dict(skill: Any) -> Dict[str, Any]:
    try:
        examples = []
        for e in list(getattr(skill, "examples", []) or []):
            examples.append(
                {
                    "input": str(getattr(e, "input", "") or ""),
                    "output": (str(getattr(e, "output", "") or "") or None),
                    "notes": (str(getattr(e, "notes", "") or "") or None),
                }
            )
        return {
            "id": str(getattr(skill, "id", "") or ""),
            "name": str(getattr(skill, "name", "") or ""),
            "description": str(getattr(skill, "description", "") or ""),
            "version": str(getattr(skill, "version", "") or ""),
            "triggers": list(getattr(skill, "triggers", []) or []),
            "tags": list(getattr(skill, "tags", []) or []),
            "examples": examples,
        }
    except Exception:
        return {"id": "", "name": "", "description": "", "version": ""}


def _skills_compact_list(skills: Any) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()
    for s in list(skills or []):
        sid = str(getattr(s, "id", "") or "").strip()
        name = str(getattr(s, "name", "") or "").strip()
        key = (sid, name)
        if key in seen:
            continue
        seen.add(key)
        out.append({"id": sid, "name": name})
    return out


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


def _build_sdk_from_args(args: argparse.Namespace) -> AutoSkill:
    llm_cfg = _build_llm_config(args)
    store_cfg: Dict[str, Any] = {"provider": "local"}
    if str(args.store_path or "").strip():
        store_cfg["path"] = str(args.store_path).strip()
    return AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings={"provider": "hashing", "dims": 256},
            store=store_cfg,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract skills from OpenAI-format conversation JSON/JSONL files (or a directory of them)."
    )
    parser.add_argument("--file", required=True, help="Path to an OpenAI-format .json/.jsonl file or directory.")
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
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sdk = _build_sdk_from_args(args)

    def _on_progress(evt: Dict[str, Any]) -> None:
        idx = int(evt.get("index", 0)) + 1
        total = int(evt.get("total", 0))
        fname = str(evt.get("file_name") or "")
        status = str(evt.get("status") or "ok")
        if status == "error":
            err = str(evt.get("error") or "unknown error")
            print(f"[{idx}/{total}] {fname} -> ERROR: {err}", flush=True)
            return
        skills = list(evt.get("skills") or [])
        if not skills:
            print(f"[{idx}/{total}] {fname} -> no skills", flush=True)
            return
        names = [str(x.get("name") or "").strip() for x in skills if str(x.get("name") or "").strip()]
        if not names:
            print(f"[{idx}/{total}] {fname} -> skills: {len(skills)}", flush=True)
            return
        print(f"[{idx}/{total}] {fname} -> skills: {', '.join(names)}", flush=True)

    result = extract_from_conversation(
        sdk=sdk,
        user_id=str(args.user_id).strip() or "u1",
        file_path=str(args.file),
        hint=(str(args.hint).strip() or None),
        continue_on_error=True,
        max_messages_per_conversation=int(args.max_messages_per_conversation or 0),
        metadata={"channel": "offline_extract_from_conversation"},
        progress_callback=_on_progress,
    )

    print("Offline conversation extraction completed.")
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
