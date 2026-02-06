"""
OpenAI-compatible reverse proxy server for AutoSkill.

Goals:
- expose a standard API surface (`/v1/chat/completions`, `/v1/embeddings`)
- keep client integration simple (reuse existing OpenAI SDK callers)
- transparently add AutoSkill retrieval + asynchronous skill evolution
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

from ..client import AutoSkill
from ..embeddings.base import EmbeddingModel
from ..embeddings.factory import build_embeddings
from ..interactive.rewriting import LLMQueryRewriter
from ..interactive.selection import LLMSkillSelector
from ..llm.base import LLM
from ..llm.factory import build_llm
from ..models import Skill
from ..render import render_skills_context, select_skills_for_context


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
    handler.send_response(int(status))
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


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
    history_turns: int = 10
    assistant_temperature: float = 0.2
    extract_enabled: bool = True
    ingest_window: int = 8
    max_bg_extract_jobs: int = 2
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
        self.history_turns = max(1, int(self.history_turns or 10))
        self.ingest_window = max(2, int(self.ingest_window or 8))
        self.max_bg_extract_jobs = max(1, int(self.max_bg_extract_jobs or 2))
        self.assistant_temperature = _safe_float(self.assistant_temperature, 0.2)
        key = str(self.proxy_api_key or "").strip()
        self.proxy_api_key = key or None
        return self


@dataclass
class _PreparedChat:
    model: str
    temperature: float
    max_tokens: Optional[int]
    user_id: str
    normalized_messages: List[Dict[str, str]]
    system_prompt: str
    user_prompt: str
    trigger: str


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

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"

                if path == "/health" or path == "/api/health":
                    return _json_response(self, {"ok": True})

                if path == "/v1/models":
                    if not self._authorized():
                        return
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

                self.send_response(404)
                self.end_headers()

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"
                if path.startswith("/v1/") and not self._authorized():
                    return
                try:
                    body = _read_json(self)
                except Exception as e:
                    return _json_response(
                        self,
                        _openai_error(str(e), code="invalid_json"),
                        status=400,
                    )

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
                    if stream:
                        return runtime.stream_chat_completion(self, prepared=prepared)
                    try:
                        payload = runtime.complete_chat_completion(prepared=prepared)
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

                return _json_response(
                    self,
                    _openai_error("Unknown endpoint", code="not_found"),
                    status=404,
                )

        return Handler

    def create_server(self, *, host: str, port: int) -> ThreadingHTTPServer:
        handler = self.make_handler()
        return ThreadingHTTPServer((str(host), int(port)), handler)

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

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope = self._resolve_scope(headers=headers)

        latest_user = _latest_user_query(messages)
        search_query = latest_user
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
                search_query = rewritten.strip()

        hits = self.sdk.search(
            search_query,
            user_id=user_id,
            limit=max(1, int(self.config.top_k)),
            filters={"scope": scope, "allow_partial_vectors": False},
        )
        min_score = float(self.config.min_score or 0.0)
        if hits and min_score > 0:
            hits = [h for h in hits if float(getattr(h, "score", 0.0) or 0.0) >= min_score]

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

        system_prompt, user_prompt = self._build_assistant_inputs(
            messages=messages,
            context=context,
            use_skills=use_skills,
        )

        return _PreparedChat(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            user_id=user_id,
            normalized_messages=messages,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            trigger="proxy_chat_completion",
        )

    def complete_chat_completion(self, *, prepared: _PreparedChat) -> Dict[str, Any]:
        chat_llm = self._build_chat_llm(
            model=prepared.model,
            max_tokens=prepared.max_tokens,
        )
        text = chat_llm.complete(
            system=prepared.system_prompt,
            user=prepared.user_prompt,
            temperature=float(prepared.temperature),
        )
        content = str(text or "").strip()
        if not content:
            content = "(empty response)"

        self._schedule_background_extraction(
            user_id=prepared.user_id,
            messages=prepared.normalized_messages,
            assistant_text=content,
            trigger=prepared.trigger,
        )

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
        }

    def stream_chat_completion(
        self,
        handler: BaseHTTPRequestHandler,
        *,
        prepared: _PreparedChat,
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
            }
            _send(role_chunk)

            chat_llm = self._build_chat_llm(
                model=prepared.model,
                max_tokens=prepared.max_tokens,
            )

            parts: List[str] = []
            for chunk in chat_llm.stream_complete(
                system=prepared.system_prompt,
                user=prepared.user_prompt,
                temperature=float(prepared.temperature),
            ):
                s = str(chunk or "")
                if not s:
                    continue
                parts.append(s)
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

            assistant_text = "".join(parts).strip()
            if not assistant_text:
                assistant_text = "(empty response)"
            self._schedule_background_extraction(
                user_id=prepared.user_id,
                messages=prepared.normalized_messages,
                assistant_text=assistant_text,
                trigger=prepared.trigger,
            )
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

    def _build_chat_llm(self, *, model: str, max_tokens: Optional[int]) -> LLM:
        cfg = dict(self.llm_config)
        if model:
            cfg["model"] = model
        if max_tokens is not None and int(max_tokens) > 0:
            cfg["max_tokens"] = int(max_tokens)
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
            return from_body
        from_header = str(headers.get("X-AutoSkill-User") or "").strip()
        if from_header:
            return from_header
        return self.config.user_id

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

    def _schedule_background_extraction(
        self,
        *,
        user_id: str,
        messages: List[Dict[str, str]],
        assistant_text: str,
        trigger: str,
    ) -> None:
        if not self.config.extract_enabled:
            return
        if not assistant_text.strip():
            return
        if not self._extract_sema.acquire(blocking=False):
            return

        window = list(messages[-int(self.config.ingest_window) :])
        window.append({"role": "assistant", "content": str(assistant_text)})

        def _run() -> None:
            try:
                updated = self.sdk.ingest(
                    user_id=str(user_id),
                    messages=window,
                    metadata={"channel": "proxy_api", "trigger": str(trigger)},
                )
                if updated:
                    print(
                        f"[proxy] extraction upserted={len(updated)} user={user_id} trigger={trigger}"
                    )
            except Exception as e:
                print(f"[proxy] extraction failed user={user_id} trigger={trigger}: {e}")
            finally:
                try:
                    self._extract_sema.release()
                except Exception:
                    pass

        threading.Thread(target=_run, daemon=True).start()

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

