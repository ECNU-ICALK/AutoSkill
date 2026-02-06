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
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.interactive import InteractiveConfig, LLMQueryRewriter
from autoskill.interactive.session import InteractiveSession
from autoskill.llm.factory import build_llm

from .interactive_chat import (
    _env,
    _pick_default_provider,
    build_embeddings_config,
    build_llm_config,
)


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


class _SessionManager:
    def __init__(
        self,
        *,
        sdk: AutoSkill,
        interactive_cfg: InteractiveConfig,
        chat_llm: Optional[Any],
        query_rewriter: Optional[LLMQueryRewriter],
    ) -> None:
        self.sdk = sdk
        self.interactive_cfg = interactive_cfg
        self.chat_llm = chat_llm
        self.query_rewriter = query_rewriter

        self._lock = threading.Lock()
        self._sessions: Dict[str, InteractiveSession] = {}

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
        with self._lock:
            self._sessions[sid] = session
        return sid, session

    def get(self, sid: str) -> Optional[InteractiveSession]:
        key = str(sid or "").strip()
        if not key:
            return None
        with self._lock:
            return self._sessions.get(key)


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
                return _json_response(self, {"ok": True})

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
                return _json_response(self, {"session_id": sid, "state": session.state()})

            if path == "/api/session/state":
                sid = str(body.get("session_id") or "").strip()
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                return _json_response(self, {"session_id": sid, "state": session.state()})

            if path == "/api/session/poll":
                sid = str(body.get("session_id") or "").strip()
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                return _json_response(self, {"session_id": sid, **session.poll()})

            if path == "/api/session/input":
                sid = str(body.get("session_id") or "").strip()
                text = str(body.get("text") or "")
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                try:
                    out = session.handle_input(text)
                except Exception as e:
                    return _json_response(self, {"error": str(e)}, status=500)
                return _json_response(self, {"session_id": sid, "result": out})

            if path == "/api/session/input_stream":
                sid = str(body.get("session_id") or "").strip()
                text = str(body.get("text") or "")
                session = manager.get(sid)
                if session is None:
                    return _json_response(self, {"error": "unknown session_id"}, status=404)
                try:
                    self._start_ndjson()
                    self._write_ndjson({"type": "meta", "session_id": sid})
                    for ev in session.handle_input_stream(text):
                        if not isinstance(ev, dict):
                            continue
                        self._write_ndjson(ev)
                except BrokenPipeError:
                    return
                except Exception as e:
                    try:
                        self._write_ndjson({"type": "error", "error": str(e)})
                    except Exception:
                        pass
                return

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

                from autoskill.models import SkillExample
                from autoskill.skill_management.formats.agent_skill import (
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
        help="mock|glm|dashscope|openai|anthropic",
    )
    parser.add_argument("--llm-model", default=None)
    parser.add_argument(
        "--embeddings-provider",
        default="",
        help="hashing|glm|dashscope|openai (default depends on llm)",
    )
    parser.add_argument("--embeddings-model", default=None)
    default_store_dir = _env("AUTOSKILL_STORE_DIR", _env("AUTOSKILL_STORE_PATH", "Skills"))
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
                rewrite_cfg["max_tokens"] = min(int(rewrite_cfg.get("max_tokens", 4096)), 4096)
            except Exception:
                rewrite_cfg["max_tokens"] = 4096
        query_rewriter = LLMQueryRewriter(build_llm(rewrite_cfg))

    manager = _SessionManager(
        sdk=sdk,
        interactive_cfg=interactive_cfg,
        chat_llm=chat_llm,
        query_rewriter=query_rewriter,
    )

    handler_cls = make_handler(manager)
    server = ThreadingHTTPServer((str(args.host), int(args.port)), handler_cls)
    host, port = server.server_address[:2]
    print(f"AutoSkill Web UI: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
