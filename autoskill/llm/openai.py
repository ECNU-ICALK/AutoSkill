"""
Minimal OpenAI Chat Completions client (urllib-based).

Notes:
- Only covers the minimal parameters needed by the SDK (model/messages/temperature)
- Advanced features (tools, response_format, etc.) can be added later if needed
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .base import LLM
from ..utils.units import truncate_system_user


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

        url = self.base_url.rstrip("/") + "/v1/chat/completions"
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
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            method="POST",
            data=data,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            body = resp.read().decode("utf-8")
        parsed = json.loads(body)
        choices = parsed.get("choices") or []
        if not choices:
            return ""
        msg = choices[0].get("message") or {}
        return str(msg.get("content") or "")
