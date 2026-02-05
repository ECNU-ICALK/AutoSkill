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
from typing import Any, Dict, List, Optional

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


@dataclass
class OpenAIChatLLM(LLM):
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com"
    timeout_s: int = 60
    max_input_chars: int = 10000
    max_tokens: int = 4096

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        # Prefer explicit api_key; fall back to env var OPENAI_API_KEY.
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OpenAIChatLLM requires api_key or OPENAI_API_KEY")

        system2, user2 = truncate_system_user(
            system=system, user=user, max_units=int(self.max_input_chars or 0)
        )

        base = self.base_url.rstrip("/")
        # Support both styles:
        # - https://api.openai.com
        # - https://api.openai.com/v1
        url = (
            (base + "/chat/completions")
            if base.endswith("/v1")
            else (base + "/v1/chat/completions")
        )
        messages = []
        if system2:
            messages.append({"role": "system", "content": system2})
        messages.append({"role": "user", "content": user2})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": float(temperature),
        }
        if int(self.max_tokens or 0) > 0:
            payload["max_tokens"] = int(self.max_tokens)
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            url,
            method="POST",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible HTTP {e.code}: {raw}") from e

        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            return ""
        return _extract_best_text(parsed)
