"""
Minimal OpenAI Chat Completions client (urllib-based).

Notes:
- Only covers the minimal parameters needed by the SDK (model/messages/temperature)
- Advanced features (tools, response_format, etc.) can be added later if needed
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional

from .base import LLM
from ..utils.json import json_from_llm_text
from ..utils.units import truncate_system_user


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


def _try_extract_json_text(text: str) -> Optional[str]:
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        obj = json_from_llm_text(raw)
    except Exception:
        return None
    if not isinstance(obj, (dict, list)):
        return None
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return None


def _extract_best_text(parsed: Dict[str, Any]) -> str:
    """
    Extracts the usable text from an OpenAI-compatible Chat Completions response.

    Notes:
    - Prefer `message.content`.
    - Some providers may put structured JSON into `reasoning_content`; we only surface it when it is
      parseable JSON to avoid returning chain-of-thought.
    """

    choices = parsed.get("choices") or []
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0] if isinstance(choices[0], dict) else {}

    msg = first.get("message") or first.get("delta") or {}
    if not isinstance(msg, dict):
        msg = {}

    content = _content_to_text(msg.get("content")).strip()
    if content:
        return content

    # Avoid returning chain-of-thought; only surface parseable JSON from reasoning fields.
    reasoning = _content_to_text(msg.get("reasoning_content") or msg.get("reasoning")).strip()
    if reasoning:
        normalized = _try_extract_json_text(reasoning)
        if normalized is not None:
            return normalized

    # Fallback fields seen in some OpenAI-compatible providers.
    content2 = _content_to_text(first.get("content")).strip()
    if content2:
        return content2
    text2 = _content_to_text(first.get("text")).strip()
    if text2:
        return text2
    return ""


def _extract_stream_delta(parsed: Dict[str, Any]) -> str:
    choices = parsed.get("choices") or []
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0] if isinstance(choices[0], dict) else {}
    delta = first.get("delta") or first.get("message") or {}
    if not isinstance(delta, dict):
        delta = {}
    text = _content_to_text(delta.get("content"))
    return str(text) if text is not None else ""


@dataclass
class OpenAIChatLLM(LLM):
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com"
    timeout_s: int = 60
    max_input_chars: int = 100000
    max_tokens: int = 30000

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
        body = self._post_json(payload=payload, stream=False)
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

    def _build_url(self) -> str:
        base = self.base_url.rstrip("/")
        return (base + "/chat/completions") if base.endswith("/v1") else (base + "/v1/chat/completions")

    def _resolve_api_key(self) -> str:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OpenAIChatLLM requires api_key or OPENAI_API_KEY")
        return key

    def _build_payload(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float,
        stream: bool,
    ) -> Dict[str, Any]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": float(temperature),
            "stream": bool(stream),
        }
        if int(self.max_tokens or 0) > 0:
            payload["max_tokens"] = int(self.max_tokens)
        return payload

    def _build_request(self, *, payload: Dict[str, Any], stream: bool) -> urllib.request.Request:
        key = self._resolve_api_key()
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return urllib.request.Request(
            self._build_url(),
            method="POST",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": ("text/event-stream" if stream else "application/json"),
            },
        )

    def _post_json(self, *, payload: Dict[str, Any], stream: bool) -> str:
        req = self._build_request(payload=payload, stream=stream)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible HTTP {e.code}: {raw}") from e
