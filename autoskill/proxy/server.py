"""
OpenAI-compatible reverse proxy server for AutoSkill.

Goals:
- expose a standard API surface (`/v1/chat/completions`, `/v1/embeddings`)
- keep client integration simple (reuse existing OpenAI SDK callers)
- transparently add AutoSkill retrieval + asynchronous skill evolution
"""

from __future__ import annotations

import base64
import io
import json
import os
import tempfile
import threading
import time
import uuid
import zipfile
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from ..client import AutoSkill
from ..embeddings.base import EmbeddingModel
from ..embeddings.factory import build_embeddings
from ..interactive.rewriting import LLMQueryRewriter
from ..interactive.selection import LLMSkillSelector
from ..llm.base import LLM
from ..llm.factory import build_llm
from ..models import Skill, SkillExample
from ..render import render_skills_context, select_skills_for_context
from ..skill_management.formats.agent_skill import parse_agent_skill_md, upsert_skill_md_metadata
from ..skill_management.stores.local import LocalSkillStore
from ..utils.time import now_iso

_HISTORY_KEY = "_autoskill_version_history"
_HISTORY_LIMIT = 30
_EXTRACT_EVENT_LIMIT = 200
_EXTRACT_TERMINAL = {"completed", "failed"}


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


def _safe_float(v: Any, default: float) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)


def _safe_int(v: Any, default: Optional[int]) -> Optional[int]:
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default


def _safe_optional_bool(v: Any) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if not s:
        return None
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return None


def _normalize_scope(scope: str) -> str:
    s = str(scope or "all").strip().lower()
    if s == "common":
        s = "library"
    if s not in {"all", "user", "library"}:
        s = "all"
    return s


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


def _parse_bool(v: Any, *, default: bool = False) -> bool:
    if v is None:
        return bool(default)
    s = str(v).strip().lower()
    if not s:
        return bool(default)
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _q_first(qs: Dict[str, List[str]], key: str, default: str = "") -> str:
    vals = qs.get(key) or []
    if not vals:
        return str(default or "")
    return str(vals[0] or "")


def _decode_jwt_payload_no_verify(token: str) -> Dict[str, Any]:
    """
    Best-effort JWT payload decode (without signature verification).

    Used only for lightweight user-id routing when caller does not provide
    explicit `user` or `X-AutoSkill-User`.
    """

    tok = str(token or "").strip()
    if not tok:
        return {}
    parts = tok.split(".")
    if len(parts) < 2:
        return {}
    payload_b64 = str(parts[1] or "").strip()
    if not payload_b64:
        return {}
    payload_b64 += "=" * (-len(payload_b64) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
        if not raw or len(raw) > 65536:
            return {}
        obj = json.loads(raw.decode("utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _user_id_from_auth_jwt(headers: Any) -> str:
    auth = str(headers.get("Authorization") or "").strip()
    if not auth:
        return ""
    if not auth.lower().startswith("bearer "):
        return ""
    token = auth[7:].strip()
    if not token:
        return ""
    payload = _decode_jwt_payload_no_verify(token)
    uid = str(payload.get("id") or "").strip()
    return uid


def _examples_to_raw(examples: List[SkillExample]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for ex in examples or []:
        out.append(
            {
                "input": str(getattr(ex, "input", "") or ""),
                "output": (str(getattr(ex, "output", "")) if getattr(ex, "output", None) is not None else None),
                "notes": (str(getattr(ex, "notes", "")) if getattr(ex, "notes", None) is not None else None),
            }
        )
    return out


def _examples_from_raw(raw: Any) -> List[SkillExample]:
    out: List[SkillExample] = []
    if not isinstance(raw, list):
        return out
    for item in raw[:50]:
        if not isinstance(item, dict):
            continue
        inp = str(item.get("input") or "").strip()
        if not inp:
            continue
        out.append(
            SkillExample(
                input=inp,
                output=(str(item.get("output")).strip() if item.get("output") else None),
                notes=(str(item.get("notes")).strip() if item.get("notes") else None),
            )
        )
    return out


def _metadata_without_history(metadata: Dict[str, Any]) -> Dict[str, Any]:
    md = dict(metadata or {})
    md.pop(_HISTORY_KEY, None)
    return md


def _make_skill_snapshot(skill: Skill) -> Dict[str, Any]:
    files = dict(getattr(skill, "files", {}) or {})
    return {
        "version": str(getattr(skill, "version", "") or ""),
        "name": str(getattr(skill, "name", "") or ""),
        "description": str(getattr(skill, "description", "") or ""),
        "instructions": str(getattr(skill, "instructions", "") or ""),
        "tags": [str(t).strip() for t in (getattr(skill, "tags", []) or []) if str(t).strip()],
        "triggers": [str(t).strip() for t in (getattr(skill, "triggers", []) or []) if str(t).strip()],
        "examples": _examples_to_raw(list(getattr(skill, "examples", []) or [])),
        "skill_md": str(files.get("SKILL.md") or ""),
        "metadata": _metadata_without_history(dict(getattr(skill, "metadata", {}) or {})),
        "source": dict(getattr(skill, "source", {}) or {}) if getattr(skill, "source", None) else None,
        "updated_at": str(getattr(skill, "updated_at", "") or ""),
    }


def _history_from_metadata(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    hist = metadata.get(_HISTORY_KEY)
    if not isinstance(hist, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in hist:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def _push_skill_snapshot(skill: Skill) -> int:
    metadata = dict(getattr(skill, "metadata", {}) or {})
    history = _history_from_metadata(metadata)
    history.append(_make_skill_snapshot(skill))
    if len(history) > int(_HISTORY_LIMIT):
        history = history[-int(_HISTORY_LIMIT) :]
    metadata[_HISTORY_KEY] = history
    skill.metadata = metadata
    return len(history)


def _pop_skill_snapshot(skill: Skill) -> Optional[Dict[str, Any]]:
    metadata = dict(getattr(skill, "metadata", {}) or {})
    history = _history_from_metadata(metadata)
    if not history:
        return None
    snapshot = dict(history[-1])
    history = history[:-1]
    metadata[_HISTORY_KEY] = history
    skill.metadata = metadata
    return snapshot


def _apply_snapshot(skill: Skill, snapshot: Dict[str, Any]) -> None:
    skill.version = str(snapshot.get("version") or str(getattr(skill, "version", "0.1.0")))
    skill.name = str(snapshot.get("name") or str(getattr(skill, "name", "")))
    skill.description = str(snapshot.get("description") or str(getattr(skill, "description", "")))
    skill.instructions = str(snapshot.get("instructions") or str(getattr(skill, "instructions", "")))

    tags = snapshot.get("tags")
    if isinstance(tags, list):
        skill.tags = [str(t).strip() for t in tags if str(t).strip()]

    triggers = snapshot.get("triggers")
    if isinstance(triggers, list):
        skill.triggers = [str(t).strip() for t in triggers if str(t).strip()]

    examples = snapshot.get("examples")
    if isinstance(examples, list):
        skill.examples = _examples_from_raw(examples)

    files = dict(getattr(skill, "files", {}) or {})
    skill_md = snapshot.get("skill_md")
    if skill_md is not None:
        files["SKILL.md"] = str(skill_md)
    skill.files = files

    md_saved = snapshot.get("metadata")
    if isinstance(md_saved, dict):
        current_history = _history_from_metadata(dict(getattr(skill, "metadata", {}) or {}))
        new_md = dict(md_saved)
        new_md[_HISTORY_KEY] = current_history
        skill.metadata = new_md

    src = snapshot.get("source")
    if src is not None:
        skill.source = dict(src) if isinstance(src, dict) else None


def _is_library_skill(skill: Skill) -> bool:
    owner = str(getattr(skill, "user_id", "") or "").strip().lower()
    return owner.startswith("library:")


def _skill_source_label(skill: Skill) -> str:
    owner = str(getattr(skill, "user_id", "") or "").strip()
    if owner.startswith("library:"):
        return owner
    if owner:
        return f"user:{owner}"
    return "user"


def _format_retrieval_hit(hit: Any, *, rank: int) -> Dict[str, Any]:
    skill = getattr(hit, "skill", None)
    score = float(getattr(hit, "score", 0.0) or 0.0)
    if skill is None:
        return {"rank": int(rank), "score": score}
    summary = _skill_summary(skill)
    return {
        "rank": int(rank),
        "score": score,
        "id": str(getattr(skill, "id", "") or ""),
        "name": str(getattr(skill, "name", "") or ""),
        "description": str(getattr(skill, "description", "") or ""),
        "source": _skill_source_label(skill),
        "owner": str(getattr(skill, "user_id", "") or ""),
        "version": str(getattr(skill, "version", "") or ""),
        "skill": summary,
    }


def _skill_summary(skill: Skill) -> Dict[str, Any]:
    return {
        "id": str(skill.id),
        "name": str(skill.name),
        "description": str(skill.description),
        "version": str(skill.version),
        "owner": str(skill.user_id),
        "tags": [str(t) for t in (skill.tags or [])],
        "triggers": [str(t) for t in (skill.triggers or [])],
        "updated_at": str(skill.updated_at or ""),
    }


def _skill_detail(skill: Skill, *, include_md: bool) -> Dict[str, Any]:
    files = dict(skill.files or {})
    out = {
        **_skill_summary(skill),
        "instructions": str(skill.instructions),
        "examples": _examples_to_raw(list(skill.examples or [])),
        "metadata": dict(skill.metadata or {}),
        "source": (dict(skill.source or {}) if skill.source else None),
    }
    if include_md:
        out["skill_md"] = str(files.get("SKILL.md") or "")
    return out


def _candidate_detail(candidate: Any) -> Dict[str, Any]:
    return {
        "name": str(getattr(candidate, "name", "") or ""),
        "description": str(getattr(candidate, "description", "") or ""),
        "instructions": str(getattr(candidate, "instructions", "") or ""),
        "triggers": [str(t) for t in (getattr(candidate, "triggers", []) or []) if str(t).strip()],
        "tags": [str(t) for t in (getattr(candidate, "tags", []) or []) if str(t).strip()],
        "examples": _examples_to_raw(list(getattr(candidate, "examples", []) or [])),
        "confidence": float(getattr(candidate, "confidence", 0.0) or 0.0),
        "source": (dict(getattr(candidate, "source", {}) or {}) if getattr(candidate, "source", None) else None),
    }


def _skill_versions(skill: Skill) -> List[Dict[str, Any]]:
    versions: List[Dict[str, Any]] = []
    hist = _history_from_metadata(dict(skill.metadata or {}))
    for item in hist:
        versions.append(
            {
                "version": str(item.get("version") or ""),
                "name": str(item.get("name") or ""),
                "description": str(item.get("description") or ""),
                "updated_at": str(item.get("updated_at") or ""),
                "is_current": False,
            }
        )
    versions.append(
        {
            "version": str(skill.version or ""),
            "name": str(skill.name or ""),
            "description": str(skill.description or ""),
            "updated_at": str(skill.updated_at or ""),
            "is_current": True,
        }
    )
    return versions


def _safe_extract_zip(zip_path: str, out_dir: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            name = str(info.filename or "")
            if not name or name.endswith("/") or "__MACOSX" in name:
                continue
            rel = os.path.normpath(name).replace("\\", "/")
            if rel.startswith("../") or rel.startswith("/"):
                continue
            dst = os.path.join(out_dir, rel)
            dst_abs = os.path.abspath(dst)
            out_abs = os.path.abspath(out_dir) + os.sep
            if not dst_abs.startswith(out_abs):
                continue
            os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
            with zf.open(info, "r") as src, open(dst_abs, "wb") as out:
                out.write(src.read())


def _latest_user_query(messages: List[Dict[str, str]]) -> str:
    for m in reversed(messages):
        if str(m.get("role") or "").strip().lower() == "user":
            q = str(m.get("content") or "").strip()
            if q:
                return q
    for m in reversed(messages):
        q = str(m.get("content") or "").strip()
        if q:
            return q
    return ""


def _format_history(messages: List[Dict[str, str]], *, max_turns: int) -> str:
    if not messages:
        return ""
    max_msgs = max(0, int(max_turns)) * 2
    window = messages[-max_msgs:] if max_msgs else messages
    lines: List[str] = []
    for m in window:
        role = str(m.get("role") or "").strip().lower()
        content = str(m.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            lines.append(f"User: {content}")
        elif role == "assistant":
            lines.append(f"Assistant: {content}")
        elif role == "system":
            lines.append(f"System: {content}")
        else:
            lines.append(f"{role.title()}: {content}")
    return "\n".join(lines).strip()


def _extract_base_system(messages: List[Dict[str, str]]) -> str:
    parts: List[str] = []
    for m in messages:
        if str(m.get("role") or "").strip().lower() != "system":
            continue
        text = str(m.get("content") or "").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip()


def _openai_error(message: str, *, code: str = "bad_request", err_type: str = "invalid_request_error") -> Dict[str, Any]:
    return {
        "error": {
            "message": str(message),
            "type": str(err_type),
            "param": None,
            "code": str(code),
        }
    }


def _json_response(handler: BaseHTTPRequestHandler, payload: Any, *, status: int = 200) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        handler.send_response(int(status))
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)
    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
        # Client closed the connection before receiving the full response.
        # This is expected for interrupted/cancelled requests and should not crash logs.
        try:
            handler.close_connection = True
        except Exception:
            pass


def _read_json(handler: BaseHTTPRequestHandler, *, max_bytes: int = 10_000_000) -> Dict[str, Any]:
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


@dataclass
class AutoSkillProxyConfig:
    user_id: str = "u1"
    skill_scope: str = "all"  # user|library|all
    rewrite_mode: str = "always"  # never|auto|always
    min_score: float = 0.4
    top_k: int = 1
    history_turns: int = 20
    assistant_temperature: float = 0.2
    extract_enabled: bool = True
    ingest_window: int = 6
    max_bg_extract_jobs: int = 2
    extract_event_include_skill_details: bool = True
    # 0 means no truncation (preferred for editable UI workflows).
    extract_event_max_md_chars: int = 0
    proxy_api_key: Optional[str] = None

    def normalize(self) -> "AutoSkillProxyConfig":
        self.user_id = str(self.user_id or "u1").strip() or "u1"
        self.skill_scope = _normalize_scope(self.skill_scope)
        mode = str(self.rewrite_mode or "always").strip().lower()
        if mode not in {"never", "auto", "always"}:
            mode = "always"
        self.rewrite_mode = mode
        self.min_score = _safe_float(self.min_score, 0.4)
        self.top_k = max(1, int(self.top_k or 1))
        self.history_turns = max(1, int(self.history_turns or 20))
        self.ingest_window = max(2, int(self.ingest_window or 6))
        self.max_bg_extract_jobs = max(1, int(self.max_bg_extract_jobs or 2))
        self.extract_event_include_skill_details = bool(self.extract_event_include_skill_details)
        self.extract_event_max_md_chars = max(0, int(self.extract_event_max_md_chars or 0))
        self.assistant_temperature = _safe_float(self.assistant_temperature, 0.2)
        key = str(self.proxy_api_key or "").strip()
        self.proxy_api_key = key or None
        return self


@dataclass
class _PreparedChat:
    model: str
    temperature: float
    max_tokens: Optional[int]
    thinking_mode: Optional[bool]
    user_id: str
    normalized_messages: List[Dict[str, str]]
    system_prompt: str
    user_prompt: str
    retrieval: Dict[str, Any]
    trigger: str


@dataclass
class _ProxyExtractJob:
    job_id: str
    user_id: str
    window: List[Dict[str, str]]
    trigger: str
    hint: Optional[str]
    retrieval_reference: Optional[Dict[str, Any]] = None


class AutoSkillProxyRuntime:
    """
    Runtime container for the OpenAI-compatible proxy.

    One runtime can serve many requests concurrently.
    """

    def __init__(
        self,
        *,
        sdk: AutoSkill,
        llm_config: Dict[str, Any],
        embeddings_config: Dict[str, Any],
        config: Optional[AutoSkillProxyConfig] = None,
        query_rewriter: Optional[LLMQueryRewriter] = None,
        skill_selector: Optional[LLMSkillSelector] = None,
    ) -> None:
        self.sdk = sdk
        self.llm_config = dict(llm_config or {})
        self.embeddings_config = dict(embeddings_config or {})
        self.config = (config or AutoSkillProxyConfig()).normalize()
        self.skill_selector = skill_selector
        self._extract_sema = threading.BoundedSemaphore(self.config.max_bg_extract_jobs)
        self._extract_sched_lock = threading.Lock()
        self._extract_running_users: set[str] = set()
        # Per-user FIFO queue for extraction jobs that arrive while a user already has a running worker.
        self._extract_queued_by_user: Dict[str, List[_ProxyExtractJob]] = {}
        self._extract_events_lock = threading.Lock()
        self._extract_events_by_user: Dict[str, List[Dict[str, Any]]] = {}
        self._extract_latest_by_job: Dict[str, Dict[str, Any]] = {}

        self._base_embeddings = build_embeddings(self.embeddings_config)

        if query_rewriter is not None:
            self.query_rewriter = query_rewriter
        else:
            provider = str(self.llm_config.get("provider") or "mock").lower()
            if provider == "mock" or self.config.rewrite_mode == "never":
                self.query_rewriter = None
            else:
                self.query_rewriter = LLMQueryRewriter(build_llm(dict(self.llm_config)))

    def make_handler(self) -> type[BaseHTTPRequestHandler]:
        runtime = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "AutoSkillProxy/0.1"

            def log_message(self, format: str, *args: Any) -> None:
                msg = str(format or "") % args
                print(f"[proxy] {msg}")

            def _authorized(self) -> bool:
                expected = runtime.config.proxy_api_key
                if not expected:
                    return True
                auth = str(self.headers.get("Authorization") or "").strip()
                token = ""
                if auth.lower().startswith("bearer "):
                    token = auth[7:].strip()
                if token == expected:
                    return True
                _json_response(
                    self,
                    _openai_error("Unauthorized", code="invalid_api_key"),
                    status=401,
                )
                return False

            def _read_body_safely(self) -> Dict[str, Any]:
                try:
                    return _read_json(self)
                except Exception as e:
                    _json_response(
                        self,
                        _openai_error(str(e), code="invalid_json"),
                        status=400,
                    )
                    return {"_error": True}

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"
                qs = parse_qs(parsed.query or "", keep_blank_values=False)

                if path == "/health" or path == "/api/health":
                    return _json_response(self, {"ok": True})

                if path.startswith("/v1/") and not self._authorized():
                    return

                if path == "/v1/models":
                    model = str(runtime.llm_config.get("model") or "autoskill-model")
                    payload = {
                        "object": "list",
                        "data": [
                            {
                                "id": model,
                                "object": "model",
                                "created": int(time.time()),
                                "owned_by": "autoskill-proxy",
                            }
                        ],
                    }
                    return _json_response(self, payload)

                if path in {"/openapi.json", "/v1/autoskill/openapi.json"}:
                    return _json_response(self, runtime.openapi_spec())

                if path == "/v1/autoskill/capabilities":
                    return _json_response(self, runtime.capabilities())

                if path == "/v1/autoskill/skills":
                    user_id = runtime._resolve_user_id(body={}, headers=self.headers)
                    user_q = _q_first(qs, "user", "")
                    if user_q.strip():
                        user_id = user_q.strip()
                    limit = _safe_int(_q_first(qs, "limit", "200"), 200) or 200
                    limit = max(1, min(1000, int(limit)))
                    skills = runtime.sdk.list(user_id=user_id)[:limit]
                    return _json_response(
                        self,
                        {
                            "object": "list",
                            "data": [_skill_summary(s) for s in skills],
                            "user": user_id,
                        },
                    )

                if path.startswith("/v1/autoskill/skills/"):
                    skill_id, tail = runtime._parse_skill_path(path)
                    if not skill_id:
                        return _json_response(
                            self,
                            _openai_error("Invalid skill path", code="invalid_request"),
                            status=400,
                        )
                    if tail in {"", "/"}:
                        skill = runtime.sdk.get(skill_id)
                        if skill is None:
                            return _json_response(
                                self,
                                _openai_error("Skill not found", code="not_found"),
                                status=404,
                            )
                        include_md = _parse_bool(_q_first(qs, "include_md", "0"), default=False)
                        return _json_response(self, {"object": "skill", "data": _skill_detail(skill, include_md=include_md)})
                    if tail == "/md":
                        skill = runtime.sdk.get(skill_id)
                        if skill is None:
                            return _json_response(
                                self,
                                _openai_error("Skill not found", code="not_found"),
                                status=404,
                            )
                        md = runtime.sdk.export_skill_md(skill_id) or ""
                        return _json_response(
                            self,
                            {
                                "object": "skill_md",
                                "skill_id": skill_id,
                                "name": skill.name,
                                "version": skill.version,
                                "skill_md": md,
                            },
                        )
                    if tail == "/versions":
                        skill = runtime.sdk.get(skill_id)
                        if skill is None:
                            return _json_response(
                                self,
                                _openai_error("Skill not found", code="not_found"),
                                status=404,
                            )
                        return _json_response(
                            self,
                            {
                                "object": "list",
                                "skill_id": skill_id,
                                "name": skill.name,
                                "data": _skill_versions(skill),
                            },
                        )
                    if tail == "/export":
                        try:
                            payload = runtime.export_skill_api(path=path, query=qs)
                        except Exception as e:
                            return _json_response(
                                self,
                                _openai_error(str(e), code="invalid_request"),
                                status=400,
                            )
                        code = int(payload.pop("_status", 200))
                        return _json_response(self, payload, status=code)

                if path == "/v1/autoskill/vectors/status":
                    user_id = runtime._resolve_user_id(body={}, headers=self.headers)
                    user_q = _q_first(qs, "user", "")
                    if user_q.strip():
                        user_id = user_q.strip()
                    scope = _normalize_scope(_q_first(qs, "scope", runtime._resolve_scope(headers=self.headers)))
                    try:
                        payload = runtime.vector_status_api(user_id=user_id, scope=scope)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    code = int(payload.pop("_status", 200))
                    return _json_response(self, payload, status=code)

                if path == "/v1/autoskill/extractions/latest":
                    user_id = runtime._resolve_user_id(body={}, headers=self.headers)
                    user_q = _q_first(qs, "user", "")
                    if user_q.strip():
                        user_id = user_q.strip()
                    ev = runtime._get_latest_extraction_event(user_id=user_id)
                    return _json_response(self, {"object": "extraction_event", "data": ev})

                if path == "/v1/autoskill/extractions":
                    user_id = runtime._resolve_user_id(body={}, headers=self.headers)
                    user_q = _q_first(qs, "user", "")
                    if user_q.strip():
                        user_id = user_q.strip()
                    limit = _safe_int(_q_first(qs, "limit", "20"), 20) or 20
                    limit = max(1, min(200, int(limit)))
                    events = runtime._list_extraction_events(user_id=user_id, limit=limit)
                    return _json_response(self, {"object": "list", "data": events})

                if path.startswith("/v1/autoskill/extractions/"):
                    rest = str(path.split("/v1/autoskill/extractions/", 1)[1] or "").strip().strip("/")
                    if rest.endswith("/events"):
                        job_id = str(rest[: -len("/events")] or "").strip().strip("/")
                        if not job_id:
                            return _json_response(
                                self,
                                _openai_error("Missing job_id", code="invalid_request"),
                                status=400,
                            )
                        timeout_s = _safe_float(_q_first(qs, "timeout_s", "30"), 30.0)
                        return runtime.stream_extraction_events(
                            self,
                            job_id=job_id,
                            timeout_s=max(1.0, min(300.0, float(timeout_s))),
                        )
                    job_id = rest
                    if not job_id:
                        return _json_response(
                            self,
                            _openai_error("Missing job_id", code="invalid_request"),
                            status=400,
                        )
                    ev = runtime._get_extraction_event_by_job(job_id=job_id)
                    if ev is None:
                        return _json_response(
                            self,
                            _openai_error("Extraction job not found", code="not_found"),
                            status=404,
                        )
                    return _json_response(self, {"object": "extraction_event", "data": ev})

                self.send_response(404)
                self.end_headers()

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"
                if path.startswith("/v1/") and not self._authorized():
                    return
                body = self._read_body_safely()
                if body.get("_error"):
                    return

                if path == "/v1/chat/completions":
                    stream = bool(body.get("stream"))
                    try:
                        prepared = runtime.prepare_chat(
                            body=body,
                            headers=self.headers,
                        )
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    extraction_job_id: Optional[str] = None
                    extraction_status = "disabled"
                    extraction_window = runtime._build_auto_extraction_window(
                        prepared.normalized_messages
                    )
                    if extraction_window:
                        top_ref = runtime._top_reference_from_retrieval_hits(
                            retrieval_hits=list((prepared.retrieval or {}).get("hits") or []),
                            user_id=prepared.user_id,
                        )
                        extraction_job_id = runtime._schedule_extraction_job(
                            user_id=prepared.user_id,
                            messages=extraction_window,
                            trigger=prepared.trigger,
                            retrieval_reference=top_ref,
                        )
                        ev = runtime._get_extraction_event_by_job(job_id=extraction_job_id)
                        extraction_status = str((ev or {}).get("status") or "scheduled")
                    if stream:
                        return runtime.stream_chat_completion(
                            self,
                            prepared=prepared,
                            extraction_job_id=extraction_job_id,
                            extraction_status=extraction_status,
                        )
                    try:
                        payload = runtime.complete_chat_completion(
                            prepared=prepared,
                            extraction_job_id=extraction_job_id,
                            extraction_status=extraction_status,
                        )
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="upstream_error"),
                            status=500,
                        )
                    return _json_response(self, payload)

                if path == "/v1/embeddings":
                    try:
                        payload = runtime.create_embeddings(body=body)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="upstream_error"),
                            status=500,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/skills/search":
                    try:
                        payload = runtime.search_skills_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                    )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/retrieval/preview":
                    try:
                        payload = runtime.retrieval_preview_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/extractions":
                    try:
                        payload = runtime.extract_now_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                    )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/extractions/simulate":
                    try:
                        payload = runtime.simulate_extraction_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/skills/import":
                    try:
                        payload = runtime.import_skills_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    code = int(payload.pop("_status", 200))
                    return _json_response(self, payload, status=code)

                if path.startswith("/v1/autoskill/skills/") and path.endswith("/rollback"):
                    try:
                        payload = runtime.rollback_skill_api(path=path, body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    code = int(payload.pop("_status", 200))
                    return _json_response(self, payload, status=code)

                if path == "/v1/autoskill/vectors/rebuild":
                    try:
                        payload = runtime.vector_rebuild_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    code = int(payload.pop("_status", 200))
                    return _json_response(self, payload, status=code)

                return _json_response(
                    self,
                    _openai_error("Unknown endpoint", code="not_found"),
                    status=404,
                )

            def do_PUT(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"
                if path.startswith("/v1/") and not self._authorized():
                    return
                body = self._read_body_safely()
                if body.get("_error"):
                    return
                if path.startswith("/v1/autoskill/skills/") and path.endswith("/md"):
                    try:
                        payload = runtime.save_skill_md_api(path=path, body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    code = int(payload.pop("_status", 200))
                    return _json_response(self, payload, status=code)
                return _json_response(
                    self,
                    _openai_error("Unknown endpoint", code="not_found"),
                    status=404,
                )

            def do_DELETE(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"
                if path.startswith("/v1/") and not self._authorized():
                    return
                if path.startswith("/v1/autoskill/skills/"):
                    try:
                        payload = runtime.delete_skill_api(path=path, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    code = int(payload.pop("_status", 200))
                    return _json_response(self, payload, status=code)
                return _json_response(
                    self,
                    _openai_error("Unknown endpoint", code="not_found"),
                    status=404,
                )

        return Handler

    def create_server(self, *, host: str, port: int) -> ThreadingHTTPServer:
        handler = self.make_handler()
        return ThreadingHTTPServer((str(host), int(port)), handler)

    def capabilities(self) -> Dict[str, Any]:
        return {
            "object": "autoskill.capabilities",
            "data": {
                "llm": self._runtime_llm_info(),
                "chat": {"path": "/v1/chat/completions", "stream": True},
                "embeddings": {"path": "/v1/embeddings"},
                "skills": {
                    "list": "/v1/autoskill/skills",
                    "get": "/v1/autoskill/skills/{skill_id}",
                    "get_md": "/v1/autoskill/skills/{skill_id}/md",
                    "save_md": "/v1/autoskill/skills/{skill_id}/md",
                    "delete": "/v1/autoskill/skills/{skill_id}",
                    "rollback": "/v1/autoskill/skills/{skill_id}/rollback",
                    "versions": "/v1/autoskill/skills/{skill_id}/versions",
                    "export": "/v1/autoskill/skills/{skill_id}/export",
                    "search": "/v1/autoskill/skills/search",
                    "import": "/v1/autoskill/skills/import",
                },
                "retrieval": {"preview": "/v1/autoskill/retrieval/preview"},
                "extractions": {
                    "extract_now": "/v1/autoskill/extractions",
                    "simulate": "/v1/autoskill/extractions/simulate",
                    "latest": "/v1/autoskill/extractions/latest",
                    "list": "/v1/autoskill/extractions",
                    "get": "/v1/autoskill/extractions/{job_id}",
                    "events_stream": "/v1/autoskill/extractions/{job_id}/events",
                },
                "vectors": {
                    "status": "/v1/autoskill/vectors/status",
                    "rebuild": "/v1/autoskill/vectors/rebuild",
                },
                "meta": {
                    "capabilities": "/v1/autoskill/capabilities",
                    "openapi": "/v1/autoskill/openapi.json",
                },
            },
        }

    def _runtime_llm_info(self) -> Dict[str, Any]:
        provider = str(self.llm_config.get("provider") or "mock").strip().lower() or "mock"
        model = str(self.llm_config.get("model") or "").strip()
        thinking_supported = provider in {"internlm", "intern", "intern-s1", "intern-s1-pro"}
        requested = _safe_optional_bool(self.llm_config.get("thinking_mode"))
        if thinking_supported and requested is None:
            requested = True
        return {
            "provider": provider,
            "model": model,
            "thinking_mode": {
                "supported": bool(thinking_supported),
                "requested": requested,
            },
        }

    def openapi_spec(self) -> Dict[str, Any]:
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "AutoSkill Proxy API",
                "version": "0.2.0",
                "description": "OpenAI-compatible proxy with skill retrieval/evolution management APIs.",
            },
            "paths": {
                "/v1/chat/completions": {"post": {"summary": "OpenAI-compatible chat"}},
                "/v1/embeddings": {"post": {"summary": "OpenAI-compatible embeddings"}},
                "/v1/models": {"get": {"summary": "List models"}},
                "/v1/autoskill/capabilities": {"get": {"summary": "Discover supported APIs"}},
                "/v1/autoskill/openapi.json": {"get": {"summary": "OpenAPI schema"}},
                "/v1/autoskill/skills": {"get": {"summary": "List user skills"}},
                "/v1/autoskill/skills/{skill_id}": {
                    "get": {"summary": "Get one skill"},
                    "delete": {"summary": "Delete one skill"},
                },
                "/v1/autoskill/skills/{skill_id}/md": {
                    "get": {"summary": "Get SKILL.md"},
                    "put": {"summary": "Update SKILL.md"},
                },
                "/v1/autoskill/skills/{skill_id}/rollback": {
                    "post": {"summary": "Rollback to previous version"},
                },
                "/v1/autoskill/skills/{skill_id}/versions": {"get": {"summary": "List version timeline"}},
                "/v1/autoskill/skills/{skill_id}/export": {"get": {"summary": "Export one skill"}},
                "/v1/autoskill/skills/search": {"post": {"summary": "Search skills"}},
                "/v1/autoskill/skills/import": {"post": {"summary": "Import Agent Skills"}},
                "/v1/autoskill/retrieval/preview": {"post": {"summary": "Preview retrieval pipeline"}},
                "/v1/autoskill/extractions": {
                    "get": {"summary": "List extraction events"},
                    "post": {"summary": "Trigger extraction now"},
                },
                "/v1/autoskill/extractions/latest": {"get": {"summary": "Get latest extraction event"}},
                "/v1/autoskill/extractions/{job_id}": {"get": {"summary": "Get extraction event by job"}},
                "/v1/autoskill/extractions/{job_id}/events": {
                    "get": {"summary": "SSE stream of extraction updates"},
                },
                "/v1/autoskill/extractions/simulate": {"post": {"summary": "Dry-run extraction"}},
                "/v1/autoskill/vectors/status": {"get": {"summary": "Vector index status"}},
                "/v1/autoskill/vectors/rebuild": {"post": {"summary": "Rebuild vector index"}},
            },
        }

    def _retrieve_context(
        self,
        *,
        messages: List[Dict[str, str]],
        user_id: str,
        scope: str,
        limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        latest_user = _latest_user_query(messages)
        search_query = latest_user
        rewritten_query = ""
        retrieval_error: Optional[str] = None
        if (
            self.query_rewriter is not None
            and self.config.rewrite_mode in {"always", "auto"}
            and latest_user
        ):
            try:
                rewritten = self.query_rewriter.rewrite(query=latest_user, messages=messages)
            except Exception:
                rewritten = ""
            if rewritten and rewritten.strip():
                rewritten_query = rewritten.strip()
                search_query = rewritten_query

        lim = max(1, int(limit or self.config.top_k))
        min_score_v = float(self.config.min_score if min_score is None else min_score)
        try:
            hits = self.sdk.search(
                search_query,
                user_id=user_id,
                limit=lim,
                filters={"scope": scope, "allow_partial_vectors": False},
            )
        except Exception as e:
            hits = []
            retrieval_error = str(e)
        if hits and min_score_v > 0:
            hits = [h for h in hits if float(getattr(h, "score", 0.0) or 0.0) >= min_score_v]

        retrieval_hits: List[Dict[str, Any]] = []
        for idx, h in enumerate(hits, start=1):
            retrieval_hits.append(_format_retrieval_hit(h, rank=idx))

        skills_for_use = [h.skill for h in hits]
        if self.skill_selector is not None and skills_for_use:
            try:
                selected_for_use = self.skill_selector.select(
                    query=latest_user,
                    messages=messages,
                    skills=skills_for_use,
                )
            except Exception:
                selected_for_use = skills_for_use
            skills_for_use = list(selected_for_use or [])

        selected = select_skills_for_context(
            skills_for_use,
            query=search_query,
            max_chars=self.sdk.config.max_context_chars,
        )
        use_skills = bool(selected)
        context = (
            render_skills_context(
                selected,
                query=search_query,
                max_chars=self.sdk.config.max_context_chars,
            )
            if use_skills
            else ""
        )

        return {
            "original_query": latest_user,
            "latest_user_query": latest_user,
            "search_query": search_query,
            "rewritten_query": rewritten_query,
            "event_time": int(time.time() * 1000),
            "scope": scope,
            "top_k": int(lim),
            "min_score": float(min_score_v),
            "hits": retrieval_hits,
            "selected_for_use_ids": [str(getattr(s, "id", "") or "") for s in skills_for_use],
            "selected_for_context_ids": [str(getattr(s, "id", "") or "") for s in selected],
            "context_injected": bool(use_skills),
            "error": (retrieval_error if retrieval_error else None),
            "selected_skills": selected,
            "selected_summaries": [_skill_summary(s) for s in selected],
            "context": context,
            # Compatibility aliases expected by existing proxy consumers.
            "query": latest_user,
        }

    def _retrieval_response_payload(self, retrieval: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a JSON-safe retrieval payload aligned with interactive session schema.
        """

        out = {
            "original_query": str(retrieval.get("original_query") or retrieval.get("latest_user_query") or ""),
            "rewritten_query": (
                str(retrieval.get("rewritten_query") or "").strip() or None
            ),
            "search_query": str(retrieval.get("search_query") or ""),
            "event_time": int(retrieval.get("event_time") or int(time.time() * 1000)),
            "scope": str(retrieval.get("scope") or ""),
            "top_k": int(
                retrieval["top_k"] if retrieval.get("top_k") is not None else self.config.top_k
            ),
            "min_score": float(
                retrieval["min_score"] if retrieval.get("min_score") is not None else self.config.min_score
            ),
            "hits": list(retrieval.get("hits") or []),
            "selected_for_use_ids": [str(x) for x in (retrieval.get("selected_for_use_ids") or [])],
            "selected_for_context_ids": [str(x) for x in (retrieval.get("selected_for_context_ids") or [])],
            "context_injected": bool(retrieval.get("context_injected")),
            "error": (str(retrieval.get("error")) if retrieval.get("error") else None),
        }
        # Backward-compatible aliases.
        out["query"] = str(out["original_query"])
        out["latest_user_query"] = str(out["original_query"])
        out["selected_skills"] = list(retrieval.get("selected_summaries") or [])
        return out

    def prepare_chat(
        self,
        *,
        body: Dict[str, Any],
        headers: Any,
    ) -> _PreparedChat:
        messages = _normalize_messages(body.get("messages"))
        if not messages:
            raise ValueError("messages is required and must contain text messages")

        model = str(body.get("model") or self.llm_config.get("model") or "autoskill-model")
        temperature = _safe_float(body.get("temperature"), self.config.assistant_temperature)
        max_tokens = _safe_int(body.get("max_tokens"), None)
        thinking_mode = _safe_optional_bool(body.get("thinking_mode")) if "thinking_mode" in body else None

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope = self._resolve_scope(headers=headers)
        retrieval = self._retrieve_context(
            messages=messages,
            user_id=user_id,
            scope=scope,
            limit=self.config.top_k,
            min_score=self.config.min_score,
        )
        use_skills = bool(retrieval["selected_skills"])

        system_prompt, user_prompt = self._build_assistant_inputs(
            messages=messages,
            context=str(retrieval["context"] or ""),
            use_skills=use_skills,
        )

        return _PreparedChat(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_mode=thinking_mode,
            user_id=user_id,
            normalized_messages=messages,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            retrieval=self._retrieval_response_payload(retrieval),
            trigger="proxy_chat_completion",
        )

    def complete_chat_completion(
        self,
        *,
        prepared: _PreparedChat,
        extraction_job_id: Optional[str] = None,
        extraction_status: str = "scheduled",
    ) -> Dict[str, Any]:
        chat_llm = self._build_chat_llm(
            model=prepared.model,
            max_tokens=prepared.max_tokens,
            thinking_mode=prepared.thinking_mode,
        )
        text = chat_llm.complete(
            system=prepared.system_prompt,
            user=prepared.user_prompt,
            temperature=float(prepared.temperature),
        )
        content = str(text or "").strip()
        if not content:
            content = "(empty response)"

        created = int(time.time())
        completion_id = f"chatcmpl-{uuid.uuid4().hex}"
        return {
            "id": completion_id,
            "object": "chat.completion",
            "created": created,
            "model": prepared.model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "autoskill": {
                "retrieval": dict(prepared.retrieval or {}),
                "extraction": {
                    "job_id": extraction_job_id,
                    "status": str(extraction_status or ("scheduled" if extraction_job_id else "disabled")),
                },
            },
        }

    def stream_chat_completion(
        self,
        handler: BaseHTTPRequestHandler,
        *,
        prepared: _PreparedChat,
        extraction_job_id: Optional[str] = None,
        extraction_status: str = "scheduled",
    ) -> None:
        created = int(time.time())
        completion_id = f"chatcmpl-{uuid.uuid4().hex}"
        handler.send_response(200)
        handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("Connection", "keep-alive")
        handler.send_header("X-Accel-Buffering", "no")
        handler.end_headers()

        def _send(obj: Dict[str, Any]) -> None:
            data = f"data: {json.dumps(obj, ensure_ascii=False)}\n\n".encode("utf-8")
            handler.wfile.write(data)
            handler.wfile.flush()

        def _done() -> None:
            handler.wfile.write(b"data: [DONE]\n\n")
            handler.wfile.flush()

        try:
            role_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": prepared.model,
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
                "autoskill": {
                    "retrieval": dict(prepared.retrieval or {}),
                    "extraction": {
                        "job_id": extraction_job_id,
                        "status": str(extraction_status or ("scheduled" if extraction_job_id else "disabled")),
                    },
                },
            }
            _send(role_chunk)

            chat_llm = self._build_chat_llm(
                model=prepared.model,
                max_tokens=prepared.max_tokens,
                thinking_mode=prepared.thinking_mode,
            )

            for chunk in chat_llm.stream_complete(
                system=prepared.system_prompt,
                user=prepared.user_prompt,
                temperature=float(prepared.temperature),
            ):
                s = str(chunk or "")
                if not s:
                    continue
                _send(
                    {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": prepared.model,
                        "choices": [{"index": 0, "delta": {"content": s}, "finish_reason": None}],
                    }
                )

            _send(
                {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": prepared.model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                }
            )
            _done()
        except BrokenPipeError:
            return
        except Exception as e:
            try:
                _send(
                    {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": prepared.model,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                        "error": {"message": str(e)},
                    }
                )
                _done()
            except Exception:
                pass

    def create_embeddings(self, *, body: Dict[str, Any]) -> Dict[str, Any]:
        inp = body.get("input")
        model = str(body.get("model") or self.embeddings_config.get("model") or "embedding-model")
        texts = self._normalize_embedding_input(inp)
        if not texts:
            raise ValueError("input is required")

        em = self._build_embeddings_model(model=model)
        vecs = em.embed(texts)
        data = []
        for i, vec in enumerate(vecs):
            data.append({"object": "embedding", "index": i, "embedding": [float(x) for x in (vec or [])]})
        return {
            "object": "list",
            "data": data,
            "model": model,
            "usage": {"prompt_tokens": 0, "total_tokens": 0},
        }

    def search_skills_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        query = str(body.get("query") or body.get("q") or "").strip()
        if not query:
            raise ValueError("query is required")
        user_id = self._resolve_user_id(body=body, headers=headers)
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        limit = _safe_int(body.get("limit"), self.config.top_k) or self.config.top_k
        limit = max(1, min(200, int(limit)))
        min_score = _safe_float(body.get("min_score"), self.config.min_score)

        hits = self.sdk.search(
            query,
            user_id=user_id,
            limit=limit,
            filters={"scope": scope, "allow_partial_vectors": False},
        )
        if hits and min_score > 0:
            hits = [h for h in hits if float(getattr(h, "score", 0.0) or 0.0) >= min_score]

        data: List[Dict[str, Any]] = []
        for i, h in enumerate(hits, start=1):
            data.append(_format_retrieval_hit(h, rank=i))
        return {
            "object": "list",
            "query": query,
            "user": user_id,
            "scope": scope,
            "data": data,
        }

    def retrieval_preview_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        messages = _normalize_messages(body.get("messages"))
        query = str(body.get("query") or body.get("q") or "").strip()
        if not messages and query:
            messages = [{"role": "user", "content": query}]
        if not messages:
            raise ValueError("messages or query is required")

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        limit = _safe_int(body.get("limit"), self.config.top_k) or self.config.top_k
        min_score = _safe_float(body.get("min_score"), self.config.min_score)

        retrieval = self._retrieve_context(
            messages=messages,
            user_id=user_id,
            scope=scope,
            limit=limit,
            min_score=min_score,
        )
        payload = self._retrieval_response_payload(retrieval)
        return {
            "object": "retrieval_preview",
            "user": user_id,
            "scope": scope,
            **payload,
            "context": retrieval["context"],
        }

    def extract_now_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        user_id = self._resolve_user_id(body=body, headers=headers)
        messages = _normalize_messages(body.get("messages"))
        query = str(body.get("query") or "").strip()
        if not messages and query:
            messages = [{"role": "user", "content": query}]
        if not messages:
            raise ValueError("messages or query is required")
        hint_raw = body.get("hint")
        hint = str(hint_raw).strip() if hint_raw is not None and str(hint_raw).strip() else None
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        min_score = _safe_float(body.get("min_score"), self.config.min_score)
        retrieval = self._retrieve_context(
            messages=messages,
            user_id=user_id,
            scope=scope,
            limit=1,
            min_score=min_score,
        )
        top_ref = self._top_reference_from_retrieval_hits(
            retrieval_hits=list(retrieval.get("hits") or []),
            user_id=user_id,
        )

        job_id = self._schedule_extraction_job(
            user_id=user_id,
            messages=messages[-int(self.config.ingest_window) :],
            trigger="proxy_extract_now",
            hint=hint,
            retrieval_reference=top_ref,
        )
        ev = self._get_extraction_event_by_job(job_id=job_id)
        return {
            "object": "extraction_event",
            "data": ev,
        }

    def simulate_extraction_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        user_id = self._resolve_user_id(body=body, headers=headers)
        messages = _normalize_messages(body.get("messages"))
        query = str(body.get("query") or "").strip()
        if not messages and query:
            messages = [{"role": "user", "content": query}]
        if not messages:
            raise ValueError("messages or query is required")
        hint_raw = body.get("hint")
        hint = str(hint_raw).strip() if hint_raw is not None and str(hint_raw).strip() else None

        max_candidates = max(0, min(1, int(self.sdk.config.max_candidates_per_ingest)))
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        min_score = _safe_float(body.get("min_score"), self.config.min_score)
        retrieval = self._retrieve_context(
            messages=messages,
            user_id=user_id,
            scope=scope,
            limit=1,
            min_score=min_score,
        )
        top_ref = self._top_reference_from_retrieval_hits(
            retrieval_hits=list(retrieval.get("hits") or []),
            user_id=user_id,
        )
        extracted = self.sdk.extract_candidates(
            user_id=user_id,
            messages=messages[-int(self.config.ingest_window) :],
            events=None,
            hint=hint,
            max_candidates=max_candidates,
            retrieved_reference=top_ref,
        )
        return {
            "object": "extraction_simulation",
            "user": user_id,
            "count": len(extracted or []),
            "skills": [_candidate_detail(s) for s in (extracted or [])],
        }

    def save_skill_md_api(self, *, path: str, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        skill_id, tail = self._parse_skill_path(path)
        if not skill_id or tail != "/md":
            return {"_status": 400, **_openai_error("Invalid skill md path", code="invalid_request")}

        skill = self.sdk.get(skill_id)
        if skill is None:
            return {"_status": 404, **_openai_error("Skill not found", code="not_found")}

        user_id = self._resolve_user_id(body=body, headers=headers)
        owner_err = self._skill_owner_guard(skill=skill, user_id=user_id)
        if owner_err is not None:
            return owner_err

        md = str(body.get("skill_md") or body.get("md") or "")
        if not md.strip():
            return {"_status": 400, **_openai_error("skill_md is required", code="invalid_request")}

        parsed = parse_agent_skill_md(md)
        name = str(parsed.get("name") or "").strip() or str(skill.name or "").strip()
        if not name:
            return {"_status": 400, **_openai_error("SKILL.md must include non-empty name", code="invalid_request")}

        description = str(parsed.get("description") or "").strip() or str(skill.description or "").strip() or name
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

        examples2 = _examples_from_raw(parsed.get("examples") or [])
        md2 = upsert_skill_md_metadata(md, skill_id=skill_id, name=name, description=description, version=version)

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
            self.sdk.store.upsert(skill, raw=None)
        except Exception as e:
            return {"_status": 500, **_openai_error(str(e), code="upstream_error")}

        return {
            "ok": True,
            "object": "skill",
            "data": _skill_detail(skill, include_md=True),
            "history_count": int(history_size),
        }

    def rollback_skill_api(self, *, path: str, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        skill_id, tail = self._parse_skill_path(path)
        if not skill_id or tail != "/rollback":
            return {"_status": 400, **_openai_error("Invalid rollback path", code="invalid_request")}

        skill = self.sdk.get(skill_id)
        if skill is None:
            return {"_status": 404, **_openai_error("Skill not found", code="not_found")}

        user_id = self._resolve_user_id(body=body, headers=headers)
        owner_err = self._skill_owner_guard(skill=skill, user_id=user_id)
        if owner_err is not None:
            return owner_err

        snapshot = _pop_skill_snapshot(skill)
        if snapshot is None:
            return {"_status": 400, **_openai_error("No previous version available", code="invalid_request")}

        _apply_snapshot(skill, snapshot)
        skill.updated_at = now_iso()
        skill.files = dict(skill.files or {})

        try:
            self.sdk.store.upsert(skill, raw=None)
        except Exception as e:
            return {"_status": 500, **_openai_error(str(e), code="upstream_error")}

        history_count = len(_history_from_metadata(dict(skill.metadata or {})))
        return {
            "ok": True,
            "object": "skill",
            "data": _skill_detail(skill, include_md=True),
            "restored_from": {
                "version": str(snapshot.get("version") or ""),
                "updated_at": str(snapshot.get("updated_at") or ""),
            },
            "history_count": int(history_count),
        }

    def export_skill_api(self, *, path: str, query: Dict[str, List[str]]) -> Dict[str, Any]:
        skill_id, tail = self._parse_skill_path(path)
        if not skill_id or tail != "/export":
            return {"_status": 400, **_openai_error("Invalid skill export path", code="invalid_request")}

        skill = self.sdk.get(skill_id)
        if skill is None:
            return {"_status": 404, **_openai_error("Skill not found", code="not_found")}

        fmt = str(_q_first(query, "format", "files") or "files").strip().lower()
        if fmt in {"md", "skill_md"}:
            md = self.sdk.export_skill_md(skill_id) or ""
            return {
                "object": "skill_export",
                "format": "md",
                "skill_id": skill_id,
                "name": skill.name,
                "version": skill.version,
                "skill_md": md,
            }

        files = self.sdk.export_skill_dir(skill_id) or {}
        if fmt in {"zip", "zip_base64"}:
            bio = io.BytesIO()
            with zipfile.ZipFile(bio, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                for rel, content in files.items():
                    rel2 = str(rel or "").lstrip("/").replace("..", "_")
                    if not rel2:
                        continue
                    zf.writestr(rel2, str(content or ""))
            data_b64 = base64.b64encode(bio.getvalue()).decode("ascii")
            return {
                "object": "skill_export",
                "format": "zip_base64",
                "skill_id": skill_id,
                "name": skill.name,
                "version": skill.version,
                "file_name": f"{skill.name or skill_id}.zip",
                "zip_base64": data_b64,
            }

        return {
            "object": "skill_export",
            "format": "files",
            "skill_id": skill_id,
            "name": skill.name,
            "version": skill.version,
            "files": files,
        }

    def import_skills_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        user_id = self._resolve_user_id(body=body, headers=headers)
        root_dir = str(body.get("root_dir") or "").strip()
        zip_path = str(body.get("zip_path") or "").strip()
        if not root_dir and not zip_path:
            return {
                "_status": 400,
                **_openai_error("root_dir or zip_path is required", code="invalid_request"),
            }

        overwrite = _parse_bool(body.get("overwrite"), default=True)
        include_files = _parse_bool(body.get("include_files"), default=True)
        max_file_bytes = max(1024, int(_safe_int(body.get("max_file_bytes"), 1_000_000) or 1_000_000))
        max_depth = max(1, int(_safe_int(body.get("max_depth"), 6) or 6))
        reassign_ids = _parse_bool(body.get("reassign_ids"), default=True)

        if zip_path:
            abs_zip = os.path.abspath(os.path.expanduser(zip_path))
            if not os.path.isfile(abs_zip):
                return {"_status": 404, **_openai_error("zip_path not found", code="not_found")}
            with tempfile.TemporaryDirectory(prefix="autoskill-import-") as tmp:
                _safe_extract_zip(abs_zip, tmp)
                imported = self.sdk.import_agent_skill_dirs(
                    root_dir=tmp,
                    user_id=user_id,
                    overwrite=overwrite,
                    include_files=include_files,
                    max_file_bytes=max_file_bytes,
                    max_depth=max_depth,
                    reassign_ids=reassign_ids,
                )
        else:
            imported = self.sdk.import_agent_skill_dirs(
                root_dir=root_dir,
                user_id=user_id,
                overwrite=overwrite,
                include_files=include_files,
                max_file_bytes=max_file_bytes,
                max_depth=max_depth,
                reassign_ids=reassign_ids,
            )

        return {
            "ok": True,
            "object": "list",
            "imported_count": len(imported or []),
            "data": [_skill_summary(s) for s in (imported or [])],
        }

    def vector_status_api(self, *, user_id: str, scope: str) -> Dict[str, Any]:
        store = self._local_store()
        if store is None:
            return {
                "_status": 400,
                **_openai_error("vector status is only available for local store", code="unsupported"),
            }
        return {
            "object": "vector_status",
            "data": store.vector_status(user_id=user_id, scope=scope),
        }

    def vector_rebuild_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        store = self._local_store()
        if store is None:
            return {
                "_status": 400,
                **_openai_error("vector rebuild is only available for local store", code="unsupported"),
            }

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        force = _parse_bool(body.get("force"), default=False)
        blocking = _parse_bool(body.get("blocking"), default=True)
        rebuilt = int(store.rebuild_vectors(user_id=user_id, scope=scope, force=force, blocking=blocking))
        return {
            "ok": True,
            "object": "vector_rebuild",
            "data": {
                "user": user_id,
                "scope": scope,
                "force": force,
                "blocking": blocking,
                "rebuilt": rebuilt,
                "status": store.vector_status(user_id=user_id, scope=scope),
            },
        }

    def delete_skill_api(self, *, path: str, headers: Any) -> Dict[str, Any]:
        skill_id, tail = self._parse_skill_path(path)
        if not skill_id or tail not in {"", "/"}:
            return {"_status": 400, **_openai_error("Invalid skill delete path", code="invalid_request")}

        skill = self.sdk.get(skill_id)
        if skill is None:
            return {"_status": 404, **_openai_error("Skill not found", code="not_found")}

        user_id = self._resolve_user_id(body={}, headers=headers)
        owner_err = self._skill_owner_guard(skill=skill, user_id=user_id)
        if owner_err is not None:
            return owner_err

        deleted = bool(self.sdk.delete(skill_id))
        if not deleted:
            return {"_status": 500, **_openai_error("Delete failed", code="upstream_error")}
        return {"ok": True, "deleted": True, "skill_id": skill_id}

    def _parse_skill_path(self, path: str) -> Tuple[str, str]:
        prefix = "/v1/autoskill/skills/"
        raw = str(path or "")
        if not raw.startswith(prefix):
            return "", ""
        rest = raw[len(prefix) :]
        if not rest:
            return "", ""
        if "/" not in rest:
            return rest.strip(), ""
        skill_id, tail = rest.split("/", 1)
        return skill_id.strip(), "/" + tail.strip()

    def _skill_owner_guard(self, *, skill: Skill, user_id: str) -> Optional[Dict[str, Any]]:
        owner = str(getattr(skill, "user_id", "") or "").strip()
        if _is_library_skill(skill):
            return {"_status": 403, **_openai_error("Library skills are read-only", code="forbidden")}
        if owner and owner != str(user_id or "").strip():
            return {"_status": 403, **_openai_error("Skill does not belong to this user", code="forbidden")}
        return None

    def _record_extraction_event(self, *, user_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        uid = str(user_id or "").strip() or self.config.user_id
        ev = dict(event or {})
        ev["user_id"] = uid
        ev["event_time"] = int(ev.get("event_time") or int(time.time() * 1000))
        ev["event_id"] = str(ev.get("event_id") or uuid.uuid4().hex)
        job_id = str(ev.get("job_id") or "").strip()
        if job_id:
            ev["job_id"] = job_id

        with self._extract_events_lock:
            arr = self._extract_events_by_user.get(uid)
            if arr is None:
                arr = []
                self._extract_events_by_user[uid] = arr
            arr.append(ev)
            if len(arr) > int(_EXTRACT_EVENT_LIMIT):
                arr[:] = arr[-int(_EXTRACT_EVENT_LIMIT) :]
            if job_id:
                self._extract_latest_by_job[job_id] = ev
        return dict(ev)

    def _list_extraction_events(self, *, user_id: str, limit: int) -> List[Dict[str, Any]]:
        uid = str(user_id or "").strip() or self.config.user_id
        lim = max(1, min(200, int(limit or 20)))
        with self._extract_events_lock:
            arr = list(self._extract_events_by_user.get(uid) or [])
        return list(reversed(arr[-lim:]))

    def _get_latest_extraction_event(self, *, user_id: str) -> Optional[Dict[str, Any]]:
        uid = str(user_id or "").strip() or self.config.user_id
        with self._extract_events_lock:
            arr = self._extract_events_by_user.get(uid) or []
            if not arr:
                return None
            return dict(arr[-1])

    def _get_extraction_event_by_job(self, *, job_id: str) -> Optional[Dict[str, Any]]:
        jid = str(job_id or "").strip()
        if not jid:
            return None
        with self._extract_events_lock:
            ev = self._extract_latest_by_job.get(jid)
            return dict(ev) if isinstance(ev, dict) else None

    def stream_extraction_events(
        self,
        handler: BaseHTTPRequestHandler,
        *,
        job_id: str,
        timeout_s: float = 30.0,
    ) -> None:
        jid = str(job_id or "").strip()
        if not jid:
            return _json_response(
                handler,
                _openai_error("Missing job_id", code="invalid_request"),
                status=400,
            )

        handler.send_response(200)
        handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("Connection", "keep-alive")
        handler.send_header("X-Accel-Buffering", "no")
        handler.end_headers()

        def _send(event: str, payload: Dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False)
            handler.wfile.write(f"event: {event}\n".encode("utf-8"))
            handler.wfile.write(f"data: {data}\n\n".encode("utf-8"))
            handler.wfile.flush()

        started = time.time()
        last_event_id = ""
        try:
            while (time.time() - started) < float(timeout_s):
                ev = self._get_extraction_event_by_job(job_id=jid)
                if ev is not None:
                    eid = str(ev.get("event_id") or "")
                    if eid and eid != last_event_id:
                        _send("update", ev)
                        last_event_id = eid
                        if str(ev.get("status") or "").strip().lower() in _EXTRACT_TERMINAL:
                            break
                time.sleep(0.2)
            latest = self._get_extraction_event_by_job(job_id=jid)
            if latest is not None:
                _send("done", latest)
            else:
                _send("done", {"job_id": jid, "status": "not_found"})
            handler.wfile.write(b"data: [DONE]\n\n")
            handler.wfile.flush()
        except BrokenPipeError:
            return
        except Exception:
            return

    def _local_store(self) -> Optional[LocalSkillStore]:
        store = getattr(self.sdk, "store", None)
        if isinstance(store, LocalSkillStore):
            return store
        return None

    def _build_auto_extraction_window(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Builds the automatic extraction window for proxy chat requests.

        Semantics are aligned with interactive mode:
        - use the recent ingest window
        - latest message should be user feedback
        - schedule only when the window already contains at least one prior assistant turn
        """

        window = list(messages[-int(self.config.ingest_window) :]) if messages else []
        if not window:
            return []
        latest_role = str((window[-1] or {}).get("role") or "").strip().lower()
        if latest_role != "user":
            return []
        has_assistant_before_latest = any(
            str((m or {}).get("role") or "").strip().lower() == "assistant" for m in window[:-1]
        )
        if not has_assistant_before_latest:
            return []
        return window

    def _top_reference_from_retrieval_hits(
        self,
        *,
        retrieval_hits: List[Dict[str, Any]],
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        if not retrieval_hits:
            return None
        top = retrieval_hits[0] if isinstance(retrieval_hits[0], dict) else None
        if not isinstance(top, dict):
            return None
        skill = top.get("skill") if isinstance(top.get("skill"), dict) else None
        if isinstance(skill, dict):
            ref_id = str(skill.get("id") or "").strip()
            ref_name = str(skill.get("name") or "").strip()
            ref_desc = str(skill.get("description") or "").strip()
            ref_triggers = [
                str(t).strip() for t in (skill.get("triggers") or []) if str(t).strip()
            ][:20]
            owner = str(skill.get("owner") or "").strip()
        else:
            ref_id = str(top.get("id") or "").strip()
            ref_name = str(top.get("name") or "").strip()
            ref_desc = str(top.get("description") or "").strip()
            ref_triggers = [
                str(t).strip() for t in (top.get("triggers") or []) if str(t).strip()
            ][:20]
            owner = str(top.get("owner") or "").strip()
        if not ref_id and not ref_name and not ref_desc:
            return None
        scope = (
            "library"
            if owner.startswith("library:")
            else ("user" if owner == str(user_id or "").strip() else "other")
        )
        return {
            "id": ref_id,
            "name": ref_name,
            "description": ref_desc,
            "triggers": ref_triggers,
            "scope": scope,
            "score": float(top.get("score") or 0.0),
        }

    def _schedule_extraction_job(
        self,
        *,
        user_id: str,
        messages: List[Dict[str, str]],
        trigger: str,
        hint: Optional[str] = None,
        retrieval_reference: Optional[Dict[str, Any]] = None,
    ) -> str:
        uid = str(user_id or "").strip() or self.config.user_id
        window = list(messages or [])
        job_id = str(uuid.uuid4())
        if not self.config.extract_enabled:
            self._record_extraction_event(
                user_id=uid,
                event=self._empty_extraction_event(
                    job_id=job_id,
                    trigger=str(trigger or "proxy_extract"),
                    status="failed",
                    error="extraction disabled",
                ),
            )
            return job_id
        if not window:
            self._record_extraction_event(
                user_id=uid,
                event=self._empty_extraction_event(
                    job_id=job_id,
                    trigger=str(trigger or "proxy_extract"),
                    status="failed",
                    error="empty extraction window",
                ),
            )
            return job_id

        job = _ProxyExtractJob(
            job_id=job_id,
            user_id=uid,
            window=window,
            trigger=str(trigger or "proxy_extract"),
            hint=(str(hint).strip() if hint and str(hint).strip() else None),
            retrieval_reference=(dict(retrieval_reference) if isinstance(retrieval_reference, dict) else None),
        )
        self._record_extraction_event(
            user_id=uid,
            event=self._empty_extraction_event(
                job_id=job_id,
                trigger=str(trigger or "proxy_extract"),
                status="scheduled",
                error="",
            ),
        )

        should_start_worker = False
        with self._extract_sched_lock:
            if uid in self._extract_running_users:
                # A job is already running for this user: queue for FIFO background processing.
                q = self._extract_queued_by_user.get(uid)
                if q is None:
                    q = []
                    self._extract_queued_by_user[uid] = q
                q.append(job)
            else:
                self._extract_running_users.add(uid)
                should_start_worker = True

        if should_start_worker:
            threading.Thread(
                target=self._background_extraction_worker,
                args=(job,),
                daemon=True,
            ).start()
        return job_id

    def _empty_extraction_event(
        self,
        *,
        job_id: str,
        trigger: str,
        status: str,
        error: str,
        event_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        return {
            "job_id": str(job_id or ""),
            "trigger": str(trigger or "proxy_extract"),
            "event_time": int(event_time or int(time.time() * 1000)),
            "status": str(status or ""),
            "error": str(error or ""),
            "upserted": [],
            "skills": [],
            "skill_mds": [],
        }

    def _build_completed_extraction_event(
        self,
        *,
        updated: List[Skill],
        job_id: str,
        trigger: str,
        event_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        event = self._empty_extraction_event(
            job_id=job_id,
            trigger=trigger,
            status="completed",
            error="",
            event_time=event_time,
        )
        skills = list(updated or [])
        event["upserted"] = [_skill_summary(s) for s in skills]

        if not bool(self.config.extract_event_include_skill_details):
            return event

        max_md_chars = int(self.config.extract_event_max_md_chars or 0)

        md_items: List[Dict[str, Any]] = []
        skill_items: List[Dict[str, Any]] = []
        for s in skills[:3]:
            md_full = str(self.sdk.export_skill_md(str(s.id)) or "")
            md = md_full
            truncated = False
            if max_md_chars > 0 and len(md_full) > max_md_chars:
                md = md_full[:max_md_chars]
                truncated = True
            md_items.append({"id": str(s.id), "md": md, "truncated": bool(truncated)})
            skill_items.append(
                {
                    "id": str(s.id),
                    "name": str(s.name),
                    "description": str(s.description),
                    "version": str(s.version),
                    "owner": str(s.user_id),
                    "triggers": [str(t) for t in (s.triggers or [])],
                    "tags": [str(t) for t in (s.tags or [])],
                    "instructions": str(s.instructions or ""),
                    "examples": _examples_to_raw(list(s.examples or [])),
                    "skill_md": md,
                    "skill_md_truncated": bool(truncated),
                }
            )
        event["skills"] = skill_items
        event["skill_mds"] = md_items
        return event

    def _background_extraction_worker(self, job: _ProxyExtractJob) -> None:
        uid = str(getattr(job, "user_id", "") or "").strip() or self.config.user_id
        acquired = False
        current = job
        try:
            self._extract_sema.acquire()
            acquired = True
            while True:
                self._record_extraction_event(
                    user_id=uid,
                    event=self._empty_extraction_event(
                        job_id=str(current.job_id),
                        trigger=str(current.trigger),
                        status="running",
                        error="",
                    ),
                )
                try:
                    updated = self.sdk.ingest(
                        user_id=uid,
                        messages=list(current.window or []),
                        metadata={
                            "channel": "proxy_api",
                            "trigger": str(current.trigger),
                            "extraction_reference": (
                                dict(current.retrieval_reference)
                                if isinstance(current.retrieval_reference, dict)
                                else None
                            ),
                        },
                        hint=current.hint,
                    )
                    event = self._build_completed_extraction_event(
                        updated=list(updated or []),
                        job_id=str(current.job_id),
                        trigger=str(current.trigger),
                    )
                    self._record_extraction_event(user_id=uid, event=event)
                    if updated:
                        print(
                            f"[proxy] extraction upserted={len(updated)} user={uid} "
                            f"trigger={current.trigger} job={current.job_id}"
                        )
                except Exception as e:
                    self._record_extraction_event(
                        user_id=uid,
                        event=self._empty_extraction_event(
                            job_id=str(current.job_id),
                            trigger=str(current.trigger),
                            status="failed",
                            error=str(e),
                        ),
                    )
                    print(
                        f"[proxy] extraction failed user={uid} "
                        f"trigger={current.trigger} job={current.job_id}: {e}"
                    )

                with self._extract_sched_lock:
                    q = self._extract_queued_by_user.get(uid)
                    next_job = q.pop(0) if q else None
                    if q is not None and not q:
                        self._extract_queued_by_user.pop(uid, None)
                    if next_job is None:
                        self._extract_running_users.discard(uid)
                        break
                current = next_job
        finally:
            if acquired:
                try:
                    self._extract_sema.release()
                except Exception:
                    pass

    def _build_chat_llm(
        self,
        *,
        model: str,
        max_tokens: Optional[int],
        thinking_mode: Optional[bool] = None,
    ) -> LLM:
        cfg = dict(self.llm_config)
        if model:
            cfg["model"] = model
        if max_tokens is not None and int(max_tokens) > 0:
            cfg["max_tokens"] = int(max_tokens)
        if thinking_mode is not None:
            cfg["thinking_mode"] = bool(thinking_mode)
        return build_llm(cfg)

    def _build_embeddings_model(self, *, model: str) -> EmbeddingModel:
        if not model or str(model).strip() == str(self.embeddings_config.get("model") or "").strip():
            return self._base_embeddings
        cfg = dict(self.embeddings_config)
        cfg["model"] = str(model)
        return build_embeddings(cfg)

    def _resolve_user_id(self, *, body: Dict[str, Any], headers: Any) -> str:
        from_body = str(body.get("user") or "").strip()
        if from_body:
            print(f"[proxy] resolved user_id from body user={from_body}", flush=True)
            return from_body
        from_header = str(headers.get("X-AutoSkill-User") or "").strip()
        if from_header:
            print(f"[proxy] resolved user_id from X-AutoSkill-User user={from_header}", flush=True)
            return from_header
        from_auth_jwt = _user_id_from_auth_jwt(headers)
        if from_auth_jwt:
            print(f"[proxy] resolved user_id from Authorization JWT id={from_auth_jwt}", flush=True)
            return from_auth_jwt
        fallback = self.config.user_id
        print(f"[proxy] resolved user_id from default user={fallback}", flush=True)
        return fallback

    def _resolve_scope(self, *, headers: Any) -> str:
        raw = str(headers.get("X-AutoSkill-Scope") or "").strip()
        if not raw:
            return self.config.skill_scope
        return _normalize_scope(raw)

    def _build_assistant_inputs(
        self,
        *,
        messages: List[Dict[str, str]],
        context: str,
        use_skills: bool,
    ) -> Tuple[str, str]:
        base_system = _extract_base_system(messages)
        if use_skills and str(context or "").strip():
            system = (
                "You are a helpful assistant.\n"
                "You have access to a list of retrieved Skills (capabilities) below.\n"
                "CRITICAL: These Skills may be irrelevant.\n"
                "1. Use a Skill only if it clearly matches the current user intent.\n"
                "2. Ignore unrelated Skills and answer normally.\n"
                "3. Do not mention the existence of Skills.\n\n"
                f"Skills Context:\n{context}"
            )
            if base_system:
                system += f"\n\nCaller System Instructions:\n{base_system}"
        else:
            system = base_system or "You are a helpful assistant."

        history = _format_history(messages, max_turns=int(self.config.history_turns))
        user = f"Conversation:\n{history}\n\nRespond to the latest user message."
        return system, user

    def _normalize_embedding_input(self, inp: Any) -> List[str]:
        if inp is None:
            return []
        if isinstance(inp, str):
            s = inp.strip()
            return [s] if s else []
        if isinstance(inp, list):
            out: List[str] = []
            for x in inp:
                if isinstance(x, str):
                    s = x.strip()
                    if s:
                        out.append(s)
                elif isinstance(x, (list, tuple)):
                    # Compatible with OpenAI token-array style input.
                    out.append(" ".join(str(v) for v in x))
                elif x is not None:
                    out.append(str(x))
            return out
        return [str(inp)]
