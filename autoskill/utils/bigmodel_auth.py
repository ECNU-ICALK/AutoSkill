"""
BigModel (Zhipu/GLM) auth helpers.

The common api_key format is `api_key_id.api_key_secret`:
- JWT mode: create an HS256-signed token (header + payload + signature)
- api_key mode: pass the raw `id.secret` as Bearer token (works in some environments)

This SDK defaults to auth_mode="auto":
try JWT first; on auth failure it toggles timestamp unit (ms/s) and can fall back to api_key pass-through.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple


def _base64url(data: bytes) -> str:
    """Run base64url."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _json_compact(obj) -> bytes:
    """Run json compact."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _parse_api_key(api_key: str) -> Tuple[str, str]:
    """Run parse api key."""
    parts = (api_key or "").strip().split(".")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("BigModel api_key must look like '<id>.<secret>'")
    return parts[0], parts[1]


def make_bigmodel_jwt(
    *,
    api_key_id: str,
    api_key_secret: str,
    ttl_s: int = 3600,
    timestamp_unit: str = "ms",
    now_s: Optional[int] = None,
) -> Tuple[str, int]:
    """
    Creates an HS256 JWT token used by BigModel (Zhipu/GLM) APIs.
    Returns (token, exp_epoch_seconds).
    """

    unit = (timestamp_unit or "ms").lower()
    if unit not in {"ms", "s"}:
        unit = "ms"

    now_seconds = int(time.time()) if now_s is None else int(now_s)
    if unit == "ms":
        now = now_seconds * 1000
        exp = now + int(ttl_s) * 1000
    else:
        now = now_seconds
        exp = now + int(ttl_s)

    header = {"alg": "HS256", "sign_type": "SIGN"}
    payload = {"api_key": api_key_id, "exp": exp, "timestamp": now}

    encoded_header = _base64url(_json_compact(header))
    encoded_payload = _base64url(_json_compact(payload))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    sig = hmac.new(
        api_key_secret.encode("utf-8"), signing_input, digestmod=hashlib.sha256
    ).digest()
    encoded_sig = _base64url(sig)
    return f"{encoded_header}.{encoded_payload}.{encoded_sig}", exp


@dataclass
class BigModelAuth:
    api_key: Optional[str] = None
    api_key_id: Optional[str] = None
    api_key_secret: Optional[str] = None
    token_ttl_s: int = 3600
    token_time_unit: str = "ms"  # "ms" | "s"
    auth_mode: str = "auto"  # "jwt" | "api_key" | "auto"

    _cached_token: Optional[str] = None
    _cached_exp: int = 0
    _cached_unit: str = "ms"
    _cached_mode: str = "jwt"

    def bearer_token(
        self,
        *,
        force_refresh: bool = False,
        token_time_unit: Optional[str] = None,
        auth_mode: Optional[str] = None,
    ) -> str:
        """Run bearer token."""
        unit = (token_time_unit or self.token_time_unit or "ms").lower()
        if unit not in {"ms", "s"}:
            unit = "ms"

        requested_mode = (auth_mode or self.auth_mode or "auto").lower()
        if requested_mode not in {"jwt", "api_key", "auto"}:
            requested_mode = "auto"

        mode = requested_mode
        if mode not in {"jwt", "api_key", "auto"}:
            mode = "jwt"

        now_s = int(time.time())
        cached_unit = (self._cached_unit or "ms").lower()
        if cached_unit == "ms":
            seconds_to_exp = int((self._cached_exp / 1000) - now_s)
        else:
            seconds_to_exp = int(self._cached_exp - now_s)

        if not force_refresh and self._cached_token and seconds_to_exp > 10:
            if requested_mode == "auto":
                return self._cached_token
            if self._cached_unit == unit and self._cached_mode == mode:
                return self._cached_token

        key_id = (self.api_key_id or "").strip()
        key_secret = (self.api_key_secret or "").strip()
        if not key_id or not key_secret:
            api_key = self.api_key or os.getenv("BIGMODEL_API_KEY") or os.getenv(
                "ZHIPUAI_API_KEY"
            )
            if not api_key:
                raise RuntimeError(
                    "BigModelAuth requires api_key or (api_key_id + api_key_secret)"
                )
            key_id, key_secret = _parse_api_key(api_key)

        if mode == "auto":
            mode = "jwt"

        if mode == "api_key":
            token = f"{key_id}.{key_secret}"
            self._cached_token = token
            self._cached_exp = 2**31 - 1
            self._cached_unit = unit
            self._cached_mode = mode
            return token

        token, exp = make_bigmodel_jwt(
            api_key_id=key_id,
            api_key_secret=key_secret,
            ttl_s=self.token_ttl_s,
            timestamp_unit=unit,
        )
        self._cached_token = token
        self._cached_exp = exp
        self._cached_unit = unit
        self._cached_mode = mode
        return token
