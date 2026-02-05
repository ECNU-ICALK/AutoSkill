"""
Minimal OpenAI embeddings client (urllib-based).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base import EmbeddingModel
from ..utils.units import text_units, truncate_keep_head_tail


class EmbeddingsHTTPError(RuntimeError):
    def __init__(self, code: int, body: str) -> None:
        self.code = int(code or 0)
        self.body = str(body or "")
        super().__init__(f"Embeddings HTTP {self.code}: {self.body}")


def _looks_like_request_too_large(text: str) -> bool:
    s = str(text or "").lower()
    needles = [
        "request entity too large",
        "entity too large",
        "payload too large",
        "too large",
        "maximum context length",
        "input is too long",
        "exceed",
        "exceeds",
        "limit",
        "too many tokens",
        "超过",
        "过长",
        "太长",
        "请求实体过大",
        "payload过大",
    ]
    return any(n in s for n in needles)


@dataclass
class OpenAIEmbedding(EmbeddingModel):
    model: str = "text-embedding-3-small"
    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com"
    timeout_s: int = 60
    max_text_chars: int = 10000
    min_text_chars: int = 512
    max_batch_size: int = 256
    extra_body: Optional[Dict[str, Any]] = None

    def embed(self, texts: List[str]) -> List[List[float]]:
        key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OpenAIEmbedding requires api_key or OPENAI_API_KEY")

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

    def _embed_with_fallback(self, texts: List[str], *, key: str, depth: int) -> List[List[float]]:
        if not texts:
            return []
        if depth > 6:
            # Safety valve against pathological recursion.
            return self._embed_per_item(texts, key=key)

        batch_size = int(self.max_batch_size or 0)
        if batch_size <= 0:
            batch_size = len(texts)
        batch_size = max(1, batch_size)

        out: List[List[float]] = []
        i = 0
        while i < len(texts):
            chunk = texts[i : i + batch_size]
            try:
                out.extend(self._embed_once(chunk, key=key))
            except EmbeddingsHTTPError as e:
                # Auth errors won't be fixed by splitting or per-item retries.
                if int(getattr(e, "code", 0) or 0) in {401, 403}:
                    raise

                # If the request is too large, split the chunk to reduce payload size.
                if len(chunk) > 1 and _looks_like_request_too_large(e.body):
                    mid = len(chunk) // 2
                    if mid <= 0:
                        raise
                    out.extend(self._embed_with_fallback(chunk[:mid], key=key, depth=depth + 1))
                    out.extend(self._embed_with_fallback(chunk[mid:], key=key, depth=depth + 1))
                elif len(chunk) > 1:
                    # Some OpenAI-compatible providers only accept a single string input.
                    # Fallback to per-item requests.
                    out.extend(self._embed_per_item(chunk, key=key))
                else:
                    # Single input: try more aggressive truncation on "too large" failures.
                    # Some providers return generic 400s with an empty body for size-related failures,
                    # so we also retry truncation in that case.
                    code = int(getattr(e, "code", 0) or 0)
                    body = str(getattr(e, "body", "") or "")
                    min_units = max(0, int(self.min_text_chars or 0))
                    t0 = chunk[0] if chunk else ""
                    should_truncate = _looks_like_request_too_large(body) or (
                        code in {400, 413} and not body.strip()
                    )
                    if should_truncate and min_units and text_units(t0) > min_units:
                        t2 = truncate_keep_head_tail(t0, max_units=min_units)
                        out.extend(self._embed_once([t2], key=key))
                    else:
                        raise
            i += len(chunk)

        if len(out) != len(texts):
            raise RuntimeError(f"Embeddings returned {len(out)} vectors for {len(texts)} inputs.")
        return out

    def _embed_per_item(self, texts: List[str], *, key: str) -> List[List[float]]:
        out: List[List[float]] = []
        for t in texts:
            out.extend(self._embed_once([t], key=key))
        return out

    def _embed_once(self, texts: List[str], *, key: str) -> List[List[float]]:
        base = self.base_url.rstrip("/")
        # Support both styles:
        # - https://api.openai.com
        # - https://api.openai.com/v1
        url = (base + "/embeddings") if base.endswith("/v1") else (base + "/v1/embeddings")
        input_value: Any = texts[0] if len(texts) == 1 else list(texts)
        payload: Dict[str, Any] = {"model": self.model, "input": input_value}
        if self.extra_body:
            for k, v in dict(self.extra_body).items():
                if k in {"model", "input"}:
                    continue
                payload[k] = v
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
            raise RuntimeError(f"Embeddings returned {len(vectors)} vectors for {len(texts)} inputs.")
        return vectors
