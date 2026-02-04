"""
BigModel embedding-3 client (urllib-based).

Similar to the GLM LLM client, it supports auth_mode="auto":
- try JWT first (default timestamp unit: ms)
- on auth failure, retry with ms/s toggled for JWT creation
- still failing: fall back to passing the raw api_key (id.secret) as Bearer token
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..utils.bigmodel_auth import BigModelAuth
from .base import EmbeddingModel


@dataclass
class BigModelEmbedding3(EmbeddingModel):
    """
    BigModel embedding client (embedding-3 default).
    Docs: https://docs.bigmodel.cn/cn/guide/models/embedding/embedding-3
    """

    model: str = "embedding-3"
    api_key: Optional[str] = None
    api_key_id: Optional[str] = None
    api_key_secret: Optional[str] = None
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    timeout_s: int = 60
    token_ttl_s: int = 3600
    token_time_unit: str = "ms"  # "ms" | "s"
    auth_mode: str = "auto"  # "jwt" | "api_key" | "auto"
    extra_body: Optional[Dict[str, Any]] = None
    max_text_chars: int = 12000
    min_text_chars: int = 512

    def __post_init__(self) -> None:
        self._auth = BigModelAuth(
            api_key=self.api_key,
            api_key_id=self.api_key_id,
            api_key_secret=self.api_key_secret,
            token_ttl_s=self.token_ttl_s,
            token_time_unit=self.token_time_unit,
            auth_mode=self.auth_mode,
        )

    def embed(self, texts: List[str]) -> List[List[float]]:
        texts = [str(t or "") for t in (texts or [])]
        if not texts:
            return []
        return self._embed_with_auto_split(texts)

    def _embed_with_auto_split(self, texts: List[str]) -> List[List[float]]:
        # Pre-truncate very large inputs so a single huge skill cannot break embedding.
        texts2 = [_truncate_text(t, max_chars=int(self.max_text_chars or 0)) for t in texts]
        try:
            return self._embed_once(texts2)
        except RuntimeError as e:
            if not _looks_like_request_too_large(str(e)):
                raise

            if len(texts2) <= 1:
                # Fall back to aggressive truncation for a single oversized input.
                t = texts2[0] if texts2 else ""
                min_chars = max(0, int(self.min_text_chars or 0))
                if min_chars and len(t) > min_chars:
                    return self._embed_with_auto_split([t[:min_chars]])
                raise

            mid = len(texts2) // 2
            left = self._embed_with_auto_split(texts2[:mid])
            right = self._embed_with_auto_split(texts2[mid:])
            return left + right

    def _embed_once(self, texts: List[str]) -> List[List[float]]:
        body = self._post(texts)

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            raise RuntimeError(f"BigModel embeddings returned non-JSON: {body[:2000]}")

        items = _find_embedding_items(parsed)
        if not items and _looks_like_auth_issue(parsed):
            body2 = self._post(texts, retry_alternate_time_unit=True)
            try:
                parsed2 = json.loads(body2)
            except json.JSONDecodeError:
                raise RuntimeError(f"BigModel embeddings returned non-JSON: {body2[:2000]}")
            items = _find_embedding_items(parsed2)
            if not items:
                mode = (self.auth_mode or "auto").lower()
                if mode == "auto":
                    body3 = self._post(texts, retry_auth_mode="api_key")
                    try:
                        parsed3 = json.loads(body3)
                    except json.JSONDecodeError:
                        raise RuntimeError(
                            f"BigModel embeddings returned non-JSON: {body3[:2000]}"
                        )
                    items = _find_embedding_items(parsed3)
                    if not items:
                        raise RuntimeError(
                            f"BigModel embeddings unexpected response: {body3[:2000]}"
                        )
                else:
                    raise RuntimeError(
                        f"BigModel embeddings unexpected response: {body2[:2000]}"
                    )

        if not items:
            raise RuntimeError(f"BigModel embeddings unexpected response: {body[:2000]}")

        items = sorted(
            items,
            key=lambda x: x.get("index", 0) if isinstance(x, dict) else 0,
        )
        out: List[List[float]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            emb = item.get("embedding")
            if isinstance(emb, list):
                out.append([float(x) for x in emb])
        if len(out) != len(texts):
            raise RuntimeError(
                f"BigModel embeddings returned {len(out)} vectors for {len(texts)} inputs."
            )
        return out

    def _post(
        self,
        texts: List[str],
        *,
        retry_alternate_time_unit: bool = False,
        retry_auth_mode: Optional[str] = None,
    ) -> str:
        url = self.base_url.rstrip("/") + "/embeddings"
        payload: Dict[str, Any] = {"model": self.model, "input": texts}
        if self.extra_body:
            payload.update(self.extra_body)

        token_unit = (self.token_time_unit or "ms").lower()
        if retry_alternate_time_unit:
            token_unit = "s" if token_unit == "ms" else "ms"
        token = self._auth.bearer_token(
            force_refresh=retry_alternate_time_unit or bool(retry_auth_mode),
            token_time_unit=token_unit,
            auth_mode=retry_auth_mode,
        )

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            url,
            method="POST",
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            if int(getattr(e, "code", 0) or 0) in {401, 403}:
                return raw
            raise RuntimeError(f"BigModel embeddings HTTP {e.code}: {raw}") from e
        return body


def _find_embedding_items(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict):
        data = obj.get("data")
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            return data  # type: ignore[return-value]
        if isinstance(data, dict):
            maybe = data.get("data")
            if isinstance(maybe, list) and all(isinstance(x, dict) for x in maybe):
                return maybe  # type: ignore[return-value]
    return []


def _looks_like_auth_issue(obj: Any) -> bool:
    if isinstance(obj, dict):
        http_status = obj.get("_http_status")
        if isinstance(http_status, int) and http_status in {401, 403}:
            return True
        code = obj.get("code")
        if isinstance(code, int) and code in {401, 403}:
            return True
        msg = obj.get("msg") or obj.get("message") or obj.get("error")
        msg_s = str(msg or "").lower()
        needles = [
            "invalid api key",
            "apikey",
            "api_key",
            "unauthorized",
            "forbidden",
            "signature",
            "auth",
            "authentication",
            "permission",
            "permission denied",
        ]
        return any(n in msg_s for n in needles)
    return False


def _looks_like_request_too_large(message: str) -> bool:
    s = str(message or "").lower()
    needles = [
        "request entity too large",
        "entity too large",
        '"code":"1210"',
        "code\": \"1210\"",
        "code\":1210",
    ]
    return any(n in s for n in needles)


def _truncate_text(text: str, *, max_chars: int) -> str:
    t = str(text or "")
    m = int(max_chars or 0)
    if m <= 0 or len(t) <= m:
        return t
    # Keep both head and tail to preserve key identifiers and any final checklists/output formats.
    head = int(m * 0.7)
    tail = max(0, m - head - 32)
    if tail <= 0:
        return t[:m]
    return t[:head] + "\n\n...[truncated]...\n\n" + t[-tail:]
