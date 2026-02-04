"""
Minimal OpenAI embeddings client (urllib-based).
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import List, Optional

from .base import EmbeddingModel


@dataclass
class OpenAIEmbedding(EmbeddingModel):
    model: str = "text-embedding-3-small"
    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com"
    timeout_s: int = 60

    def embed(self, texts: List[str]) -> List[List[float]]:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OpenAIEmbedding requires api_key or OPENAI_API_KEY")

        url = self.base_url.rstrip("/") + "/v1/embeddings"
        payload = {"model": self.model, "input": texts}
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
        items = parsed.get("data") or []
        items = sorted(items, key=lambda x: x.get("index", 0))
        return [item["embedding"] for item in items]
