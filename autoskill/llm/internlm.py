"""
InternLM Chat Completions client (OpenAI-compatible, urllib-based).

Official docs:
- https://internlm.intern-ai.org.cn/api/document

This provider keeps AutoSkill's LLM interface unchanged while using InternLM's
OpenAI-compatible endpoint:
- POST https://chat.intern-ai.org.cn/api/v1/chat/completions
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from ..utils.units import truncate_system_user
from .openai import OpenAIChatLLM, _extract_best_text, _extract_stream_delta


@dataclass
class InternLMChatLLM(OpenAIChatLLM):
    """
    InternLM OpenAI-compatible chat client.

    Defaults target Intern-S1 Pro.
    """

    model: str = "intern-s1-pro"
    api_key: Optional[str] = None
    base_url: str = "https://chat.intern-ai.org.cn/api/v1"
    timeout_s: int = 60
    max_input_chars: int = 10000
    max_tokens: int = 4096
    extra_body: Optional[Dict[str, Any]] = None
    # Intern-S1 defaults to think mode. Set to False to disable.
    # If the upstream rejects this parameter, AutoSkill will auto-fallback once.
    thinking_mode: Optional[bool] = True
    _thinking_mode_disabled_by_server: bool = field(default=False, init=False, repr=False)

    def _resolve_api_key(self) -> str:
        key = (
            self.api_key
            or os.getenv("INTERNLM_API_KEY")
            or os.getenv("INTERN_API_KEY")
            or os.getenv("INTERNLM_TOKEN")
        )
        if not key:
            raise RuntimeError(
                "InternLMChatLLM requires api_key or INTERNLM_API_KEY (or INTERN_API_KEY)."
            )
        return str(key)

    def _requested_thinking_mode(self) -> Optional[bool]:
        raw = self.thinking_mode
        if raw is None:
            return None
        if isinstance(raw, bool):
            return raw
        s = str(raw).strip().lower()
        if not s:
            return None
        if s in {"1", "true", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "no", "n", "off"}:
            return False
        return None

    def thinking_mode_status(self) -> Dict[str, Any]:
        requested = self._requested_thinking_mode()
        effective = requested
        if requested is True and self._thinking_mode_disabled_by_server:
            effective = False
        return {
            "supported": True,
            "requested": requested,
            "effective": effective,
            "auto_disabled": bool(self._thinking_mode_disabled_by_server),
        }

    @staticmethod
    def _is_thinking_mode_compat_error(text: str) -> bool:
        s = str(text or "").strip().lower()
        if "thinking_mode" not in s:
            return False
        # Compatible gateways use varied wording; keep this broad but specific to thinking_mode.
        hints = (
            "unsupported",
            "not support",
            "unknown",
            "unrecognized",
            "invalid",
            "unexpected",
            "not allowed",
            "extra inputs",
            "unrecognized field",
            "unknown parameter",
            "不支持",
            "无效",
            "未知字段",
            "参数错误",
        )
        return ("400" in s) or any(h in s for h in hints)

    def _should_attach_thinking_mode(self) -> bool:
        requested = self._requested_thinking_mode()
        if requested is None:
            return False
        if requested is True and self._thinking_mode_disabled_by_server:
            return False
        return True

    def _maybe_disable_thinking_for_retry(self, *, payload: Dict[str, Any], message: str) -> bool:
        if "thinking_mode" not in payload:
            return False
        if payload.get("thinking_mode") is not True:
            return False
        if not self._is_thinking_mode_compat_error(message):
            return False
        self._thinking_mode_disabled_by_server = True
        return True

    def _build_payload(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float,
        stream: bool,
    ) -> Dict[str, Any]:
        payload = super()._build_payload(
            system=system,
            user=user,
            temperature=temperature,
            stream=stream,
        )
        if self.extra_body and isinstance(self.extra_body, dict):
            payload.update(self.extra_body)
        if self._should_attach_thinking_mode() and "thinking_mode" not in payload:
            requested = self._requested_thinking_mode()
            if requested is not None:
                payload["thinking_mode"] = bool(requested)
        # Keep runtime stream flag authoritative.
        payload["stream"] = bool(stream)
        return payload

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        system2, user2 = truncate_system_user(
            system=system, user=user, max_units=int(self.max_input_chars or 0)
        )
        payload = self._build_payload(system=system2, user=user2, temperature=temperature, stream=False)

        try:
            body = self._post_json(payload=payload, stream=False)
        except RuntimeError as e:
            if self._maybe_disable_thinking_for_retry(payload=payload, message=str(e)):
                payload2 = dict(payload)
                payload2.pop("thinking_mode", None)
                body = self._post_json(payload=payload2, stream=False)
            else:
                raise

        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            return ""
        return _extract_best_text(parsed)

    def stream_complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> Iterator[str]:
        system2, user2 = truncate_system_user(
            system=system, user=user, max_units=int(self.max_input_chars or 0)
        )
        payload = self._build_payload(system=system2, user=user2, temperature=temperature, stream=True)

        attempt = 0
        while True:
            attempt += 1
            req = self._build_request(payload=payload, stream=True)
            emitted = False
            fallback_lines: List[str] = []
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    for raw in resp:
                        line = raw.decode("utf-8", errors="replace")
                        fallback_lines.append(line)
                        s = line.strip()
                        if not s.startswith("data:"):
                            continue
                        payload_line = s[5:].strip()
                        if not payload_line or payload_line == "[DONE]":
                            continue
                        try:
                            obj = json.loads(payload_line)
                        except Exception:
                            continue
                        if not isinstance(obj, dict):
                            continue
                        part = _extract_stream_delta(obj)
                        if part:
                            emitted = True
                            yield part
            except urllib.error.HTTPError as e:
                raw = e.read().decode("utf-8", errors="replace")
                if attempt == 1 and self._maybe_disable_thinking_for_retry(payload=payload, message=raw):
                    payload = dict(payload)
                    payload.pop("thinking_mode", None)
                    continue
                raise RuntimeError(f"OpenAI-compatible HTTP {e.code}: {raw}") from e

            if emitted:
                return

            fallback_body = "".join(fallback_lines).strip()
            if not fallback_body:
                return
            # Some gateways may ignore `stream=true` and return a normal JSON body.
            try:
                parsed = json.loads(fallback_body)
            except Exception:
                return
            if not isinstance(parsed, dict):
                return
            text = _extract_best_text(parsed)
            if text:
                yield text
            return
