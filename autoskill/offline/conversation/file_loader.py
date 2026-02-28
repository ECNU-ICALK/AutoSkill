"""
OpenAI-format conversation loader for offline conversation extraction.

This module is source-isolated under `offline/conversation` so conversation
pipelines can evolve independently from document/trajectory pipelines.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple


def load_openai_units(*, data: Optional[Any] = None, file_path: str = "") -> Tuple[List[Dict[str, Any]], str]:
    """
    Loads OpenAI-format conversation units from in-memory data or file path.

    Returns:
    - units: [{title, source_file, conversation_index, messages}]
    - abs_input_path: absolute input path when loading from file/dir, else ""
    """

    if data is not None:
        return _units_from_openai_data(data, source_file=""), ""
    if str(file_path or "").strip():
        return _units_from_openai_path(str(file_path))
    raise ValueError("load_openai_units requires data or file_path")


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


def _units_from_openai_path(path: str) -> Tuple[List[Dict[str, Any]], str]:
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


def _load_openai_data_from_file(path: str) -> Any:
    if not os.path.isfile(path):
        raise ValueError(f"file not found: {path}")
    if str(path).lower().endswith(".jsonl"):
        rows: List[Any] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = str(line or "").strip()
                if not s:
                    continue
                try:
                    rows.append(json.loads(s))
                except Exception:
                    continue
        return rows
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_openai_conversations(data: Any) -> List[List[Dict[str, str]]]:
    out: List[List[Dict[str, str]]] = []

    def collect(obj: Any) -> None:
        if isinstance(obj, list):
            if _looks_like_messages(obj):
                msgs = _normalize_openai_messages(obj)
                if msgs:
                    out.append(msgs)
                return
            for item in obj:
                collect(item)
            return

        if not isinstance(obj, dict):
            return

        for key in ("messages", "conversation", "dialogue", "history", "chat_history"):
            v = obj.get(key)
            if _looks_like_messages(v):
                msgs = _normalize_openai_messages(v)
                if msgs:
                    msgs = _attach_response_message(messages=msgs, record=obj)
                    out.append(msgs)
                return

        for key in ("body", "request", "input", "payload"):
            v = obj.get(key)
            if isinstance(v, dict) and _looks_like_messages(v.get("messages")):
                msgs = _normalize_openai_messages(v.get("messages"))
                if msgs:
                    msgs = _attach_response_message(messages=msgs, record=obj)
                    out.append(msgs)
                return

        for key in ("data", "items", "records", "conversations", "dialogues", "samples"):
            v = obj.get(key)
            if isinstance(v, (list, dict)):
                collect(v)

    collect(data)
    return out


def _looks_like_messages(raw: Any) -> bool:
    if not isinstance(raw, list) or not raw:
        return False
    if not all(isinstance(x, dict) for x in raw):
        return False
    has_message_shape = False
    for x in raw:
        if "role" in x:
            has_message_shape = True
            break
        if "content" in x or "text" in x:
            has_message_shape = True
            break
    return has_message_shape


def _normalize_openai_messages(raw: Any) -> List[Dict[str, str]]:
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
