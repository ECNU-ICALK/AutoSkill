"""
OpenClaw-focused AutoSkill runtime.

This runtime keeps retrieval/evolution APIs and disables chat-generation endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlparse

from autoskill.interactive.server import (
    AutoSkillProxyRuntime,
    _json_response,
    _normalize_messages,
    _normalize_scope,
    _openai_error,
    _parse_bool,
    _safe_float,
    _safe_int,
)


class OpenClawSkillRuntime(AutoSkillProxyRuntime):
    """
    Runtime specialized for OpenClaw plugin mode.

    The service does not act as a chat model proxy. It focuses on:
    - query rewrite + skill retrieval
    - background extraction/update scheduling
    - skill management APIs
    """

    def capabilities(self) -> Dict[str, Any]:
        payload = dict(super().capabilities() or {})
        data = dict(payload.get("data") or {})
        data.pop("chat", None)
        data.pop("embeddings", None)
        data["openclaw"] = {
            "turn": "/v1/autoskill/openclaw/turn",
            "retrieve_preview": "/v1/autoskill/retrieval/preview",
            "import_conversations": "/v1/autoskill/conversations/import",
        }
        payload["data"] = data
        return payload

    def openapi_spec(self) -> Dict[str, Any]:
        spec = dict(super().openapi_spec() or {})
        paths = dict(spec.get("paths") or {})
        paths.pop("/v1/chat/completions", None)
        paths.pop("/v1/embeddings", None)
        paths["/v1/autoskill/openclaw/turn"] = {
            "post": {"summary": "Retrieve skills for a turn and schedule background extraction"}
        }
        spec["paths"] = paths
        return spec

    def openclaw_turn_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """
        Main OpenClaw integration endpoint.

        Input:
        - messages or query
        - optional scope/min_score/top_k
        - optional schedule_extraction (default true)
        - optional hint

        Output:
        - retrieval payload (rewritten query + hits + selected skill ids + context)
        - extraction scheduling status/job id
        """

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

        schedule = _parse_bool(body.get("schedule_extraction"), default=True)
        hint_raw = body.get("hint")
        hint = str(hint_raw).strip() if hint_raw is not None and str(hint_raw).strip() else None
        extraction_job_id: Optional[str] = None
        extraction_status = "disabled"
        extraction_reason = "schedule_extraction=false"

        if schedule:
            extraction_window = self._build_auto_extraction_window(messages)
            if extraction_window:
                top_ref = self._top_reference_from_retrieval_hits(
                    retrieval_hits=list((retrieval or {}).get("hits") or []),
                    user_id=user_id,
                )
                extraction_job_id = self._schedule_extraction_job(
                    user_id=user_id,
                    messages=extraction_window,
                    trigger="openclaw_turn",
                    hint=hint,
                    retrieval_reference=top_ref,
                )
                ev = self._get_extraction_event_by_job(job_id=extraction_job_id)
                extraction_status = str((ev or {}).get("status") or "scheduled")
                extraction_reason = ""
            else:
                extraction_status = "skipped"
                extraction_reason = "window_not_ready"

        return {
            "object": "openclaw_turn",
            "user": user_id,
            "scope": scope,
            **payload,
            "context": str(retrieval.get("context") or ""),
            "extraction": {
                "job_id": extraction_job_id,
                "status": extraction_status,
                "reason": extraction_reason,
            },
        }

    def make_handler(self) -> type:
        base_handler = super().make_handler()
        runtime = self

        class Handler(base_handler):
            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"

                # This plugin is not a chat-generation proxy.
                if path in {"/v1/chat/completions", "/v1/embeddings"}:
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    return _json_response(
                        self,
                        _openai_error(
                            "Endpoint disabled in OpenClaw skill service",
                            code="not_supported",
                        ),
                        status=404,
                    )

                if path == "/v1/autoskill/openclaw/turn":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    try:
                        payload = runtime.openclaw_turn_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                return super().do_POST()

        return Handler
