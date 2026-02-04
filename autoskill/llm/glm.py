"""
BigModel GLM (GLM-4.7) Chat Completions client (urllib-based).

Features:
- supports JWT auth (HS256) and raw api_key pass-through; auth_mode="auto" can fall back automatically
- avoids returning chain-of-thought; will only fall back to `reasoning_content` when it contains parseable JSON
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..utils.bigmodel_auth import BigModelAuth
from ..utils.json import json_from_llm_text
from ..utils.units import truncate_system_user
from .base import LLM


def _truncate_inputs(
    *, system: Optional[str], user: str, max_input_chars: int
) -> tuple[Optional[str], str]:
    return truncate_system_user(system=system, user=user, max_units=int(max_input_chars or 0))


@dataclass
class GLMChatLLM(LLM):
    """
    BigModel GLM chat completion client (GLM-4.7 default).
    Docs: https://docs.bigmodel.cn/cn/guide/models/text/glm-4.7
    """

    model: str = "glm-4.7"
    api_key: Optional[str] = None
    api_key_id: Optional[str] = None
    api_key_secret: Optional[str] = None
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    timeout_s: int = 60
    max_tokens: int = 4096
    max_input_chars: int = 10000
    token_ttl_s: int = 3600
    token_time_unit: str = "ms"  # "ms" | "s"
    auth_mode: str = "auto"  # "jwt" | "api_key" | "auto"
    extra_body: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self._auth = BigModelAuth(
            api_key=self.api_key,
            api_key_id=self.api_key_id,
            api_key_secret=self.api_key_secret,
            token_ttl_s=self.token_ttl_s,
            token_time_unit=self.token_time_unit,
            auth_mode=self.auth_mode,
        )

    def complete(
        self,
        *,
        system: Optional[str],
        user: str,
        temperature: float = 0.0,
    ) -> str:
        system2, user2 = _truncate_inputs(
            system=system, user=user, max_input_chars=int(self.max_input_chars or 0)
        )
        messages = []
        if system2:
            messages.append({"role": "system", "content": system2})
        messages.append({"role": "user", "content": user2})

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(self.max_tokens),
            "stream": False,
        }
        if self.extra_body:
            payload.update(self.extra_body)

        body, parsed = self._post_json("/chat/completions", payload)
        out = _extract_best_text(parsed)
        if out is not None:
            return out

        # If the response looks like an auth error, retry with ms/s toggled or fall back to raw api_key.
        if _is_auth_error_response(parsed):
            body2, parsed2 = self._post_json(
                "/chat/completions", payload, retry_alternate_time_unit=True
            )
            out2 = _extract_best_text(parsed2)
            if out2 is not None:
                return out2
            mode = (self.auth_mode or "auto").lower()
            if mode == "auto":
                body3, parsed3 = self._post_json(
                    "/chat/completions",
                    payload,
                    retry_auth_mode="api_key",
                )
                out3 = _extract_best_text(parsed3)
                if out3 is not None:
                    return out3
                raise RuntimeError(_format_unexpected_response("GLM", body3, parsed3))
            raise RuntimeError(_format_unexpected_response("GLM", body2, parsed2))

        raise RuntimeError(_format_unexpected_response("GLM", body, parsed))

    def _post_json(
        self,
        path: str,
        payload: Dict[str, Any],
        *,
        retry_alternate_time_unit: bool = False,
        retry_auth_mode: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        url = self.base_url.rstrip("/") + str(path)

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
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    parsed["_http_status"] = int(getattr(e, "code", 0) or 0)
                    return raw, parsed
            except json.JSONDecodeError:
                pass
            raise RuntimeError(f"GLM HTTP {e.code}: {raw}") from e

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            raise RuntimeError(f"GLM returned non-JSON: {body[:2000]}")

        if not isinstance(parsed, dict):
            raise RuntimeError(f"GLM returned unexpected JSON: {body[:2000]}")
        return body, parsed


def _extract_chat_content(parsed: Dict[str, Any]) -> Optional[str]:
    choices = _find_choices(parsed)
    if not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None

    for key in ("message", "delta"):
        msg = first.get(key)
        if isinstance(msg, dict):
            content = msg.get("content")
            text = _content_to_text(content)
            if text is not None and str(text).strip():
                return text

    if "content" in first:
        text = _content_to_text(first.get("content"))
        if text is not None and str(text).strip():
            return text

    if "text" in first:
        return str(first.get("text") or "")

    return None


def _extract_chat_reasoning(parsed: Dict[str, Any]) -> Optional[str]:
    choices = _find_choices(parsed)
    if not choices:
        return None
    first = choices[0]
    if not isinstance(first, dict):
        return None

    for key in ("message", "delta"):
        msg = first.get(key)
        if isinstance(msg, dict):
            reasoning = msg.get("reasoning_content") or msg.get("reasoning")
            rtext = _content_to_text(reasoning)
            if rtext is not None and str(rtext).strip():
                return rtext
    return None


def _looks_like_structured_output(text: str) -> bool:
    s = (text or "").lstrip()
    if not s:
        return False
    if s[0] in "{[":
        return True
    low = s.lower()
    # Heuristic: the model likely produced structured JSON, but it may be placed in reasoning_content.
    needles = [
        '"skills"',
        '"should_extract"',
        '"use_skills"',
        '"selected_skill_ids"',
        '"action"',
        '"target_skill_id"',
        '"prompt"',
    ]
    return any(k in low for k in needles)


def _extract_best_text(parsed: Dict[str, Any]) -> Optional[str]:
    """
    Extracts the best usable text from a parsed GLM response.

    Prefer (in order):
    1) `content`
    2) parseable JSON inside `reasoning_content` (to avoid returning chain-of-thought)

    If a choices block exists but no usable text is found, return empty string so callers can fall back.
    """

    content = _extract_chat_content(parsed)
    if content is not None and content.strip():
        normalized = _try_extract_json_text(content)
        return normalized if normalized is not None else content.strip()

    reasoning = _extract_chat_reasoning(parsed)
    if reasoning is not None and reasoning.strip():
        normalized_r = _try_extract_json_text(reasoning)
        if normalized_r is not None:
            return normalized_r
        # Avoid returning chain-of-thought: only surface reasoning_content when it appears to contain
        # structured output (e.g., JSON decisions for extract/select/maintain flows).
        return reasoning.strip() if _looks_like_structured_output(reasoning) else ""

    if _find_choices(parsed):
        return ""
    return None


def _try_extract_json_text(text: str) -> Optional[str]:
    """
    Best-effort JSON normalization:
    - If `text` contains any parseable JSON (possibly wrapped in fences/commentary), return a canonical JSON string.
    - Otherwise return None so callers can treat it as normal text.
    """

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


def _content_to_text(content: Any) -> Optional[str]:
    if content is None:
        return None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts: List[str] = []
        for c in content:
            if isinstance(c, dict):
                if "text" in c:
                    texts.append(str(c.get("text") or ""))
                elif "content" in c:
                    texts.append(str(c.get("content") or ""))
            elif isinstance(c, str):
                texts.append(c)
        return "".join(texts)
    if isinstance(content, dict):
        if "text" in content:
            return str(content.get("text") or "")
        if "content" in content:
            return str(content.get("content") or "")
    return str(content)


def _find_choices(obj: Any) -> List[Any]:
    if isinstance(obj, dict) and isinstance(obj.get("choices"), list):
        return obj["choices"]
    for candidate in _walk(obj, depth=4):
        if isinstance(candidate, dict) and isinstance(candidate.get("choices"), list):
            return candidate["choices"]
    return []


def _walk(obj: Any, *, depth: int) -> List[Any]:
    if depth < 0:
        return []
    out: List[Any] = [obj]
    if depth == 0:
        return out
    if isinstance(obj, dict):
        for v in obj.values():
            out.extend(_walk(v, depth=depth - 1))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(_walk(v, depth=depth - 1))
    return out


def _is_auth_error_response(parsed: Dict[str, Any]) -> bool:
    http_status = parsed.get("_http_status")
    if isinstance(http_status, int) and http_status in {401, 403}:
        return True

    code = parsed.get("code")
    if isinstance(code, int) and code in {401, 403}:
        return True

    msg = parsed.get("msg") or parsed.get("message") or parsed.get("error")
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


def _format_unexpected_response(prefix: str, body: str, parsed: Dict[str, Any]) -> str:
    code = parsed.get("code")
    msg = parsed.get("msg") or parsed.get("message") or parsed.get("error")
    if code is not None or msg is not None:
        return f"{prefix} unexpected response: code={code} msg={msg} body={body[:2000]}"
    return f"{prefix} unexpected response body={body[:2000]}"
