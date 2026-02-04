"""
Minimal Anthropic Messages API client (urllib-based).

Notes:
- Only covers the minimal parameters needed by the SDK (model/system/messages/temperature)
- Advanced features can be added later while keeping the SDK lightweight
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Optional

from .base import LLM


@dataclass
class AnthropicLLM(LLM):
    model: str = "claude-3-5-sonnet-latest"
    api_key: Optional[str] = None
    base_url: str = "https://api.anthropic.com"
    timeout_s: int = 60

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        # Prefer explicit api_key; fall back to env var ANTHROPIC_API_KEY.
        key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("AnthropicLLM requires api_key or ANTHROPIC_API_KEY")

        url = self.base_url.rstrip("/") + "/v1/messages"
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "temperature": float(temperature),
            "system": system or "",
            "messages": [{"role": "user", "content": user}],
        }
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url,
            method="POST",
            data=data,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            body = resp.read().decode("utf-8")
        parsed = json.loads(body)
        content = parsed.get("content") or []
        if not content:
            return ""
        texts = [c.get("text", "") for c in content if isinstance(c, dict)]
        return "".join(texts).strip()
