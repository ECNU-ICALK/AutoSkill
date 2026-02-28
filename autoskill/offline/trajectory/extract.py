"""
Offline agentic trajectory extraction.

This module ingests archived agent execution traces and extracts reusable skills.
"""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict, List, Optional

from autoskill import AutoSkill, AutoSkillConfig
from .file_loader import data_to_text_unit, load_file_units
from .prompt_runtime import activate_offline_prompt_runtime


def extract_from_agentic_trajectory(
    *,
    sdk: AutoSkill,
    user_id: str,
    data: Optional[Any] = None,
    file_path: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
    continue_on_error: bool = True,
    include_tool_events: bool = True,
    success_only: bool = True,
    max_messages_per_record: int = 0,
    max_events_per_record: int = 0,
) -> Dict[str, Any]:
    """
    Runs offline extraction from agentic trajectories.
    """

    source = data
    abs_input = ""
    if source is None and str(file_path or "").strip():
        units, abs_input = load_file_units(str(file_path))
        source = {"records": [_record_from_unit(u) for u in units]}
    elif source is not None:
        source = {"records": [_record_from_unit(data_to_text_unit(source, title="inline_trajectory"))]}
    if source is None:
        raise ValueError("extract_from_agentic_trajectory requires data or file_path")

    records = _collect_records(source)
    if not records:
        return {
            "total_records": 0,
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "upserted_count": 0,
            "skills": [],
            "errors": [],
            "source_file": abs_input or None,
        }

    base_md = dict(metadata or {})
    base_md.setdefault("channel", "offline_extract_from_agentic_trajectory")
    base_md.setdefault("source_type", "agentic_trajectory")
    if abs_input:
        base_md.setdefault("source_file", abs_input)

    processed = 0
    failed = 0
    skipped = 0
    errors: List[Dict[str, Any]] = []
    upserted_by_id: Dict[str, Any] = {}
    msg_limit = max(0, int(max_messages_per_record or 0))
    ev_limit = max(0, int(max_events_per_record or 0))

    with activate_offline_prompt_runtime(sdk=sdk, channel="offline_extract_from_agentic_trajectory"):
        for idx, record in enumerate(records):
            ok = _parse_success(record)
            if success_only and not ok:
                skipped += 1
                continue

            messages = _messages_from_record(record)
            events = _events_from_record(record) if include_tool_events else []
            if msg_limit > 0 and messages:
                messages = list(messages[-msg_limit:])
            if ev_limit > 0 and events:
                events = list(events[-ev_limit:])
            if not messages and not events:
                failed += 1
                errors.append({"index": idx, "error": "no usable messages/events"})
                continue

            md = dict(base_md)
            md["trajectory_index"] = int(idx)
            md["trajectory_success"] = bool(ok)
            md["trajectory_has_events"] = bool(events)
            source_file = str(record.get("source_file") or "").strip()
            if source_file:
                md["source_file"] = source_file

            try:
                updated = sdk.ingest(
                    user_id=str(user_id or "").strip() or "u1",
                    messages=(messages or None),
                    events=(events or None),
                    metadata=md,
                    hint=(str(hint).strip() if hint and str(hint).strip() else None),
                )
                processed += 1
                for s in (updated or []):
                    sid = str(getattr(s, "id", "") or "")
                    if sid:
                        upserted_by_id[sid] = s
            except Exception as e:
                failed += 1
                errors.append({"index": idx, "error": str(e)})
                if not continue_on_error:
                    raise

    return {
        "total_records": len(records),
        "processed": processed,
        "failed": failed,
        "skipped": skipped,
        "upserted_count": len(upserted_by_id),
        "skills": [_skill_to_plain_dict(s) for s in upserted_by_id.values()],
        "errors": errors,
        "source_file": abs_input or None,
    }


def _record_from_unit(unit: Dict[str, str]) -> Dict[str, Any]:
    title = str(unit.get("title") or "").strip() or "trajectory"
    text = str(unit.get("text") or "").strip()
    source_file = str(unit.get("source_file") or "").strip()
    msg = (
        "Offline agentic trajectory source.\n"
        f"Title: {title}\n"
        "Treat this content as one complete trajectory/workflow context.\n"
        "Trajectory content:\n"
        f"{text}"
    )
    out: Dict[str, Any] = {
        "success": True,
        "messages": [{"role": "user", "content": msg}],
    }
    if source_file:
        out["source_file"] = source_file
    return out


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


def _collect_records(data: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def collect(obj: Any) -> None:
        if obj is None:
            return
        if isinstance(obj, list):
            for item in obj:
                collect(item)
            return
        if not isinstance(obj, dict):
            return

        # Direct trajectory-like record.
        if _looks_like_trajectory_record(obj):
            out.append(obj)
            return

        # Wrapper shapes.
        for key in ("data", "items", "records", "trajectories", "runs", "samples"):
            v = obj.get(key)
            if isinstance(v, (list, dict)):
                collect(v)

    collect(data)
    return out


def _looks_like_trajectory_record(obj: Dict[str, Any]) -> bool:
    if any(k in obj for k in ("messages", "events", "trace", "trajectory", "steps", "tool_calls", "actions")):
        return True
    if any(k in obj for k in ("task", "goal", "instruction", "query", "prompt", "final_answer", "output", "response")):
        return True
    return False


def _messages_from_record(record: Dict[str, Any]) -> List[Dict[str, str]]:
    # 1) Prefer canonical messages-like fields.
    for key in ("messages", "conversation", "dialogue", "history", "chat_history", "finalMessages"):
        raw = record.get(key)
        msgs = _normalize_messages(raw)
        if msgs:
            return msgs

    # 2) Request-log style.
    for key in ("body", "request", "input", "payload"):
        obj = record.get(key)
        if not isinstance(obj, dict):
            continue
        msgs = _normalize_messages(obj.get("messages"))
        if msgs:
            return _attach_response_message(messages=msgs, record=record)

    # 3) Build from sparse fields.
    out: List[Dict[str, str]] = []
    user_text = _first_non_empty_text(
        record,
        keys=("query", "task", "goal", "instruction", "prompt", "input", "user_query"),
    )
    if user_text:
        out.append({"role": "user", "content": user_text})
    assistant_text = _first_non_empty_text(
        record,
        keys=("final_answer", "output", "response", "assistant", "result_text"),
    )
    if assistant_text:
        out.append({"role": "assistant", "content": assistant_text})

    feedback = _first_non_empty_text(record, keys=("user_feedback", "feedback", "revision_request"))
    if feedback:
        out.append({"role": "user", "content": feedback})
    return out


def _attach_response_message(*, messages: List[Dict[str, str]], record: Dict[str, Any]) -> List[Dict[str, str]]:
    response = record.get("response")
    if not isinstance(response, dict):
        return messages
    assistant_text = ""
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] if isinstance(choices[0], dict) else {}
        msg = first.get("message") if isinstance(first.get("message"), dict) else {}
        assistant_text = _content_to_text(msg.get("content")).strip()
    if not assistant_text:
        assistant_text = _content_to_text(response.get("output_text")).strip()
    if not assistant_text:
        return messages
    if messages and messages[-1].get("role") == "assistant" and messages[-1].get("content", "").strip():
        return messages
    out = list(messages)
    out.append({"role": "assistant", "content": assistant_text})
    return out


def _normalize_messages(raw: Any) -> List[Dict[str, str]]:
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower() or "user"
        if role not in {"system", "user", "assistant", "tool"}:
            role = "user"
        content = _content_to_text(item.get("content")).strip()
        if not content:
            continue
        out.append({"role": role, "content": content})
    return out


def _events_from_record(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for key in ("events", "trace", "trajectory", "steps", "actions", "tool_calls", "tools"):
        raw = record.get(key)
        if isinstance(raw, dict):
            out.append({"type": key, "data": raw})
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    e = dict(item)
                    e.setdefault("event_type", key)
                    out.append(e)
                elif item is not None:
                    out.append({"event_type": key, "text": str(item)})

    env = record.get("environment")
    if isinstance(env, dict) and env:
        out.append({"event_type": "environment", "data": env})
    return out


def _parse_success(record: Dict[str, Any]) -> bool:
    for key in ("success", "task_success", "objective_met"):
        if key in record:
            return bool(record.get(key))
    status = str(record.get("status") or "").strip().lower()
    if status in {"success", "succeeded", "completed", "ok", "done"}:
        return True
    if status in {"failed", "error", "timeout", "cancelled", "canceled"}:
        return False
    nested = record.get("result")
    if isinstance(nested, dict) and "success" in nested:
        return bool(nested.get("success"))
    return True


def _first_non_empty_text(obj: Dict[str, Any], *, keys: tuple[str, ...]) -> str:
    for key in keys:
        text = _content_to_text(obj.get(key)).strip()
        if text:
            return text
    return ""


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if "text" in item:
                    parts.append(str(item.get("text") or ""))
                elif "content" in item:
                    parts.append(str(item.get("content") or ""))
        return "".join(parts)
    if isinstance(content, dict):
        if "text" in content:
            return str(content.get("text") or "")
        if "content" in content:
            return str(content.get("content") or "")
    return str(content)


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


def _parse_bool_text(v: Any, default: bool) -> bool:
    if v is None:
        return bool(default)
    s = str(v).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract skills from offline files/directories as trajectories.")
    parser.add_argument("--file", required=True, help="Path to a file or directory.")
    parser.add_argument("--user-id", default="u1", help="Target user id.")
    parser.add_argument("--hint", default="", help="Optional extraction hint.")
    parser.add_argument("--include-tool-events", default="1", help="1|0")
    parser.add_argument("--success-only", default="1", help="1|0")
    parser.add_argument("--max-messages-per-record", type=int, default=0, help="0 means no clipping.")
    parser.add_argument("--max-events-per-record", type=int, default=0, help="0 means no clipping.")
    parser.add_argument(
        "--llm-provider",
        default=_env("AUTOSKILL_LLM_PROVIDER", "mock"),
        help="mock|generic|glm|internlm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=_env("AUTOSKILL_LLM_MODEL", ""))
    parser.add_argument("--llm-base-url", default=_env("AUTOSKILL_LLM_BASE_URL", ""))
    parser.add_argument("--llm-api-key", default=_env("AUTOSKILL_LLM_API_KEY", ""))
    parser.add_argument("--auth-mode", default=_env("AUTOSKILL_LLM_AUTH_MODE", ""))
    parser.add_argument("--store-path", default=_env("AUTOSKILL_STORE_PATH", ""))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sdk = _build_sdk_from_args(args)
    result = extract_from_agentic_trajectory(
        sdk=sdk,
        user_id=str(args.user_id).strip() or "u1",
        file_path=str(args.file or ""),
        hint=(str(args.hint).strip() or None),
        include_tool_events=_parse_bool_text(args.include_tool_events, True),
        success_only=_parse_bool_text(args.success_only, True),
        max_messages_per_record=int(args.max_messages_per_record or 0),
        max_events_per_record=int(args.max_events_per_record or 0),
        continue_on_error=True,
        metadata={"channel": "offline_extract_from_agentic_trajectory"},
    )
    print("Offline agentic trajectory extraction completed.")
    print(
        f"records={result.get('total_records', 0)} "
        f"processed={result.get('processed', 0)} "
        f"skipped={result.get('skipped', 0)} "
        f"failed={result.get('failed', 0)} "
        f"upserted={result.get('upserted_count', 0)}"
    )
    for i, s in enumerate(list(result.get("skills") or []), start=1):
        print(f"{i}. {s.get('name', '')} ({s.get('version', '')})")
    errors = list(result.get("errors") or [])
    if errors:
        print("Errors:")
        for e in errors[:20]:
            print(f"- #{e.get('index')}: {e.get('error')}")


if __name__ == "__main__":
    main()
