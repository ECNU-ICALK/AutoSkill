"""
Persist OpenClaw conversation payloads locally for future replay/offline processing.

The archive is intentionally append-only and JSONL-based so it stays lightweight,
easy to inspect, and independent from the AutoSkill core store implementation.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _slug(value: Any, *, fallback: str) -> str:
    raw = _safe_text(value)
    if not raw:
        return fallback
    out: List[str] = []
    prev_dash = False
    for ch in raw:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
            continue
        if ch in {"-", "_", ".", ":"}:
            out.append(ch)
            prev_dash = False
            continue
        if ch.isspace():
            if not prev_dash:
                out.append("-")
                prev_dash = True
    text = "".join(out).strip("-_.:") or fallback
    return text[:96] or fallback


def detect_archive_dir(explicit_path: str = "") -> str:
    explicit = _safe_text(explicit_path)
    if explicit:
        return str(Path(explicit).expanduser().resolve())
    return str((Path.home() / ".openclaw" / "autoskill" / "conversations").resolve())


def _sanitize_message(message: Any, *, max_content_chars: int) -> Optional[Dict[str, Any]]:
    if not isinstance(message, dict):
        return None
    role = _safe_text(message.get("role")).lower()
    if not role:
        return None
    content = message.get("content")
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = _safe_text(item.get("text") or item.get("content"))
                if text:
                    parts.append(text)
        content_text = "".join(parts)
    else:
        content_text = _safe_text(content)
    if max_content_chars > 0 and len(content_text) > max_content_chars:
        content_text = content_text[:max_content_chars]
    out: Dict[str, Any] = {
        "role": role,
        "content": content_text,
    }
    name = _safe_text(message.get("name"))
    if name:
        out["name"] = name[:128]
    tool_call_id = _safe_text(message.get("tool_call_id"))
    if tool_call_id:
        out["tool_call_id"] = tool_call_id[:128]
    return out


def _sanitize_messages(
    messages: List[Dict[str, Any]],
    *,
    max_messages: int,
    max_content_chars: int,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in list(messages or [])[: max(1, int(max_messages or 200))]:
        sanitized = _sanitize_message(item, max_content_chars=max_content_chars)
        if sanitized is not None:
            out.append(sanitized)
    return out


def _sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    raw = metadata if isinstance(metadata, dict) else {}
    out: Dict[str, Any] = {}
    for key, value in raw.items():
        k = _safe_text(key)
        if not k:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[k] = value
            continue
        if isinstance(value, dict):
            nested: Dict[str, Any] = {}
            for nk, nv in value.items():
                nnk = _safe_text(nk)
                if not nnk:
                    continue
                if isinstance(nv, (str, int, float, bool)) or nv is None:
                    nested[nnk] = nv
            if nested:
                out[k] = nested
            continue
        if isinstance(value, list):
            items = [item for item in value if isinstance(item, (str, int, float, bool)) or item is None]
            if items:
                out[k] = items
    return out


@dataclass
class OpenClawConversationArchiveConfig:
    enabled: bool = True
    archive_dir: str = ""
    max_messages_per_record: int = 200
    max_content_chars: int = 20000
    session_idle_timeout_seconds: int = 0
    session_max_turns: int = 20

    def normalize(self) -> "OpenClawConversationArchiveConfig":
        self.enabled = bool(self.enabled)
        self.archive_dir = detect_archive_dir(self.archive_dir)
        self.max_messages_per_record = max(1, int(self.max_messages_per_record or 200))
        self.max_content_chars = max(256, int(self.max_content_chars or 20000))
        self.session_idle_timeout_seconds = max(0, int(self.session_idle_timeout_seconds or 0))
        self.session_max_turns = max(0, int(self.session_max_turns or 0))
        return self


class OpenClawConversationArchive:
    """Append OpenClaw conversation payloads into local JSONL files."""

    def __init__(self, *, config: Optional[OpenClawConversationArchiveConfig] = None) -> None:
        self.config = (config or OpenClawConversationArchiveConfig()).normalize()
        self._lock = threading.Lock()
        self._active_session_by_user: Dict[str, str] = {}
        self._active_session_touch_ms: Dict[str, int] = {}
        self._active_session_turn_count: Dict[str, int] = {}

    def status(self) -> Dict[str, Any]:
        return {
            "enabled": bool(self.config.enabled),
            "archive_dir": str(self.config.archive_dir),
            "max_messages_per_record": int(self.config.max_messages_per_record),
            "max_content_chars": int(self.config.max_content_chars),
            "session_idle_timeout_seconds": int(self.config.session_idle_timeout_seconds),
            "session_max_turns": int(self.config.session_max_turns),
            "session_archive_dir": str((Path(self.config.archive_dir).expanduser().resolve() / "sessions")),
        }

    def append_record(
        self,
        *,
        user_id: str,
        source: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        uid = _safe_text(user_id)
        if not self.config.enabled:
            return {"enabled": False, "skipped": True, "reason": "archive_disabled", "user_id": uid}
        sanitized_messages = _sanitize_messages(
            list(messages or []),
            max_messages=int(self.config.max_messages_per_record),
            max_content_chars=int(self.config.max_content_chars),
        )
        if not sanitized_messages:
            return {"enabled": True, "skipped": True, "reason": "empty_messages", "user_id": uid}

        root = Path(self.config.archive_dir).expanduser().resolve()
        bucket = root / _slug(uid or "default", fallback="default")
        bucket.mkdir(parents=True, exist_ok=True)
        day = time.strftime("%Y-%m-%d", time.localtime())
        path = bucket / f"{day}.jsonl"
        payload = {
            "record_id": uuid.uuid4().hex,
            "event_time": int(time.time() * 1000),
            "user_id": uid,
            "source": _safe_text(source) or "openclaw",
            "message_count": len(sanitized_messages),
            "messages": sanitized_messages,
            "metadata": _sanitize_metadata(metadata),
        }
        line = json.dumps(payload, ensure_ascii=False) + "\n"
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line)
        return {
            "enabled": True,
            "skipped": False,
            "reason": "",
            "user_id": uid,
            "path": str(path),
            "record_id": str(payload["record_id"]),
        }

    def append_session_record(
        self,
        *,
        user_id: str,
        session_id: str,
        turn_type: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        session_done: bool = False,
        success: bool = True,
    ) -> Dict[str, Any]:
        """
        Append one turn payload into the session-specific file.

        It also detects session boundaries per user:
        - current session_id differs from the previous active session_id
        - explicit session_done=True
        """

        uid = _safe_text(user_id)
        sid = _safe_text(session_id)
        if not self.config.enabled:
            return {
                "enabled": False,
                "skipped": True,
                "reason": "archive_disabled",
                "user_id": uid,
                "session_id": sid,
                "ended_sessions": [],
            }
        if not sid:
            return {
                "enabled": True,
                "skipped": True,
                "reason": "missing_session_id",
                "user_id": uid,
                "session_id": sid,
                "ended_sessions": [],
            }

        sanitized_messages = _sanitize_messages(
            list(messages or []),
            max_messages=int(self.config.max_messages_per_record),
            max_content_chars=int(self.config.max_content_chars),
        )
        if not sanitized_messages:
            return {
                "enabled": True,
                "skipped": True,
                "reason": "empty_messages",
                "user_id": uid,
                "session_id": sid,
                "ended_sessions": [],
            }

        ended_sessions: List[Dict[str, Any]] = []
        turn_type_norm = _safe_text(turn_type).lower()
        root = Path(self.config.archive_dir).expanduser().resolve()
        now_ms = int(time.time() * 1000)
        current_path: Optional[Path] = None
        with self._lock:
            if int(self.config.session_idle_timeout_seconds or 0) > 0:
                ended_sessions.extend(self._close_idle_session_locked(user_id=uid, now_ms=now_ms))

            prev_sid = self._active_session_by_user.get(uid)
            if prev_sid and prev_sid != sid:
                ended_sessions.append(
                    self._close_session_file_locked(
                        user_id=uid,
                        session_id=prev_sid,
                        reason="session_id_changed",
                    )
                )
                self._active_session_turn_count.pop(uid, None)

            path = self._session_file_path(root=root, user_id=uid, session_id=sid)
            current_path = path
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "record_id": uuid.uuid4().hex,
                "event_time": int(time.time() * 1000),
                "user_id": uid,
                "session_id": sid,
                "turn_type": turn_type_norm,
                "session_done": bool(session_done),
                "success": bool(success),
                "message_count": len(sanitized_messages),
                "messages": sanitized_messages,
                "metadata": _sanitize_metadata(metadata),
            }
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            self._active_session_by_user[uid] = sid
            self._active_session_touch_ms[uid] = int(now_ms)
            current_turn_count = int(self._active_session_turn_count.get(uid) or 0) + 1
            self._active_session_turn_count[uid] = current_turn_count

            if bool(session_done):
                ended_sessions.append(
                    self._close_session_file_locked(
                        user_id=uid,
                        session_id=sid,
                        reason="session_done",
                    )
                )
                self._clear_active_session_locked(user_id=uid, session_id=sid)
            elif int(self.config.session_max_turns or 0) > 0 and current_turn_count >= int(
                self.config.session_max_turns
            ):
                ended_sessions.append(
                    self._close_session_file_locked(
                        user_id=uid,
                        session_id=sid,
                        reason="session_turn_limit",
                    )
                )
                self._clear_active_session_locked(user_id=uid, session_id=sid)

        ended_unique = self._dedupe_ended_sessions(ended_sessions)
        if ended_unique:
            for ended in reversed(ended_unique):
                if _safe_text(ended.get("session_id")) == sid:
                    ended_path = _safe_text(ended.get("path"))
                    if ended_path:
                        current_path = Path(ended_path)
                    break

        return {
            "enabled": True,
            "skipped": False,
            "reason": "",
            "user_id": uid,
            "session_id": sid,
            "path": str(current_path or path),
            "record_id": str(payload["record_id"]),
            "ended_sessions": ended_unique,
        }

    def sweep_inactive_sessions(self, *, user_id: str) -> Dict[str, Any]:
        """
        Close an active session for `user_id` when idle timeout is exceeded.

        This is a safe no-op unless `session_idle_timeout_seconds > 0`.
        """

        uid = _safe_text(user_id)
        if not self.config.enabled:
            return {
                "enabled": False,
                "skipped": True,
                "reason": "archive_disabled",
                "user_id": uid,
                "ended_sessions": [],
            }
        if int(self.config.session_idle_timeout_seconds or 0) <= 0:
            return {
                "enabled": True,
                "skipped": True,
                "reason": "idle_timeout_disabled",
                "user_id": uid,
                "ended_sessions": [],
            }
        if not uid:
            return {
                "enabled": True,
                "skipped": True,
                "reason": "missing_user_id",
                "user_id": uid,
                "ended_sessions": [],
            }

        with self._lock:
            ended = self._close_idle_session_locked(
                user_id=uid,
                now_ms=int(time.time() * 1000),
            )
        ended_unique = self._dedupe_ended_sessions(ended)
        return {
            "enabled": True,
            "skipped": not bool(ended_unique),
            "reason": "" if ended_unique else "idle_not_expired",
            "user_id": uid,
            "ended_sessions": ended_unique,
        }

    def load_session_for_extraction(
        self,
        *,
        path: str,
    ) -> Dict[str, Any]:
        """
        Build a full-session extraction payload from a closed session archive file.
        """

        session_path = Path(_safe_text(path)).expanduser().resolve()
        if not session_path.exists():
            return {
                "ok": False,
                "reason": "session_file_missing",
                "path": str(session_path),
                "messages": [],
                "has_main_turn": False,
                "has_successful_main_turn": False,
                "turn_count": 0,
            }

        records: List[Dict[str, Any]] = []
        for line in session_path.read_text(encoding="utf-8").splitlines():
            text = str(line or "").strip()
            if not text:
                continue
            try:
                obj = json.loads(text)
            except Exception:
                continue
            if isinstance(obj, dict):
                records.append(obj)

        if not records:
            return {
                "ok": False,
                "reason": "session_file_empty",
                "path": str(session_path),
                "messages": [],
                "has_main_turn": False,
                "has_successful_main_turn": False,
                "turn_count": 0,
            }

        merged_messages: List[Dict[str, Any]] = []
        has_main_turn = False
        has_successful_main_turn = False
        session_id = ""
        user_id = ""
        for rec in records:
            turn_type = _safe_text(rec.get("turn_type")).lower()
            success = bool(rec.get("success"))
            if turn_type == "main":
                has_main_turn = True
                if success:
                    has_successful_main_turn = True
            session_id = session_id or _safe_text(rec.get("session_id"))
            user_id = user_id or _safe_text(rec.get("user_id"))
            msg_list = rec.get("messages")
            if not isinstance(msg_list, list):
                continue
            turn_messages = _sanitize_messages(
                msg_list,
                max_messages=int(self.config.max_messages_per_record),
                max_content_chars=int(self.config.max_content_chars),
            )
            merged_messages = self._merge_messages_with_overlap(
                merged_messages,
                turn_messages,
            )

        return {
            "ok": True,
            "reason": "",
            "path": str(session_path),
            "session_id": session_id,
            "user_id": user_id,
            "messages": merged_messages,
            "has_main_turn": bool(has_main_turn),
            "has_successful_main_turn": bool(has_successful_main_turn),
            "turn_count": len(records),
        }

    def _session_file_path(self, *, root: Path, user_id: str, session_id: str) -> Path:
        """Return a stable file path for one user/session pair."""
        user_slug = _slug(user_id or "default", fallback="default")
        session_slug = _slug(session_id, fallback="session")
        return root / "sessions" / user_slug / f"{session_slug}.jsonl"

    def _close_session_file_locked(self, *, user_id: str, session_id: str, reason: str) -> Dict[str, Any]:
        """Rotate the active session file into a closed immutable file."""
        root = Path(self.config.archive_dir).expanduser().resolve()
        src = self._session_file_path(root=root, user_id=user_id, session_id=session_id)
        if not src.exists():
            return {
                "user_id": str(user_id or ""),
                "session_id": str(session_id or ""),
                "reason": str(reason or ""),
                "path": str(src),
                "closed": False,
            }
        closed_suffix = _slug(reason, fallback="closed")
        dst = src.with_name(f"{src.stem}.{int(time.time() * 1000)}.{closed_suffix}.jsonl")
        if dst.exists():
            dst = src.with_name(
                f"{src.stem}.{int(time.time() * 1000)}.{closed_suffix}.{uuid.uuid4().hex[:8]}.jsonl"
            )
        try:
            src.rename(dst)
            path = dst
            closed = True
        except Exception:
            path = src
            closed = False
        return {
            "user_id": str(user_id or ""),
            "session_id": str(session_id or ""),
            "reason": str(reason or ""),
            "path": str(path),
            "closed": bool(closed),
        }

    def _close_idle_session_locked(self, *, user_id: str, now_ms: int) -> List[Dict[str, Any]]:
        """
        Close active session for user when idle timeout is exceeded.

        Caller must hold `self._lock`.
        """

        timeout_s = int(self.config.session_idle_timeout_seconds or 0)
        if timeout_s <= 0:
            return []
        uid = _safe_text(user_id)
        sid = _safe_text(self._active_session_by_user.get(uid))
        if not sid:
            return []
        last_touch = int(self._active_session_touch_ms.get(uid) or 0)
        if last_touch <= 0:
            return []
        if int(now_ms) - last_touch <= timeout_s * 1000:
            return []
        closed = self._close_session_file_locked(
            user_id=uid,
            session_id=sid,
            reason="session_idle_timeout",
        )
        self._clear_active_session_locked(user_id=uid, session_id=sid)
        return [closed]

    def _clear_active_session_locked(self, *, user_id: str, session_id: str = "") -> None:
        """Clear active-session bookkeeping for a user when the expected session matches."""

        uid = _safe_text(user_id)
        sid = _safe_text(session_id)
        if sid and _safe_text(self._active_session_by_user.get(uid)) not in {"", sid}:
            return
        self._active_session_by_user.pop(uid, None)
        self._active_session_touch_ms.pop(uid, None)
        self._active_session_turn_count.pop(uid, None)

    @staticmethod
    def _dedupe_ended_sessions(ended_sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate ended-session records by `(session_id, path)`."""
        ended_unique: List[Dict[str, Any]] = []
        seen: set[Tuple[str, str]] = set()
        for item in list(ended_sessions or []):
            session_key = (_safe_text(item.get("session_id")), _safe_text(item.get("path")))
            if not all(session_key) or session_key in seen:
                continue
            seen.add(session_key)
            ended_unique.append(item)
        return ended_unique

    @staticmethod
    def _merge_messages_with_overlap(
        existing: List[Dict[str, Any]],
        incoming: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Merge turn-level windows into one timeline by removing prefix/suffix overlap.
        """
        base = list(existing or [])
        nxt = list(incoming or [])
        if not base:
            return nxt
        if not nxt:
            return base

        max_overlap = min(len(base), len(nxt))
        overlap = 0
        for size in range(max_overlap, 0, -1):
            if base[-size:] == nxt[:size]:
                overlap = size
                break
        if overlap > 0:
            return base + nxt[overlap:]
        return base + nxt
