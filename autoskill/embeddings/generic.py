"""
Generic OpenAI-compatible embeddings provider.

Key behavior:
- Accepts custom URL/model defaults for private deployments.
- API key is optional; Authorization header is added only when key is present.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List

from .openai import EmbeddingsHTTPError, OpenAIEmbedding
from ..utils.units import truncate_keep_head_tail


@dataclass
class GenericEmbedding(OpenAIEmbedding):
    model: str = "embd_qwen3vl8b"
    api_key: str | None = None
    base_url: str = "http://s-20260204155338-p8gv8.ailab-evalservice.pjh-service.org.cn/v1"
    timeout_s: int = 60
    max_text_chars: int = 10000
    min_text_chars: int = 512
    max_batch_size: int = 256

    def _resolve_api_key_optional(self) -> str:
        """Run resolve api key optional."""
        key = self.api_key
        if key is None or not str(key).strip():
            key = os.getenv("AUTOSKILL_GENERIC_API_KEY", "")
        return str(key or "").strip()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Run embed."""
        key = self._resolve_api_key_optional()
        raw_texts = [str(t or "") for t in (texts or [])]
        if not raw_texts:
            return []

        texts2 = [
            truncate_keep_head_tail(t, max_units=int(self.max_text_chars or 0))
            for t in raw_texts
        ]
        if not texts2:
            return []
        return self._embed_with_fallback(texts2, key=key, depth=0)

    def _embed_once(self, texts: List[str], *, key: str) -> List[List[float]]:
        """Run embed once."""
        base = self.base_url.rstrip("/")
        url = (base + "/embeddings") if base.endswith("/v1") else (base + "/v1/embeddings")
        input_value: Any = texts[0] if len(texts) == 1 else list(texts)
        payload: Dict[str, Any] = {"model": self.model, "input": input_value}
        if self.extra_body:
            for k, v in dict(self.extra_body).items():
                if k in {"model", "input"}:
                    continue
                payload[k] = v
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if key:
            headers["Authorization"] = f"Bearer {key}"

        req = urllib.request.Request(
            url,
            method="POST",
            data=data,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            raise EmbeddingsHTTPError(int(getattr(e, "code", 0) or 0), raw) from e

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            raise RuntimeError(f"Embeddings returned non-JSON: {body[:2000]}")

        items = parsed.get("data") if isinstance(parsed, dict) else None
        if not isinstance(items, list):
            raise RuntimeError(f"Embeddings returned unexpected JSON: {body[:2000]}")

        items = [it for it in items if isinstance(it, dict)]
        items = sorted(items, key=lambda x: x.get("index", 0))
        vectors: List[List[float]] = []
        for it in items:
            emb = it.get("embedding")
            if isinstance(emb, list):
                vectors.append([float(x) for x in emb])
            else:
                raise RuntimeError(
                    "Embeddings returned non-float format; set encoding_format=float."
                )
        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Embeddings returned {len(vectors)} vectors for {len(texts)} inputs."
            )
        return vectors

