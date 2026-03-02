"""
Generic OpenAI-compatible chat provider.

Key behavior:
- Accepts custom URL/model defaults for private deployments.
- API key is optional; Authorization header is added only when key is present.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict

from .openai import OpenAIChatLLM


@dataclass
class GenericChatLLM(OpenAIChatLLM):
    model: str = "gpt-5.2"
    api_key: str | None = None
    base_url: str = "http://35.220.164.252:3888/v1"
    timeout_s: int = 60
    max_input_chars: int = 100000
    max_tokens: int = 30000

    def _resolve_api_key_optional(self) -> str:
        """Run resolve api key optional."""
        key = self.api_key
        if key is None or not str(key).strip():
            key = os.getenv("AUTOSKILL_GENERIC_API_KEY", "")
        return str(key or "").strip()

    def _build_request(self, *, payload: Dict[str, Any], stream: bool) -> urllib.request.Request:
        """Run build request."""
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": ("text/event-stream" if stream else "application/json"),
        }
        key = self._resolve_api_key_optional()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return urllib.request.Request(
            self._build_url(),
            method="POST",
            data=data,
            headers=headers,
        )

