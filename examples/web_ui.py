"""
Local web UI for AutoSkill interactive chat.

This server provides:
- a simple HTML frontend (chat + command input)
- retrieval display (rewritten query, hits, selected skills)
- extraction display (upserted skills + SKILL.md preview)

No external dependencies are required (stdlib `http.server`).
Run:
  python3 -m examples.web_ui
Then open:
  http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import uuid
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.config import default_store_path
from autoskill.interactive import InteractiveConfig, LLMQueryRewriter
from autoskill.interactive.session import InteractiveSession
from autoskill.interactive.skill_versions import (
    apply_snapshot as _apply_snapshot,
    examples_to_raw as _examples_to_raw,
    history_from_metadata as _history_from_metadata,
    pop_skill_snapshot as _pop_skill_snapshot,
    push_skill_snapshot as _push_skill_snapshot,
)
from autoskill.llm.factory import build_llm
from autoskill.models import Skill, SkillExample

from .interactive_chat import (
    _env,
    _pick_default_provider,
    build_embeddings_config,
    build_llm_config,
)

_SESSION_DUMP_VERSION = 1


def _json_response(handler: BaseHTTPRequestHandler, payload: Any, *, status: int = 200) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(int(status))
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _read_json(handler: BaseHTTPRequestHandler, *, max_bytes: int = 5_000_000) -> Dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or 0)
    if length <= 0:
        return {}
    if length > int(max_bytes):
        raise ValueError(f"request too large: {length} bytes")
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    obj = json.loads(raw.decode("utf-8"))
    if obj is None:
        return {}
    if not isinstance(obj, dict):
        raise ValueError("request body must be a JSON object")
    return obj


def _repo_root() -> Path:
    # examples/web_ui.py -> examples/ -> repo root
    return Path(__file__).resolve().parents[1]


def _web_dir() -> Path:
    return _repo_root() / "web"


def _safe_static_path(path: str) -> Optional[Path]:
    web = _web_dir().resolve()
    rel = str(path or "").lstrip("/")
    if not rel.startswith("static/"):
        return None
    candidate = (web / rel.replace("/", os.sep)).resolve()
    try:
        candidate.relative_to(web)
    except Exception:
        return None
    return candidate


def _content_type_for(path: str) -> str:
    p = str(path or "").lower()
    if p.endswith(".html"):
        return "text/html; charset=utf-8"
    if p.endswith(".css"):
        return "text/css; charset=utf-8"
    if p.endswith(".js"):
        return "application/javascript; charset=utf-8"
    if p.endswith(".json"):
        return "application/json; charset=utf-8"
    if p.endswith(".svg"):
        return "image/svg+xml"
    if p.endswith(".png"):
        return "image/png"
    if p.endswith(".jpg") or p.endswith(".jpeg"):
        return "image/jpeg"
    if p.endswith(".txt"):
        return "text/plain; charset=utf-8"
    return "application/octet-stream"


def _coerce_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if not s:
        return None
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return None


class _SessionManager:
    def __init__(
        self,
        *,
        sdk: AutoSkill,
        interactive_cfg: InteractiveConfig,
        chat_llm: Optional[Any],
        query_rewriter: Optional[LLMQueryRewriter],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.sdk = sdk
        self.interactive_cfg = interactive_cfg
        self.chat_llm = chat_llm
        self.query_rewriter = query_rewriter
        self.llm_config = dict(llm_config or {})

        self._lock = threading.Lock()
        self._sessions: Dict[str, InteractiveSession] = {}
        self._meta: Dict[str, Dict[str, Any]] = {}
        self._trace: Dict[str, Dict[str, Any]] = {}

        store_root = os.path.abspath(
            os.path.expanduser(str(getattr(self.interactive_cfg, "store_dir", "") or "SkillBank"))
        )
        user_key = str(getattr(self.interactive_cfg, "user_id", "") or "u1").strip() or "u1"
        self._persist_file = os.path.join(store_root, "web_sessions", f"{user_key}.json")
        self._load_from_disk()

    def runtime_info(self) -> Dict[str, Any]:
        provider = str(self.llm_config.get("provider") or "mock").strip().lower() or "mock"
        model = str(self.llm_config.get("model") or "").strip()

        thinking: Dict[str, Any] = {
            "supported": False,
            "requested": None,
            "effective": None,
            "auto_disabled": False,
        }
        if provider in {"internlm", "intern", "intern-s1", "intern-s1-pro"}:
            requested = _coerce_bool(self.llm_config.get("thinking_mode"))
            if requested is None:
                requested = True
            effective = requested
            auto_disabled = False
            if self.chat_llm is not None and hasattr(self.chat_llm, "thinking_mode_status"):
                try:
                    st = self.chat_llm.thinking_mode_status()
                except Exception:
                    st = None
                if isinstance(st, dict):
                    requested2 = _coerce_bool(st.get("requested"))
                    effective2 = _coerce_bool(st.get("effective"))
                    auto_disabled2 = _coerce_bool(st.get("auto_disabled"))
                    if requested2 is not None:
                        requested = requested2
                    if effective2 is not None:
                        effective = effective2
                    if auto_disabled2 is not None:
                        auto_disabled = auto_disabled2
            thinking = {
                "supported": True,
                "requested": requested,
                "effective": effective,
                "auto_disabled": bool(auto_disabled),
            }

        return {
            "llm_provider": provider,
            "llm_model": model,
            "thinking": thinking,
        }

    @staticmethod
    def _now_ms() -> int:
        import time

        return int(time.time() * 1000)

    @staticmethod
    def _title_from_text(text: str, *, max_chars: int = 32) -> str:
        s = " ".join(str(text or "").strip().split())
        if not s:
            return "New Chat"
        chars = list(s)
        if len(chars) <= max_chars:
            return s
        return "".join(chars[: max(3, max_chars - 3)]) + "..."

    @staticmethod
    def _session_preview(messages: List[Dict[str, Any]], *, max_chars: int = 120) -> str:
        for m in reversed(messages or []):
            content = str((m or {}).get("content") or "").strip()
            if content:
                s = " ".join(content.split())
                if len(s) <= max_chars:
                    return s
                return s[: max(3, max_chars - 3)] + "..."
        return ""

    @staticmethod
    def _default_trace() -> Dict[str, Any]:
        return {
            "version": 1,
            "next_turn_seq": 1,
            "turns": [],
            "retrieval_events": [],
            "extraction_events": [],
            "config_events": [],
            "last_result": None,
        }

    @staticmethod
    def _clone(obj: Any) -> Any:
        try:
            return json.loads(json.dumps(obj, ensure_ascii=False))
        except Exception:
            return None

    def _trace_for_locked(self, sid: str) -> Dict[str, Any]:
        t = self._trace.get(sid)
        if not isinstance(t, dict):
            t = self._default_trace()
            self._trace[sid] = t
        return t

    def _append_event_locked(self, sid: str, bucket: str, payload: Dict[str, Any]) -> None:
        tr = self._trace_for_locked(sid)
        arr = tr.get(bucket)
        if not isinstance(arr, list):
            arr = []
            tr[bucket] = arr
        arr.append(dict(payload or {}))

    @staticmethod
    def _trace_turn_id(seq: int) -> str:
        return f"turn_{int(seq)}"

    def _next_turn_id_locked(self, sid: str) -> str:
        tr = self._trace_for_locked(sid)
        seq_raw = tr.get("next_turn_seq")
        try:
            seq = int(seq_raw)
        except Exception:
            seq = 1
        if seq < 1:
            seq = 1
        tr["next_turn_seq"] = seq + 1
        return self._trace_turn_id(seq)

    def _find_turn_locked(self, sid: str, turn_id: str) -> Optional[Dict[str, Any]]:
        tr = self._trace_for_locked(sid)
        turns = tr.get("turns")
        if not isinstance(turns, list):
            turns = []
            tr["turns"] = turns
        for item in reversed(turns):
            if not isinstance(item, dict):
                continue
            if str(item.get("id") or "").strip() == str(turn_id or "").strip():
                return item
        return None

    def begin_turn(self, sid: str, *, user_text: str) -> Optional[str]:
        key = str(sid or "").strip()
        if not key:
            return None
        now = self._now_ms()
        with self._lock:
            if key not in self._sessions:
                return None
            turn_id = self._next_turn_id_locked(key)
            tr = self._trace_for_locked(key)
            turns = tr.get("turns")
            if not isinstance(turns, list):
                turns = []
                tr["turns"] = turns
            turns.append(
                {
                    "id": turn_id,
                    "input": str(user_text or ""),
                    "started_at_ms": now,
                    "finished_at_ms": None,
                    "kind": "unknown",
                    "command": "",
                    "chat_append": [],
                    "retrieval": None,
                    "extraction": None,
                    "error": "",
                }
            )
            return turn_id

    def record_retrieval(self, sid: str, *, turn_id: Optional[str], retrieval: Any, source: str) -> None:
        key = str(sid or "").strip()
        if not key:
            return
        if not isinstance(retrieval, dict):
            return
        now = self._now_ms()
        rec = self._clone(retrieval) or {}
        with self._lock:
            if key not in self._sessions:
                return
            self._append_event_locked(
                key,
                "retrieval_events",
                {
                    "event_time": now,
                    "source": str(source or ""),
                    "turn_id": (str(turn_id).strip() if turn_id else None),
                    "retrieval": rec,
                },
            )
            if turn_id:
                turn = self._find_turn_locked(key, turn_id)
                if turn is not None:
                    turn["retrieval"] = rec

    def record_extraction(self, sid: str, *, turn_id: Optional[str], extraction: Any, source: str) -> None:
        key = str(sid or "").strip()
        if not key:
            return
        if not isinstance(extraction, dict):
            return
        now = self._now_ms()
        rec = self._clone(extraction) or {}
        with self._lock:
            if key not in self._sessions:
                return
            turn_id_s = str(turn_id or "").strip()
            if not turn_id_s:
                job_id = str(rec.get("job_id") or rec.get("jobId") or "").strip()
                if job_id:
                    tr_prev = self._trace_for_locked(key)
                    prev_events = tr_prev.get("extraction_events")
                    if isinstance(prev_events, list):
                        for ev in reversed(prev_events):
                            if not isinstance(ev, dict):
                                continue
                            ev_tid = str(ev.get("turn_id") or ev.get("turnId") or "").strip()
                            if not ev_tid:
                                continue
                            ev_ex = ev.get("extraction")
                            if not isinstance(ev_ex, dict):
                                continue
                            ev_job = str(ev_ex.get("job_id") or ev_ex.get("jobId") or "").strip()
                            if ev_job and ev_job == job_id:
                                turn_id_s = ev_tid
                                break
            self._append_event_locked(
                key,
                "extraction_events",
                {
                    "event_time": now,
                    "source": str(source or ""),
                    "turn_id": (turn_id_s or None),
                    "extraction": rec,
                },
            )
            if turn_id_s:
                turn = self._find_turn_locked(key, turn_id_s)
                if turn is not None:
                    turn["extraction"] = rec
            # Keep latest extraction in trace-level last_result so UI restore can always recover it.
            tr = self._trace_for_locked(key)
            last_result = tr.get("last_result")
            if not isinstance(last_result, dict):
                last_result = {}
            last_result["extraction"] = rec
            tr["last_result"] = last_result

    def complete_turn(self, sid: str, *, turn_id: Optional[str], result: Any, source: str) -> None:
        key = str(sid or "").strip()
        if not key:
            return
        if not isinstance(result, dict):
            return
        now = self._now_ms()
        result_copy = self._clone(result) or {}
        with self._lock:
            if key not in self._sessions:
                return
            if turn_id:
                turn = self._find_turn_locked(key, turn_id)
                if turn is not None:
                    turn["finished_at_ms"] = now
                    turn["kind"] = str(result.get("kind") or "unknown")
                    turn["command"] = str(result.get("command") or "")
                    chat_append = result.get("chat_append")
                    turn["chat_append"] = self._clone(chat_append) if isinstance(chat_append, list) else []
                    turn["error"] = ""
            tr = self._trace_for_locked(key)
            tr["last_result"] = result_copy

        # Record retrieval/extraction payloads from final result as well.
        self.record_retrieval(key, turn_id=turn_id, retrieval=result.get("retrieval"), source=source)
        self.record_extraction(key, turn_id=turn_id, extraction=result.get("extraction"), source=source)

    def fail_turn(self, sid: str, *, turn_id: Optional[str], error: str) -> None:
        key = str(sid or "").strip()
        if not key:
            return
        now = self._now_ms()
        msg = str(error or "").strip()
        with self._lock:
            if key not in self._sessions:
                return
            if turn_id:
                turn = self._find_turn_locked(key, turn_id)
                if turn is not None:
                    turn["finished_at_ms"] = now
                    turn["kind"] = "error"
                    turn["command"] = ""
                    turn["chat_append"] = []
                    turn["error"] = msg
            tr = self._trace_for_locked(key)
            tr["last_result"] = {"kind": "error", "error": msg}

    def _save_to_disk_locked(self) -> None:
        try:
            root_dir = os.path.dirname(self._persist_file)
            os.makedirs(root_dir, exist_ok=True)
            sessions_out: List[Dict[str, Any]] = []
            for sid, session in self._sessions.items():
                meta = dict(self._meta.get(sid) or {})
                trace = self._clone(self._trace.get(sid) or self._default_trace()) or self._default_trace()
                sessions_out.append(
                    {
                        "id": sid,
                        "meta": meta,
                        "state": session.state(),
                        "trace": trace,
                    }
                )
            payload = {
                "version": _SESSION_DUMP_VERSION,
                "user_id": str(getattr(self.interactive_cfg, "user_id", "") or "u1"),
                "saved_at_ms": self._now_ms(),
                "sessions": sessions_out,
            }
            tmp = self._persist_file + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False, indent=2))
            os.replace(tmp, self._persist_file)
        except Exception:
            return

    def _load_from_disk(self) -> None:
        path = str(self._persist_file or "")
        if not path or not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                obj = json.loads(f.read())
        except Exception:
            return
        if not isinstance(obj, dict):
            return
        sessions = obj.get("sessions")
        if not isinstance(sessions, list):
            return

        for item in sessions:
            if not isinstance(item, dict):
                continue
            sid = str(item.get("id") or "").strip() or str(uuid.uuid4())
            state = item.get("state")
            if not isinstance(state, dict):
                state = {}
            cfg_raw = state.get("config")
            cfg = InteractiveConfig(**asdict(self.interactive_cfg)).normalize()
            if isinstance(cfg_raw, dict):
                for k, v in cfg_raw.items():
                    if hasattr(cfg, k):
                        setattr(cfg, k, v)
                cfg = cfg.normalize()

            session = InteractiveSession(
                sdk=self.sdk,
                config=cfg,
                chat_llm=self.chat_llm,
                query_rewriter=self.query_rewriter,
                skill_selector=None,
            )
            msgs = state.get("messages")
            if isinstance(msgs, list):
                session.messages = [m for m in msgs if isinstance(m, dict)]

            meta = item.get("meta")
            if not isinstance(meta, dict):
                meta = {}
            now = self._now_ms()
            title = str(meta.get("title") or "").strip() or "New Chat"
            created_at_ms = int(meta.get("created_at_ms") or now)
            updated_at_ms = int(meta.get("updated_at_ms") or now)

            trace = item.get("trace")
            if not isinstance(trace, dict):
                trace = self._default_trace()
            trace.setdefault("next_turn_seq", 1)
            trace.setdefault("turns", [])
            trace.setdefault("retrieval_events", [])
            trace.setdefault("extraction_events", [])
            trace.setdefault("config_events", [])
            trace.setdefault("last_result", None)

            self._sessions[sid] = session
            self._meta[sid] = {
                "id": sid,
                "title": title,
                "created_at_ms": created_at_ms,
                "updated_at_ms": updated_at_ms,
            }
            self._trace[sid] = trace

    def new_session(self, *, overrides: Optional[Dict[str, Any]] = None) -> Tuple[str, InteractiveSession]:
        overrides2 = dict(overrides or {})
        cfg = InteractiveConfig(**asdict(self.interactive_cfg)).normalize()
        for k, v in overrides2.items():
            if not hasattr(cfg, k):
                continue
            setattr(cfg, k, v)
        cfg = cfg.normalize()

        sid = str(uuid.uuid4())
        session = InteractiveSession(
            sdk=self.sdk,
            config=cfg,
            chat_llm=self.chat_llm,
            query_rewriter=self.query_rewriter,
            skill_selector=None,
        )
        now = self._now_ms()
        with self._lock:
            self._sessions[sid] = session
            self._meta[sid] = {
                "id": sid,
                "title": "New Chat",
                "created_at_ms": now,
                "updated_at_ms": now,
            }
            self._trace[sid] = self._default_trace()
            self._append_event_locked(
                sid,
                "config_events",
                {"event_time": now, "source": "session/new", "config": asdict(cfg)},
            )
            self._save_to_disk_locked()
        return sid, session

    def get(self, sid: str) -> Optional[InteractiveSession]:
        key = str(sid or "").strip()
        if not key:
            return None
        with self._lock:
            return self._sessions.get(key)

    def get_trace(self, sid: str) -> Optional[Dict[str, Any]]:
        key = str(sid or "").strip()
        if not key:
            return None
        with self._lock:
            if key not in self._sessions:
                return None
            trace = self._clone(self._trace.get(key) or self._default_trace())
            if not isinstance(trace, dict):
                return self._default_trace()
            return trace

    def touch(self, sid: str, *, user_text: Optional[str] = None) -> None:
        key = str(sid or "").strip()
        if not key:
            return
        now = self._now_ms()
        with self._lock:
            meta = self._meta.get(key)
            if meta is None:
                meta = {
                    "id": key,
                    "title": "New Chat",
                    "created_at_ms": now,
                    "updated_at_ms": now,
                }
                self._meta[key] = meta
            meta["updated_at_ms"] = now
            txt = str(user_text or "").strip()
            if txt:
                title = str(meta.get("title") or "").strip()
                if not title or title == "New Chat":
                    meta["title"] = self._title_from_text(txt)
            self._save_to_disk_locked()

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._lock:
            items: List[Dict[str, Any]] = []
            for sid, session in self._sessions.items():
                meta = dict(self._meta.get(sid) or {})
                state = session.state()
                msgs = list(state.get("messages") or [])
                preview = self._session_preview(msgs)
                title = str(meta.get("title") or "").strip() or self._title_from_text(preview)
                items.append(
                    {
                        "id": sid,
                        "title": title or "New Chat",
                        "created_at_ms": int(meta.get("created_at_ms") or self._now_ms()),
                        "updated_at_ms": int(meta.get("updated_at_ms") or self._now_ms()),
                        "message_count": int(len(msgs)),
                        "preview": preview,
                    }
                )
        items.sort(key=lambda x: int(x.get("updated_at_ms") or 0), reverse=True)
        return items

    def delete_session(self, sid: str) -> Tuple[bool, Optional[str]]:
        key = str(sid or "").strip()
        if not key:
            return False, None
        with self._lock:
            if key not in self._sessions:
                return False, None
            self._sessions.pop(key, None)
            self._meta.pop(key, None)
            self._trace.pop(key, None)

            next_sid: Optional[str] = None
            if self._sessions:
                ranked: List[Tuple[int, str]] = []
                for cur_sid in self._sessions.keys():
                    meta = self._meta.get(cur_sid) or {}
                    updated = int(meta.get("updated_at_ms") or 0)
                    ranked.append((updated, str(cur_sid)))
                ranked.sort(key=lambda x: x[0], reverse=True)
                next_sid = ranked[0][1] if ranked else next(iter(self._sessions.keys()))

            self._save_to_disk_locked()
            return True, next_sid


def make_handler(manager: _SessionManager) -> type[BaseHTTPRequestHandler]:
    web = _web_dir()

    class Handler(BaseHTTPRequestHandler):
        server_version = "AutoSkillWeb/0.1"

        def log_message(self, format: str, *args: Any) -> None:
            # Keep console output readable.
            msg = str(format or "") % args
            print(f"[web] {msg}")

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path or "/")
            path = parsed.path or "/"

            if path == "/api/health":
                return _json_response(self, {"ok": True, "runtime": manager.runtime_info()})

            if path == "/" or path == "/index.html":
                index = web / "index.html"
                if not index.exists():
                    return _json_response(self, {"error": "web/index.html not found"}, status=500)
                data = index.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", _content_type_for(str(index)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            static_path = _safe_static_path(path)
            if static_path is not None and static_path.exists() and static_path.is_file():
                data = static_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", _content_type_for(str(static_path)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            self.send_response(404)
            self.end_headers()

        def _start_ndjson(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()

        def _write_ndjson(self, payload: Dict[str, Any]) -> None:
            data = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
            self.wfile.write(data)
            self.wfile.flush()

        @staticmethod
        def _extract_extraction_events(polled: Any) -> List[Dict[str, Any]]:
            events_obj = polled.get("events") if isinstance(polled, dict) else {}
            out: List[Dict[str, Any]] = []
            if isinstance(events_obj, dict):
                raw = events_obj.get("extraction")
                if isinstance(raw, list):
                    out = [ev for ev in raw if isinstance(ev, dict)]
            return out

        def _drain_extraction_events_for_refresh(self, sid: str, session: InteractiveSession) -> List[Dict[str, Any]]:
            """
            Drains background extraction events and persists them to trace.

            This is used by both `/api/session/poll` and `/api/session/state` so that
            page refresh can recover the latest extraction result immediately instead of
            showing an old scheduled/running state.
            """

            polled = session.poll()
            extraction_events = self._extract_extraction_events(polled)
            if extraction_events:
                for ev in extraction_events:
                    manager.record_extraction(sid, turn_id=None, extraction=ev, source="poll")
                manager.touch(sid)
            return extraction_events

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path or "/")
            path = parsed.path or "/"
            try:
                body = _read_json(self)
            except Exception as e:
                return _json_response(self, {"error": str(e)}, status=400)

            if path == "/api/session/new":
                overrides = body.get("config") if isinstance(body, dict) else None
                if overrides is not None and not isinstance(overrides, dict):
                    return _json_response(self, {"error": "config must be an object"}, status=400)
                sid, session = manager.new_session(overrides=overrides)
                return _json_response(
                    self,
                    {
                        "session_id": sid,
                        "state": session.state(),
                        "trace": manager.get_trace(sid),
                        "runtime": manager.runtime_info(),
                        "sessions": manager.list_sessions(),
                    },
                )

            if path == "/api/session/list":
                return _json_response(self, {"sessions": manager.list_sessions()})

            if path == "/api/session/delete":
                sid = str(body.get("session_id") or "").strip()
                if not sid:
                    return _json_response(self, {"error": "session_id is required"}, status=400)
                deleted, next_sid = manager.delete_session(sid)
                if not deleted:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                next_state = None
                next_trace = None
                if next_sid:
                    next_session = manager.get(next_sid)
                    if next_session is not None:
                        next_state = next_session.state()
                        next_trace = manager.get_trace(next_sid)
                return _json_response(
                    self,
                    {
                        "deleted_session_id": sid,
                        "next_session_id": next_sid,
                        "state": next_state,
                        "trace": next_trace,
                        "runtime": manager.runtime_info(),
                        "sessions": manager.list_sessions(),
                    },
                )

            if path == "/api/session/state":
                sid = str(body.get("session_id") or "").strip()
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                # Refresh-time reconciliation: opportunistically drain background extraction
                # events so the right panel can restore completed skill details immediately.
                extraction_events = self._drain_extraction_events_for_refresh(sid, session)
                return _json_response(
                    self,
                    {
                        "session_id": sid,
                        "state": session.state(),
                        "trace": manager.get_trace(sid),
                        "events": {"extraction": extraction_events},
                        "runtime": manager.runtime_info(),
                        "sessions": manager.list_sessions(),
                    },
                )

            if path == "/api/session/poll":
                sid = str(body.get("session_id") or "").strip()
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                polled = session.poll()
                extraction_events = self._extract_extraction_events(polled)
                if extraction_events:
                    for ev in extraction_events:
                        manager.record_extraction(sid, turn_id=None, extraction=ev, source="poll")
                    # Persist extraction trace updates so refresh can restore the right-side panel.
                    manager.touch(sid)
                return _json_response(self, {"session_id": sid, "runtime": manager.runtime_info(), **polled})

            if path == "/api/session/input":
                sid = str(body.get("session_id") or "").strip()
                text = str(body.get("text") or "")
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                turn_id = manager.begin_turn(sid, user_text=text)
                try:
                    manager.touch(sid, user_text=text)
                    out = session.handle_input(text)
                    manager.complete_turn(sid, turn_id=turn_id, result=out, source="input")
                    # Persist again after generation so the latest assistant turn is not lost on refresh.
                    manager.touch(sid)
                except Exception as e:
                    manager.fail_turn(sid, turn_id=turn_id, error=str(e))
                    return _json_response(self, {"error": str(e)}, status=500)
                return _json_response(self, {"session_id": sid, "result": out, "runtime": manager.runtime_info()})

            if path == "/api/session/input_stream":
                sid = str(body.get("session_id") or "").strip()
                text = str(body.get("text") or "")
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                turn_id = manager.begin_turn(sid, user_text=text)
                try:
                    manager.touch(sid, user_text=text)
                    self._start_ndjson()
                    self._write_ndjson(
                        {"type": "meta", "session_id": sid, "runtime": manager.runtime_info()}
                    )
                    for ev in session.handle_input_stream(text):
                        if not isinstance(ev, dict):
                            continue
                        ev_type = str(ev.get("type") or "").strip().lower()
                        if ev_type == "retrieval":
                            manager.record_retrieval(
                                sid, turn_id=turn_id, retrieval=ev.get("retrieval"), source="stream"
                            )
                        elif ev_type == "extraction":
                            manager.record_extraction(
                                sid, turn_id=turn_id, extraction=ev.get("extraction"), source="stream"
                            )
                        elif ev_type == "result":
                            result_payload = ev.get("result")
                            if isinstance(result_payload, dict):
                                result_payload = dict(result_payload)
                                result_payload["runtime"] = manager.runtime_info()
                                ev = dict(ev)
                                ev["result"] = result_payload
                            manager.complete_turn(sid, turn_id=turn_id, result=ev.get("result"), source="stream")
                        self._write_ndjson(ev)
                    # Persist after stream completes so refresh always sees the final turn.
                    manager.touch(sid)
                except BrokenPipeError:
                    # Client disconnected; keep server-side conversation state persisted.
                    try:
                        manager.fail_turn(sid, turn_id=turn_id, error="client disconnected")
                        manager.touch(sid)
                    except Exception:
                        pass
                    return
                except Exception as e:
                    manager.fail_turn(sid, turn_id=turn_id, error=str(e))
                    try:
                        self._write_ndjson({"type": "error", "error": str(e)})
                    except Exception:
                        pass
                    try:
                        manager.touch(sid)
                    except Exception:
                        pass
                return

            if path == "/api/skills/get_many":
                sid = str(body.get("session_id") or "").strip()
                skill_ids_raw = body.get("skill_ids")
                if not sid:
                    return _json_response(self, {"error": "session_id is required"}, status=400)
                if not isinstance(skill_ids_raw, list):
                    return _json_response(self, {"error": "skill_ids must be an array"}, status=400)

                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)

                uid = str(session.config.user_id or "").strip()
                out: List[Dict[str, Any]] = []
                for item in skill_ids_raw[:500]:
                    skill_id = str(item or "").strip()
                    if not skill_id:
                        continue
                    skill = manager.sdk.get(skill_id)
                    if skill is None:
                        continue
                    owner = str(getattr(skill, "user_id", "") or "").strip()
                    # For export/debug purposes, allow current user's skills and shared library skills.
                    if owner and not owner.startswith("library:") and owner != uid:
                        continue
                    md = manager.sdk.export_skill_md(skill_id) or ""
                    out.append(
                        {
                            "id": str(skill.id),
                            "name": str(skill.name),
                            "description": str(skill.description),
                            "version": str(skill.version),
                            "owner": str(skill.user_id),
                            "triggers": [str(t) for t in (skill.triggers or [])],
                            "tags": [str(t) for t in (skill.tags or [])],
                            "examples": _examples_to_raw(list(skill.examples or [])),
                            "instructions": str(skill.instructions or ""),
                            "skill_md": md,
                            "created_at": str(skill.created_at or ""),
                            "updated_at": str(skill.updated_at or ""),
                            "metadata": dict(skill.metadata or {}),
                        }
                    )
                return _json_response(self, {"skills": out})

            if path == "/api/skill/save_md":
                sid = str(body.get("session_id") or "").strip()
                skill_id = str(body.get("skill_id") or "").strip()
                md = str(body.get("skill_md") or "")
                if not sid or not skill_id:
                    return _json_response(self, {"error": "session_id and skill_id are required"}, status=400)

                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)

                skill = manager.sdk.get(skill_id)
                if skill is None:
                    return _json_response(self, {"error": "unknown skill_id"}, status=404)

                owner = str(getattr(skill, "user_id", "") or "").strip()
                if owner.startswith("library:"):
                    return _json_response(self, {"error": "library skills are read-only"}, status=403)
                if owner and owner != str(session.config.user_id or "").strip():
                    return _json_response(self, {"error": "skill does not belong to this session user"}, status=403)

                from autoskill.management.formats.agent_skill import (
                    parse_agent_skill_md,
                    upsert_skill_md_metadata,
                )
                from autoskill.utils.time import now_iso

                parsed = parse_agent_skill_md(md)
                name = str(parsed.get("name") or "").strip() or str(skill.name or "").strip()
                if not name:
                    return _json_response(self, {"error": "SKILL.md must include a non-empty name"}, status=400)

                description = (
                    str(parsed.get("description") or "").strip()
                    or str(skill.description or "").strip()
                    or name
                )
                instructions = str(parsed.get("prompt") or "").strip() or str(skill.instructions or "").strip()
                version = str(parsed.get("version") or "").strip() or str(skill.version or "0.1.0").strip()

                tags = parsed.get("tags") or []
                if not isinstance(tags, list):
                    tags = []
                tags2 = [str(t).strip() for t in tags if str(t).strip()]

                triggers = parsed.get("triggers") or []
                if not isinstance(triggers, list):
                    triggers = []
                triggers2 = [str(t).strip() for t in triggers if str(t).strip()]

                examples2 = []
                ex_raw = parsed.get("examples") or []
                if isinstance(ex_raw, list):
                    for ex in ex_raw[:20]:
                        if not isinstance(ex, dict):
                            continue
                        inp = str(ex.get("input") or "").strip()
                        if not inp:
                            continue
                        examples2.append(
                            SkillExample(
                                input=inp,
                                output=(str(ex.get("output")).strip() if ex.get("output") else None),
                                notes=(str(ex.get("notes")).strip() if ex.get("notes") else None),
                            )
                        )

                md2 = upsert_skill_md_metadata(
                    md, skill_id=skill_id, name=name, description=description, version=version
                )

                history_size = _push_skill_snapshot(skill)
                skill.name = name
                skill.description = description
                skill.instructions = instructions
                skill.version = version
                skill.tags = tags2
                skill.triggers = triggers2
                skill.examples = examples2
                skill.updated_at = now_iso()
                skill.files = dict(skill.files or {})
                skill.files["SKILL.md"] = md2

                try:
                    manager.sdk.store.upsert(skill, raw=asdict(skill))
                except Exception as e:
                    return _json_response(self, {"error": str(e)}, status=500)

                return _json_response(
                    self,
                    {
                        "ok": True,
                        "skill": {
                            "id": skill.id,
                            "name": skill.name,
                            "description": skill.description,
                            "version": skill.version,
                            "owner": skill.user_id,
                        },
                        "skill_md": md2,
                        "history_count": int(history_size),
                    },
                )

            if path == "/api/skill/rollback_prev":
                sid = str(body.get("session_id") or "").strip()
                skill_id = str(body.get("skill_id") or "").strip()
                if not sid or not skill_id:
                    return _json_response(self, {"error": "session_id and skill_id are required"}, status=400)

                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)

                skill = manager.sdk.get(skill_id)
                if skill is None:
                    return _json_response(self, {"error": "unknown skill_id"}, status=404)

                owner = str(getattr(skill, "user_id", "") or "").strip()
                if owner.startswith("library:"):
                    return _json_response(self, {"error": "library skills are read-only"}, status=403)
                if owner and owner != str(session.config.user_id or "").strip():
                    return _json_response(self, {"error": "skill does not belong to this session user"}, status=403)

                from autoskill.utils.time import now_iso

                snapshot = _pop_skill_snapshot(skill)
                if snapshot is None:
                    return _json_response(self, {"error": "no previous version available"}, status=400)

                _apply_snapshot(skill, snapshot)
                skill.updated_at = now_iso()
                skill.files = dict(skill.files or {})
                skill_md = str(skill.files.get("SKILL.md") or "")

                try:
                    manager.sdk.store.upsert(skill, raw=asdict(skill))
                except Exception as e:
                    return _json_response(self, {"error": str(e)}, status=500)

                history_count = len(_history_from_metadata(dict(skill.metadata or {})))
                return _json_response(
                    self,
                    {
                        "ok": True,
                        "skill": {
                            "id": skill.id,
                            "name": skill.name,
                            "description": skill.description,
                            "version": skill.version,
                            "owner": skill.user_id,
                        },
                        "skill_md": skill_md,
                        "restored_from": {
                            "version": str(snapshot.get("version") or ""),
                            "updated_at": str(snapshot.get("updated_at") or ""),
                        },
                        "history_count": int(history_count),
                    },
                )

            if path == "/api/skill/delete":
                sid = str(body.get("session_id") or "").strip()
                skill_id = str(body.get("skill_id") or "").strip()
                if not sid or not skill_id:
                    return _json_response(self, {"error": "session_id and skill_id are required"}, status=400)

                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)

                skill = manager.sdk.get(skill_id)
                if skill is None:
                    return _json_response(self, {"error": "unknown skill_id"}, status=404)

                owner = str(getattr(skill, "user_id", "") or "").strip()
                if owner.startswith("library:"):
                    return _json_response(self, {"error": "library skills are read-only"}, status=403)
                if owner and owner != str(session.config.user_id or "").strip():
                    return _json_response(self, {"error": "skill does not belong to this session user"}, status=403)

                deleted = bool(manager.sdk.delete(skill_id))
                if not deleted:
                    return _json_response(self, {"error": "delete failed"}, status=500)
                return _json_response(self, {"ok": True, "deleted": True, "skill_id": skill_id})

            return _json_response(self, {"error": "unknown endpoint"}, status=404)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoSkill local web UI")
    parser.add_argument("--host", default=_env("AUTOSKILL_WEB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(_env("AUTOSKILL_WEB_PORT", "8000")))

    parser.add_argument(
        "--llm-provider",
        default=_pick_default_provider(),
        help="mock|generic|glm|internlm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=None)
    parser.add_argument(
        "--embeddings-provider",
        default="",
        help="hashing|generic|glm|dashscope|openai (default depends on llm)",
    )
    parser.add_argument("--embeddings-model", default=None)
    default_store_dir = _env(
        "AUTOSKILL_STORE_DIR",
        _env("AUTOSKILL_STORE_PATH", default_store_path()),
    )
    parser.add_argument("--store-dir", dest="store_dir", default=default_store_dir)
    parser.add_argument("--user-id", default=_env("AUTOSKILL_USER_ID", "u1"))
    parser.add_argument(
        "--skill-scope",
        default=_env("AUTOSKILL_SKILL_SCOPE", "all"),
        help="user|common|all (common==shared library).",
    )
    parser.add_argument(
        "--rewrite-mode",
        default=_env("AUTOSKILL_REWRITE_MODE", "always"),
        help="auto|always|never.",
    )
    parser.add_argument(
        "--extract-mode",
        default=_env("AUTOSKILL_EXTRACT_MODE", "auto"),
        help="auto|always|never.",
    )
    parser.add_argument(
        "--extract-turn-limit",
        type=int,
        default=int(_env("AUTOSKILL_EXTRACT_TURN_LIMIT", "1")),
        help="In auto mode, attempt extraction once every N turns (N=extract_turn_limit).",
    )
    parser.add_argument(
        "--gating-mode",
        default=_env("AUTOSKILL_GATING_MODE", "llm"),
        help="Deprecated (extraction gating is integrated into the extractor).",
    )
    parser.add_argument("--min-score", type=float, default=float(_env("AUTOSKILL_MIN_SCORE", "0.4")))
    parser.add_argument("--top-k", type=int, default=int(_env("AUTOSKILL_TOP_K", "1")))
    parser.add_argument("--library-dir", action="append", default=[], help="Additional read-only library root.")
    args = parser.parse_args()

    interactive_cfg = InteractiveConfig(
        store_dir=str(args.store_dir),
        user_id=str(args.user_id),
        skill_scope=str(args.skill_scope),
        rewrite_mode=str(args.rewrite_mode),
        extract_mode=str(args.extract_mode),
        extract_turn_limit=int(args.extract_turn_limit),
        min_score=float(args.min_score),
        top_k=int(args.top_k),
    ).normalize()

    llm_provider = str(args.llm_provider or "mock").lower()
    llm_cfg = build_llm_config(llm_provider, model=args.llm_model)
    emb_cfg = build_embeddings_config(
        str(args.embeddings_provider),
        model=args.embeddings_model,
        llm_provider=llm_provider,
    )

    env_libs = _env("AUTOSKILL_LIBRARY_DIRS", "").strip()
    library_dirs = list(args.library_dir or [])
    if env_libs:
        library_dirs.extend([p.strip() for p in env_libs.split(",") if p.strip()])

    store_cfg: Dict[str, Any] = {"provider": "local", "path": interactive_cfg.store_dir}
    if library_dirs:
        store_cfg["libraries"] = library_dirs

    sdk = AutoSkill(
        AutoSkillConfig(
            llm=llm_cfg,
            embeddings=emb_cfg,
            store=store_cfg,
            maintenance_strategy=("llm" if llm_provider != "mock" else "heuristic"),
        )
    )

    chat_llm = None if llm_provider == "mock" else build_llm(llm_cfg)

    query_rewriter = None
    if llm_provider != "mock":
        rewrite_cfg = dict(llm_cfg)
        if str(rewrite_cfg.get("provider") or "").lower() in {"glm", "bigmodel", "zhipu"}:
            try:
                rewrite_cfg["max_tokens"] = min(int(rewrite_cfg.get("max_tokens", 30000)), 30000)
            except Exception:
                rewrite_cfg["max_tokens"] = 30000
        query_rewriter = LLMQueryRewriter(build_llm(rewrite_cfg))

    manager = _SessionManager(
        sdk=sdk,
        interactive_cfg=interactive_cfg,
        chat_llm=chat_llm,
        query_rewriter=query_rewriter,
        llm_config=llm_cfg,
    )

    handler_cls = make_handler(manager)
    server = ThreadingHTTPServer((str(args.host), int(args.port)), handler_cls)
    host, port = server.server_address[:2]
    print(f"AutoSkill Web UI: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
