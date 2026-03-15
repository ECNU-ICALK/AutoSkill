"""
OpenClaw main-turn chat proxy and sampler.

This module keeps all OpenClaw-specific main-turn sampling logic inside the
plugin directory so the core AutoSkill runtime does not need architectural
changes.
"""

from __future__ import annotations

import hashlib
import http.client
import json
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Tuple
from urllib.parse import urljoin, urlparse

_ALLOWED_MESSAGE_ROLES = {"system", "user", "assistant", "tool", "environment"}
_HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def _log(message: str) -> None:
    """Run log."""
    print(f"[openclaw-main-turn-proxy] {message}", flush=True)


def _bool_from_any(value: Any, default: bool = False) -> bool:
    """Run bool from any."""
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if not text:
        return bool(default)
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _safe_int(value: Any, default: int = 0) -> int:
    """Run safe int."""
    try:
        return int(value)
    except Exception:
        return int(default)


def _content_to_text(content: Any) -> str:
    """Run content to text."""
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
                elif "output_text" in item:
                    parts.append(str(item.get("output_text") or ""))
        return "".join(parts)
    if isinstance(content, dict):
        if "text" in content:
            return str(content.get("text") or "")
        if "content" in content:
            return str(content.get("content") or "")
        if "output_text" in content:
            return str(content.get("output_text") or "")
    return str(content)


def _message_role(role: Any) -> str:
    """Run message role."""
    text = str(role or "").strip().lower()
    if text in _ALLOWED_MESSAGE_ROLES:
        return text
    return "user"


def _compact_json(value: Any, *, max_chars: int = 8000) -> str:
    """Run compact json."""
    try:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    except Exception:
        text = str(value)
    text = str(text or "").strip()
    if max_chars > 0 and len(text) > max_chars:
        return text[:max_chars]
    return text


def _assistant_message_content(message: Mapping[str, Any]) -> str:
    """Run assistant message content."""
    content = _content_to_text(message.get("content")).strip()
    if content:
        return content
    payload: Dict[str, Any] = {}
    for key in ("tool_calls", "function_call", "refusal", "audio", "annotations"):
        if key in message and message.get(key) not in (None, "", [], {}):
            payload[key] = message.get(key)
    if payload:
        return _compact_json(payload)
    return ""


def _normalize_message(item: Any) -> Optional[Dict[str, Any]]:
    """Run normalize message."""
    if not isinstance(item, dict):
        return None
    role = _message_role(item.get("role"))
    content = ""
    if role in {"tool", "environment"}:
        content = _content_to_text(
            item.get("content")
            if item.get("content") is not None
            else (
                item.get("result")
                if item.get("result") is not None
                else (item.get("output") if item.get("output") is not None else item.get("observation"))
            )
        ).strip()
    elif role == "assistant":
        content = _assistant_message_content(item).strip()
    else:
        content = _content_to_text(item.get("content")).strip()
    if not content:
        return None
    out: Dict[str, Any] = {"role": role, "content": content}
    name = str(item.get("name") or "").strip()
    if name:
        out["name"] = name
    tool_call_id = str(item.get("tool_call_id") or "").strip()
    if tool_call_id:
        out["tool_call_id"] = tool_call_id
    return out


def normalize_openclaw_messages(raw: Any) -> List[Dict[str, Any]]:
    """Normalize OpenClaw/OpenAI-compatible messages while preserving `environment`."""
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in raw:
        msg = _normalize_message(item)
        if msg is not None:
            out.append(msg)
    return out


def infer_turn_type_from_messages(messages: List[Dict[str, Any]]) -> str:
    """Best-effort turn type inference when OpenClaw does not forward explicit metadata."""
    has_user = False
    has_assistant = False
    has_tool_or_env = False
    for item in list(messages or []):
        role = str((item or {}).get("role") or "").strip().lower()
        if role == "user":
            has_user = True
            continue
        if role == "assistant":
            has_assistant = True
            continue
        if role in {"tool", "environment"}:
            has_tool_or_env = True
    if has_user:
        return "main"
    if has_assistant and not has_tool_or_env:
        return "main"
    if has_tool_or_env and not has_user and not has_assistant:
        return "side"
    return ""


def _header_value(headers: Any, key: str) -> str:
    """Run header value."""
    if headers is None:
        return ""
    try:
        value = headers.get(key)
    except Exception:
        value = None
    return str(value or "").strip()


def _body_value(body: Dict[str, Any], *paths: Any) -> Any:
    """Run body value."""
    for path in paths:
        if isinstance(path, str):
            if path in body and body.get(path) not in (None, ""):
                return body.get(path)
            continue
        cur: Any = body
        ok = True
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                ok = False
                break
            cur = cur.get(key)
        if ok and cur not in (None, ""):
            return cur
    return None


def _extract_last_next_state(messages: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], int]:
    """Run extract last next state."""
    for idx in range(len(messages) - 1, -1, -1):
        role = str((messages[idx] or {}).get("role") or "").strip().lower()
        if role in {"user", "tool", "environment"}:
            return dict(messages[idx]), idx
    return None, -1


def _extract_fallback_assistant(messages: List[Dict[str, Any]], *, before_index: int) -> Optional[Dict[str, Any]]:
    """Run extract fallback assistant."""
    if before_index < 0:
        before_index = len(messages)
    for idx in range(min(before_index - 1, len(messages) - 1), -1, -1):
        role = str((messages[idx] or {}).get("role") or "").strip().lower()
        if role != "assistant":
            continue
        content = str((messages[idx] or {}).get("content") or "").strip()
        if content:
            return dict(messages[idx])
    return None


def _normalize_target_base_url(base_url: str) -> str:
    """Run normalize target base url."""
    text = str(base_url or "").strip().rstrip("/")
    if not text:
        return ""
    parsed = urlparse(text)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("AUTOSKILL_OPENCLAW_PROXY_TARGET_BASE_URL must be an absolute URL")
    if parsed.path.endswith("/v1"):
        return text
    if not parsed.path or parsed.path == "/":
        return text + "/v1"
    return text


def build_target_chat_url(base_url: str) -> str:
    """Run build target chat url."""
    base = _normalize_target_base_url(base_url)
    if not base:
        return ""
    return urljoin(base + "/", "chat/completions")


def _copy_headers_for_upstream(headers: Any, *, target_api_key: Optional[str]) -> Dict[str, str]:
    """Run copy headers for upstream."""
    out: Dict[str, str] = {}
    items: List[Tuple[str, str]] = []
    try:
        items = list(headers.items())  # type: ignore[attr-defined]
    except Exception:
        items = []
    for key, value in items:
        k = str(key or "").strip()
        if not k:
            continue
        if k.lower() in _HOP_BY_HOP_HEADERS:
            continue
        if k.lower() == "authorization" and target_api_key:
            continue
        out[k] = str(value or "")
    if target_api_key:
        out["Authorization"] = f"Bearer {target_api_key}"
    return out


def _copy_headers_to_client(
    handler: BaseHTTPRequestHandler,
    headers: List[Tuple[str, str]],
    *,
    content_length: Optional[int],
) -> None:
    """Run copy headers to client."""
    for key, value in headers:
        k = str(key or "").strip()
        if not k:
            continue
        lk = k.lower()
        if lk in _HOP_BY_HOP_HEADERS:
            continue
        if lk == "content-length":
            # Always rebuild Content-Length explicitly for non-stream responses.
            # For stream/chunked responses we must not emit a synthetic zero length.
            continue
        handler.send_header(k, str(value or ""))
    if content_length is not None:
        handler.send_header("Content-Length", str(int(content_length)))


@dataclass
class OpenClawMainTurnProxyConfig:
    enabled: bool = False
    target_base_url: str = ""
    target_api_key: Optional[str] = None
    ingest_window: int = 6
    connect_timeout_s: float = 20.0
    read_timeout_s: float = 600.0
    agent_end_extract_enabled: bool = True
    dedupe_max_entries: int = 4096

    def normalize(self) -> "OpenClawMainTurnProxyConfig":
        """Run normalize."""
        self.enabled = bool(self.enabled)
        self.target_base_url = _normalize_target_base_url(self.target_base_url) if self.target_base_url else ""
        key = str(self.target_api_key or "").strip()
        self.target_api_key = key or None
        self.ingest_window = max(3, int(self.ingest_window or 6))
        self.connect_timeout_s = max(1.0, float(self.connect_timeout_s or 20.0))
        self.read_timeout_s = max(5.0, float(self.read_timeout_s or 600.0))
        self.agent_end_extract_enabled = bool(self.agent_end_extract_enabled)
        self.dedupe_max_entries = max(128, int(self.dedupe_max_entries or 4096))
        return self

    @property
    def chat_endpoint_enabled(self) -> bool:
        """Run chat endpoint enabled."""
        return bool(self.target_base_url)

    @property
    def target_chat_url(self) -> str:
        """Run target chat url."""
        return build_target_chat_url(self.target_base_url)


@dataclass
class AssistantCapture:
    role: str
    content: str
    raw_message: Optional[Dict[str, Any]] = None

    def as_message(self) -> Optional[Dict[str, Any]]:
        """Run as message."""
        text = str(self.content or "").strip()
        if not text and not self.raw_message:
            return None
        return {"role": "assistant", "content": text or _compact_json(self.raw_message or {})}


@dataclass
class OpenClawTurnContext:
    request_id: str
    session_id: str
    user_id: str
    turn_type: str
    session_done: bool
    turn_index: int
    request_seq: int
    stream: bool
    messages: List[Dict[str, Any]]
    prompt_messages_tail: List[Dict[str, Any]]
    next_state: Optional[Dict[str, Any]]
    next_state_index: int
    retrieval_reference: Optional[Dict[str, Any]]
    retrieval_metadata: Optional[Dict[str, Any]]
    source_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PendingMainTurn:
    session_id: str
    user_id: str
    turn_index: int
    request_seq: int
    prompt_messages_tail: List[Dict[str, Any]]
    assistant_message: Optional[Dict[str, Any]]
    retrieval_reference: Optional[Dict[str, Any]]
    retrieval_metadata: Optional[Dict[str, Any]]
    source_metadata: Dict[str, Any]
    timestamp_ms: int


@dataclass
class MainTurnFlushResult:
    scheduled_job_id: Optional[str] = None
    status: str = "skipped"
    reason: str = ""
    dedupe_key: str = ""


@dataclass
class MainTurnSample:
    user_id: str
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    dedupe_key: str
    retrieval_reference: Optional[Dict[str, Any]]


def extract_retrieval_metadata(body: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Extract compact retrieval context from body when available."""
    retrieval = None
    autoskill_obj = body.get("autoskill")
    if isinstance(autoskill_obj, dict) and isinstance(autoskill_obj.get("retrieval"), dict):
        retrieval = dict(autoskill_obj.get("retrieval") or {})
    elif isinstance(body.get("retrieval"), dict):
        retrieval = dict(body.get("retrieval") or {})

    selected_raw = None
    if isinstance(body.get("selected_skills"), list):
        selected_raw = list(body.get("selected_skills") or [])
    elif isinstance(retrieval, dict) and isinstance(retrieval.get("selected_skills"), list):
        selected_raw = list(retrieval.get("selected_skills") or [])

    hits_raw = list(retrieval.get("hits") or []) if isinstance(retrieval, dict) else []
    selected_skills: List[Dict[str, Any]] = []
    for item in list(selected_raw or [])[:4]:
        if not isinstance(item, dict):
            continue
        selected_skills.append(
            {
                "id": str(item.get("id") or "").strip(),
                "name": str(item.get("name") or "").strip(),
                "description": str(item.get("description") or "").strip(),
            }
        )
    context_text = ""
    if isinstance(retrieval, dict):
        context_text = _content_to_text(retrieval.get("context_message") or retrieval.get("context")).strip()
    if not context_text:
        context_text = _content_to_text(body.get("context_message") or body.get("context")).strip()

    metadata: Dict[str, Any] = {}
    if isinstance(retrieval, dict):
        if retrieval.get("selected_for_context_ids"):
            metadata["selected_for_context_ids"] = [
                str(x).strip() for x in list(retrieval.get("selected_for_context_ids") or [])[:8] if str(x).strip()
            ]
        if retrieval.get("selected_for_use_ids"):
            metadata["selected_for_use_ids"] = [
                str(x).strip() for x in list(retrieval.get("selected_for_use_ids") or [])[:8] if str(x).strip()
            ]
        if retrieval.get("context_injected") is not None:
            metadata["context_injected"] = bool(retrieval.get("context_injected"))
        if retrieval.get("query"):
            metadata["query"] = str(retrieval.get("query") or "").strip()
        elif retrieval.get("original_query"):
            metadata["query"] = str(retrieval.get("original_query") or "").strip()
    if selected_skills:
        metadata["selected_skills"] = selected_skills
    if context_text:
        metadata["context_excerpt"] = context_text[:1200]

    reference: Optional[Dict[str, Any]] = None
    top = None
    if selected_raw and isinstance(selected_raw[0], dict):
        top = selected_raw[0]
    elif hits_raw and isinstance(hits_raw[0], dict):
        top = hits_raw[0]
    if isinstance(top, dict):
        skill = top.get("skill") if isinstance(top.get("skill"), dict) else top
        reference = {
            "id": str(skill.get("id") or "").strip(),
            "name": str(skill.get("name") or "").strip(),
            "description": str(skill.get("description") or "").strip(),
            "triggers": [
                str(x).strip() for x in list(skill.get("triggers") or [])[:12] if str(x).strip()
            ],
            "resource_paths": [
                str(x).strip() for x in list(skill.get("resource_paths") or [])[:12] if str(x).strip()
            ],
            "score": float(top.get("score") or 0.0),
        }
        if not any(reference.values()):
            reference = None

    if not metadata:
        metadata = None
    return reference, metadata


def parse_turn_context(
    *,
    body: Dict[str, Any],
    headers: Any,
    default_user_id: str,
    ingest_window: int,
) -> OpenClawTurnContext:
    """Parse session/turn metadata from OpenClaw proxy request."""
    session_id = _header_value(headers, "X-Session-Id") or str(
        _body_value(
            body,
            "session_id",
            "sessionId",
            ("metadata", "session_id"),
            ("metadata", "sessionId"),
            ("openclaw", "session_id"),
            ("openclaw", "sessionId"),
        )
        or ""
    ).strip()
    turn_type = _header_value(headers, "X-Turn-Type") or str(
        _body_value(body, "turn_type", "turnType", ("metadata", "turn_type"), ("metadata", "turnType")) or ""
    ).strip().lower()
    session_done = _bool_from_any(
        _header_value(headers, "X-Session-Done")
        or _body_value(
            body,
            "session_done",
            "sessionDone",
            "done",
            ("metadata", "session_done"),
            ("metadata", "sessionDone"),
        ),
        False,
    )
    turn_index = _safe_int(
        _header_value(headers, "X-Turn-Index")
        or _body_value(
            body,
            "turn_index",
            "turnIndex",
            "request_seq",
            "requestSeq",
            ("metadata", "turn_index"),
            ("metadata", "request_seq"),
        ),
        0,
    )
    request_seq = _safe_int(_header_value(headers, "X-Request-Seq") or _body_value(body, "request_seq", "requestSeq"), 0)
    messages = normalize_openclaw_messages(body.get("messages"))
    if not turn_type:
        turn_type = infer_turn_type_from_messages(messages)
    next_state, next_state_index = _extract_last_next_state(messages)
    reference, retrieval_metadata = extract_retrieval_metadata(body)
    user_id = (
        _header_value(headers, "X-User-Id")
        or str(_body_value(body, "user", "user_id", "userId", ("metadata", "user_id")) or "").strip()
        or str(default_user_id or "").strip()
    )
    request_id = _header_value(headers, "X-Request-Id") or uuid.uuid4().hex
    prompt_tail_len = max(1, int(ingest_window) - 2)
    prompt_messages_tail = list(messages[-prompt_tail_len:]) if messages else []
    source_metadata = {
        "request_id": request_id,
        "stream": _bool_from_any(body.get("stream"), False),
        "model": str(body.get("model") or "").strip(),
    }
    return OpenClawTurnContext(
        request_id=request_id,
        session_id=session_id,
        user_id=user_id,
        turn_type=turn_type,
        session_done=session_done,
        turn_index=turn_index,
        request_seq=request_seq,
        stream=_bool_from_any(body.get("stream"), False),
        messages=messages,
        prompt_messages_tail=prompt_messages_tail,
        next_state=next_state,
        next_state_index=next_state_index,
        retrieval_reference=reference,
        retrieval_metadata=retrieval_metadata,
        source_metadata=source_metadata,
    )


def assistant_capture_from_chat_payload(payload: Any) -> Optional[AssistantCapture]:
    """Best-effort assistant capture from non-stream chat completion payload."""
    if not isinstance(payload, dict):
        return None
    choices = payload.get("choices")
    if not isinstance(choices, list):
        return None
    for choice in choices:
        if not isinstance(choice, dict):
            continue
        message = choice.get("message")
        if isinstance(message, dict):
            content = _assistant_message_content(message).strip()
            if content or message:
                return AssistantCapture(role="assistant", content=content, raw_message=dict(message))
        delta = choice.get("delta")
        if isinstance(delta, dict):
            content = _content_to_text(delta.get("content")).strip()
            if content:
                return AssistantCapture(role="assistant", content=content, raw_message=dict(delta))
    return None


class StreamAssistantAccumulator:
    """Incrementally parses standard OpenAI-compatible SSE chunks."""

    def __init__(self) -> None:
        """Run init."""
        self._buffer = ""
        self._content_parts: List[str] = []
        self._tool_call_chunks: List[Any] = []
        self._last_message: Optional[Dict[str, Any]] = None

    def feed(self, chunk: bytes) -> None:
        """Feed SSE bytes into the accumulator."""
        if not chunk:
            return
        self._buffer += chunk.decode("utf-8", errors="ignore")
        while "\n\n" in self._buffer:
            event, self._buffer = self._buffer.split("\n\n", 1)
            self._consume_event(event)

    def _consume_event(self, raw_event: str) -> None:
        """Run consume event."""
        data_lines: List[str] = []
        for line in str(raw_event or "").splitlines():
            if not line.startswith("data:"):
                continue
            data_lines.append(line[5:].strip())
        if not data_lines:
            return
        payload = "\n".join(data_lines).strip()
        if not payload or payload == "[DONE]":
            return
        try:
            obj = json.loads(payload)
        except Exception:
            return
        if not isinstance(obj, dict):
            return
        choices = obj.get("choices")
        if not isinstance(choices, list):
            return
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if isinstance(message, dict):
                self._last_message = dict(message)
                content = _assistant_message_content(message)
                if str(content or "").strip():
                    self._content_parts = [content]
            delta = choice.get("delta")
            if not isinstance(delta, dict):
                continue
            content = _content_to_text(delta.get("content"))
            if str(content or "").strip():
                self._content_parts.append(content)
            if delta.get("tool_calls") not in (None, "", [], {}):
                self._tool_call_chunks.append(delta.get("tool_calls"))

    def finish(self) -> Optional[AssistantCapture]:
        """Run finish."""
        content = "".join(self._content_parts).strip()
        raw = dict(self._last_message) if isinstance(self._last_message, dict) else None
        if not content and self._tool_call_chunks:
            content = _compact_json({"tool_calls": self._tool_call_chunks})
            if raw is None:
                raw = {"tool_calls": list(self._tool_call_chunks)}
        if not content and raw is None:
            return None
        return AssistantCapture(role="assistant", content=content, raw_message=raw)


class OpenClawMainTurnStateManager:
    """Per-session pending main-turn state machine."""

    def __init__(
        self,
        *,
        config: OpenClawMainTurnProxyConfig,
        schedule_extraction: Callable[[MainTurnSample], Optional[str]],
    ) -> None:
        """Run init."""
        self.config = config.normalize()
        self._schedule_extraction = schedule_extraction
        self._state_lock = threading.Lock()
        self._session_locks: Dict[str, threading.Lock] = {}
        self._seq_by_session: Dict[str, int] = {}
        self._pending_by_session: Dict[str, PendingMainTurn] = {}
        self._seen_dedupe: Dict[str, int] = {}

    @contextmanager
    def session_guard(self, session_id: str) -> Iterator[None]:
        """Serialize same-session requests without blocking other sessions."""
        sid = str(session_id or "").strip()
        if not sid:
            yield
            return
        with self._state_lock:
            lock = self._session_locks.get(sid)
            if lock is None:
                lock = threading.Lock()
                self._session_locks[sid] = lock
        lock.acquire()
        try:
            yield
        finally:
            lock.release()

    def prepare_request(self, ctx: OpenClawTurnContext) -> MainTurnFlushResult:
        """Flush previous pending main turn when next_state becomes available."""
        if not self.config.enabled:
            _log("request received but main-turn extraction is disabled; proxy will only forward")
            return MainTurnFlushResult(status="disabled", reason="main_turn_extract_disabled")
        if not ctx.session_id:
            _log("request received without session_id; skip sampling")
            return MainTurnFlushResult(status="skipped", reason="missing_session_id")

        if ctx.turn_index <= 0 or ctx.request_seq <= 0:
            seq = self._next_sequence_locked(ctx.session_id)
            if ctx.turn_index <= 0:
                ctx.turn_index = seq
            if ctx.request_seq <= 0:
                ctx.request_seq = seq

        _log(
            "request received "
            f"session={ctx.session_id} turn_type={ctx.turn_type or '<empty>'} "
            f"session_done={int(ctx.session_done)} turn_index={ctx.turn_index}"
        )

        pending = self._pending_by_session.get(ctx.session_id)
        if pending is None:
            if ctx.turn_type != "main":
                _log(f"side skipped session={ctx.session_id} reason=no_pending_main")
            return MainTurnFlushResult(status="skipped", reason="no_pending_main")

        if ctx.next_state is None:
            if ctx.session_done:
                self._cleanup_session_locked(ctx.session_id, reason="session_done_without_next_state")
                return MainTurnFlushResult(status="skipped", reason="session_done_without_next_state")
            _log(f"pending kept session={ctx.session_id} reason=next_state_not_ready")
            return MainTurnFlushResult(status="pending", reason="next_state_not_ready")

        fallback_assistant = _extract_fallback_assistant(ctx.messages, before_index=ctx.next_state_index)
        sample = self._build_sample_locked(pending=pending, ctx=ctx, fallback_assistant=fallback_assistant)
        self._pending_by_session.pop(ctx.session_id, None)
        if sample is None:
            _log(f"pending flushed without scheduling session={ctx.session_id} reason=window_not_ready")
            if ctx.session_done:
                self._cleanup_session_locked(ctx.session_id, reason="session_done")
            return MainTurnFlushResult(status="skipped", reason="window_not_ready")

        if not self._mark_dedupe_locked(sample.dedupe_key):
            _log(f"dedupe skipped session={ctx.session_id} dedupe_key={sample.dedupe_key}")
            if ctx.session_done:
                self._cleanup_session_locked(ctx.session_id, reason="session_done")
            return MainTurnFlushResult(
                scheduled_job_id=None,
                status="skipped",
                reason="dedupe_skipped",
                dedupe_key=sample.dedupe_key,
            )

        job_id = self._schedule_extraction(sample)
        _log(
            f"pending flushed session={ctx.session_id} turn_index={pending.turn_index} "
            f"next_state_role={sample.metadata.get('next_state_role')} job_id={job_id or '<none>'}"
        )
        return MainTurnFlushResult(
            scheduled_job_id=(str(job_id).strip() or None),
            status="scheduled" if job_id else "skipped",
            reason="" if job_id else "scheduler_returned_empty_job_id",
            dedupe_key=sample.dedupe_key,
        )

    def finalize_request(
        self,
        *,
        ctx: OpenClawTurnContext,
        assistant: Optional[AssistantCapture],
        success: bool,
        error: str = "",
    ) -> None:
        """Cache current main turn after upstream reply, or clean session if finished."""
        if not ctx.session_id:
            return
        if not success:
            _log(
                f"error details session={ctx.session_id} turn_type={ctx.turn_type or '<empty>'} "
                f"turn_index={ctx.turn_index} error={error or 'forward_failed'}"
            )
            if ctx.session_done:
                self._cleanup_session_locked(ctx.session_id, reason="session_done_after_forward_error")
            return

        if ctx.turn_type != "main":
            _log(f"side skipped session={ctx.session_id} reason=turn_type_{ctx.turn_type or 'empty'}")
            if ctx.session_done:
                self._cleanup_session_locked(ctx.session_id, reason="session_done_after_side_turn")
            return

        if ctx.session_done:
            _log(
                f"session cleaned session={ctx.session_id} reason=final_main_without_next_state "
                f"turn_index={ctx.turn_index}"
            )
            self._cleanup_session_locked(ctx.session_id, reason="final_main_without_next_state")
            return

        assistant_message = assistant.as_message() if assistant is not None else None
        if assistant_message is None:
            _log(f"pending skipped session={ctx.session_id} turn_index={ctx.turn_index} reason=assistant_not_captured")
            return

        self._pending_by_session[ctx.session_id] = PendingMainTurn(
            session_id=ctx.session_id,
            user_id=ctx.user_id,
            turn_index=ctx.turn_index,
            request_seq=ctx.request_seq,
            prompt_messages_tail=list(ctx.prompt_messages_tail or []),
            assistant_message=dict(assistant_message),
            retrieval_reference=(dict(ctx.retrieval_reference) if isinstance(ctx.retrieval_reference, dict) else None),
            retrieval_metadata=(dict(ctx.retrieval_metadata) if isinstance(ctx.retrieval_metadata, dict) else None),
            source_metadata=dict(ctx.source_metadata or {}),
            timestamp_ms=int(time.time() * 1000),
        )
        _log(
            f"pending cached session={ctx.session_id} turn_index={ctx.turn_index} "
            f"request_seq={ctx.request_seq}"
        )

    def _build_sample_locked(
        self,
        *,
        pending: PendingMainTurn,
        ctx: OpenClawTurnContext,
        fallback_assistant: Optional[Dict[str, Any]],
    ) -> Optional[MainTurnSample]:
        """Run build sample locked."""
        assistant_message = pending.assistant_message or fallback_assistant
        if not isinstance(assistant_message, dict):
            return None
        assistant_content = str(assistant_message.get("content") or "").strip()
        if not assistant_content:
            return None
        next_state = dict(ctx.next_state or {})
        next_state_role = str(next_state.get("role") or "").strip().lower()
        if next_state_role not in {"user", "tool", "environment"}:
            return None

        tail_budget = max(1, int(self.config.ingest_window) - 2)
        prompt_tail = list(pending.prompt_messages_tail or [])[-tail_budget:]
        window = [dict(m) for m in prompt_tail] + [dict(assistant_message), next_state]
        if len(window) > int(self.config.ingest_window):
            window = window[-int(self.config.ingest_window) :]

        payload_for_hash = {
            "session_id": pending.session_id,
            "turn_index": pending.turn_index,
            "request_seq": pending.request_seq,
            "messages": window,
        }
        dedupe_key = hashlib.sha256(_compact_json(payload_for_hash, max_chars=0).encode("utf-8")).hexdigest()
        metadata: Dict[str, Any] = {
            "channel": "openclaw_main_turn_proxy",
            "trigger": "openclaw_main_turn_proxy",
            "source": "openclaw_main_turn_proxy",
            "session_id": pending.session_id,
            "turn_type": "main",
            "turn_index": int(pending.turn_index),
            "request_seq": int(pending.request_seq),
            "dedupe_key": dedupe_key,
            "next_state_role": next_state_role,
            "sample_timestamp_ms": int(pending.timestamp_ms),
        }
        if pending.retrieval_metadata:
            metadata["retrieval_context"] = dict(pending.retrieval_metadata)
        return MainTurnSample(
            user_id=pending.user_id,
            messages=window,
            metadata=metadata,
            dedupe_key=dedupe_key,
            retrieval_reference=(dict(pending.retrieval_reference) if isinstance(pending.retrieval_reference, dict) else None),
        )

    def _mark_dedupe_locked(self, dedupe_key: str) -> bool:
        """Run mark dedupe locked."""
        key = str(dedupe_key or "").strip()
        if not key:
            return True
        if key in self._seen_dedupe:
            return False
        self._seen_dedupe[key] = int(time.time() * 1000)
        if len(self._seen_dedupe) > int(self.config.dedupe_max_entries):
            items = sorted(self._seen_dedupe.items(), key=lambda item: item[1])
            keep = items[-int(self.config.dedupe_max_entries) :]
            self._seen_dedupe = {k: ts for k, ts in keep}
        return True

    def _next_sequence_locked(self, session_id: str) -> int:
        """Run next sequence locked."""
        current = int(self._seq_by_session.get(session_id) or 0) + 1
        self._seq_by_session[session_id] = current
        return current

    def _cleanup_session_locked(self, session_id: str, *, reason: str) -> None:
        """Run cleanup session locked."""
        self._pending_by_session.pop(session_id, None)
        self._seq_by_session.pop(session_id, None)
        _log(f"session cleaned session={session_id} reason={reason}")


class UpstreamChatProxy:
    """Thin OpenAI-compatible reverse proxy for `/v1/chat/completions`."""

    def __init__(self, *, config: OpenClawMainTurnProxyConfig) -> None:
        """Run init."""
        self.config = config.normalize()

    def forward(
        self,
        handler: BaseHTTPRequestHandler,
        *,
        body: Dict[str, Any],
        headers: Any,
    ) -> Tuple[bool, bool, Optional[AssistantCapture], str]:
        """
        Forward one chat completion request.

        Returns:
        - success
        - response_sent
        - assistant capture
        - error text (non-empty only when success=False)
        """

        target_url = self.config.target_chat_url
        if not target_url:
            return False, False, None, "proxy target base_url is not configured"

        raw_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        upstream_headers = _copy_headers_for_upstream(headers, target_api_key=self.config.target_api_key)
        upstream_headers["Content-Type"] = "application/json"
        upstream_headers["Content-Length"] = str(len(raw_body))

        parsed = urlparse(target_url)
        conn_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
        conn = conn_cls(parsed.hostname, parsed.port, timeout=float(self.config.connect_timeout_s))
        try:
            conn.request(
                "POST",
                (parsed.path or "/") + (("?" + parsed.query) if parsed.query else ""),
                body=raw_body,
                headers=upstream_headers,
            )
            resp = conn.getresponse()
            try:
                resp.fp.raw._sock.settimeout(float(self.config.read_timeout_s))  # type: ignore[attr-defined]
            except Exception:
                pass
            stream = _bool_from_any(body.get("stream"), False)
            if stream:
                assistant = self._forward_stream(handler, resp)
                return (
                    200 <= int(resp.status or 0) < 300,
                    True,
                    assistant,
                    "" if 200 <= int(resp.status or 0) < 300 else "upstream_stream_failed",
                )
            return self._forward_non_stream(handler, resp)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError) as e:
            return False, True, None, str(e)
        except Exception as e:
            return False, False, None, str(e)
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _forward_non_stream(
        self,
        handler: BaseHTTPRequestHandler,
        resp: http.client.HTTPResponse,
    ) -> Tuple[bool, bool, Optional[AssistantCapture], str]:
        """Run forward non stream."""
        raw = resp.read()
        status = int(resp.status or 502)
        payload = None
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = None

        handler.send_response(status)
        _copy_headers_to_client(
            handler,
            headers=list(resp.getheaders()),
            content_length=len(raw),
        )
        handler.end_headers()
        handler.wfile.write(raw)
        handler.wfile.flush()

        assistant = assistant_capture_from_chat_payload(payload)
        success = 200 <= status < 300
        err = ""
        if not success:
            err = str((payload or {}).get("error") or raw.decode("utf-8", errors="ignore") or f"HTTP {status}")[:1000]
        return success, True, assistant, err

    def _forward_stream(
        self,
        handler: BaseHTTPRequestHandler,
        resp: http.client.HTTPResponse,
    ) -> Optional[AssistantCapture]:
        """Run forward stream."""
        status = int(resp.status or 502)
        response_headers = list(resp.getheaders())
        handler.send_response(status)
        _copy_headers_to_client(handler, headers=response_headers, content_length=None)
        handler.end_headers()

        content_type = ""
        for key, value in response_headers:
            if str(key).strip().lower() == "content-type":
                content_type = str(value or "").strip().lower()
                break

        accumulator = StreamAssistantAccumulator() if "text/event-stream" in content_type else None
        raw_capture = bytearray()
        while True:
            chunk = resp.read(4096)
            if not chunk:
                break
            if accumulator is not None:
                accumulator.feed(chunk)
            else:
                if len(raw_capture) < 2_000_000:
                    raw_capture.extend(chunk)
            handler.wfile.write(chunk)
            handler.wfile.flush()

        if accumulator is not None:
            return accumulator.finish()
        if raw_capture:
            try:
                payload = json.loads(bytes(raw_capture).decode("utf-8"))
            except Exception:
                payload = None
            return assistant_capture_from_chat_payload(payload)
        return None
