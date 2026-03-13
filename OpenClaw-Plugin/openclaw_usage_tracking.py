"""
OpenClaw skill retrieval/usage tracking helpers.

This module is plugin-local and best-effort only:
- never blocks or fails the main OpenClaw request path
- records explicit counters via store.record_skill_usage_judgments when available
- records inferred counters in a plugin-local manifest for observability
- can optionally trigger stale-skill pruning (disabled by default)
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from autoskill.interactive.usage_tracking import build_query_key

_INFER_DUP_WINDOW_MS = 10 * 60 * 1000
_SPACE_RE = re.compile(r"\s+")


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    text = _safe_text(value).lower()
    if not text:
        return bool(default)
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _dedupe_ids(items: List[Any], *, max_items: int = 128) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for raw in list(items or []):
        sid = _safe_text(raw)
        if not sid:
            continue
        key = sid.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(sid)
        if len(out) >= max_items:
            break
    return out


def _skill_id_from_hit(hit: Any) -> str:
    if not isinstance(hit, dict):
        return ""
    sid = _safe_text(hit.get("id"))
    if sid:
        return sid
    skill = hit.get("skill")
    if isinstance(skill, dict):
        return _safe_text(skill.get("id"))
    return ""


def _message_to_text(message: Any) -> str:
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict):
                text = _safe_text(item.get("text") or item.get("content"))
                if text:
                    parts.append(text)
            else:
                text = _safe_text(item)
                if text:
                    parts.append(text)
        return "\n".join(parts)
    if isinstance(content, str):
        return content
    if content is None:
        return ""
    return _safe_text(content)


def _normalize_match_text(text: str) -> str:
    if not text:
        return ""
    lowered = str(text).lower()
    lowered = re.sub(r"[^a-z0-9\u4e00-\u9fff_-]+", " ", lowered)
    return _SPACE_RE.sub(" ", lowered).strip()


def _normalize_hit(hit: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(hit, dict):
        return None
    sid = _skill_id_from_hit(hit)
    if not sid:
        return None
    name = _safe_text(hit.get("name"))
    description = _safe_text(hit.get("description"))
    score_raw = hit.get("score")
    try:
        score = float(score_raw if score_raw is not None else 0.0)
    except Exception:
        score = 0.0
    return {
        "id": sid,
        "name": name,
        "description": description,
        "score": score,
    }


def _extract_hit_list(retrieval: Dict[str, Any], *, max_hits: int) -> List[Dict[str, Any]]:
    buckets: List[Any] = []
    for key in ("hits", "hits_user", "hits_library"):
        value = retrieval.get(key)
        if isinstance(value, list):
            buckets.extend(value)
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for raw in buckets:
        hit = _normalize_hit(raw)
        if hit is None:
            continue
        key = str(hit.get("id") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(hit)
        if len(out) >= max(1, int(max_hits or 8)):
            break
    return out


def _extract_selected_ids(retrieval: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    context_ids = _dedupe_ids(
        list(retrieval.get("selected_for_context_ids") or []),
        max_items=64,
    )
    use_ids = _dedupe_ids(
        list(retrieval.get("selected_for_use_ids") or []),
        max_items=64,
    )
    if context_ids or use_ids:
        return context_ids, use_ids

    selected_raw = retrieval.get("selected_skills")
    if isinstance(selected_raw, list):
        selected_ids: List[str] = []
        for item in selected_raw:
            if isinstance(item, dict):
                sid = _safe_text(item.get("id"))
                if sid:
                    selected_ids.append(sid)
        context_ids = _dedupe_ids(selected_ids, max_items=64)
        use_ids = list(context_ids)
    return context_ids, use_ids


def _snapshot_from_retrieval(
    retrieval: Dict[str, Any],
    *,
    max_hits: int,
) -> Dict[str, Any]:
    source = retrieval if isinstance(retrieval, dict) else {}
    query = (
        _safe_text(source.get("search_query"))
        or _safe_text(source.get("query"))
        or _safe_text(source.get("original_query"))
        or _safe_text(source.get("latest_user_query"))
    )
    hits = _extract_hit_list(source, max_hits=max_hits)
    context_ids, use_ids = _extract_selected_ids(source)
    if not context_ids and hits:
        context_ids = [str(h.get("id") or "") for h in hits if str(h.get("id") or "").strip()]
    if not use_ids and context_ids:
        use_ids = list(context_ids)
    return {
        "query": query,
        "hits": hits,
        "selected_for_context_ids": _dedupe_ids(context_ids, max_items=64),
        "selected_for_use_ids": _dedupe_ids(use_ids, max_items=64),
        "event_time": _safe_int(source.get("event_time"), int(time.time() * 1000)),
    }


@dataclass
class OpenClawUsageTrackingConfig:
    enabled: bool = True
    infer_enabled: bool = True
    infer_from_selected_ids: bool = True
    infer_from_message_mentions: bool = True
    infer_max_message_chars: int = 6000
    infer_manifest_path: str = ""
    prune_enabled: bool = False
    prune_require_explicit_used_signal: bool = True
    prune_min_retrieved: int = 40
    prune_max_used: int = 0
    max_hits_per_turn: int = 8
    max_pending_sessions: int = 4096
    pending_ttl_seconds: int = 6 * 3600

    def normalize(self) -> "OpenClawUsageTrackingConfig":
        self.enabled = bool(self.enabled)
        self.infer_enabled = bool(self.infer_enabled)
        self.infer_from_selected_ids = bool(self.infer_from_selected_ids)
        self.infer_from_message_mentions = bool(self.infer_from_message_mentions)
        self.infer_max_message_chars = max(256, min(48000, int(self.infer_max_message_chars or 6000)))
        self.infer_manifest_path = str(self.infer_manifest_path or "").strip()
        self.prune_enabled = bool(self.prune_enabled)
        self.prune_require_explicit_used_signal = bool(self.prune_require_explicit_used_signal)
        self.prune_min_retrieved = max(0, int(self.prune_min_retrieved or 40))
        self.prune_max_used = max(0, int(self.prune_max_used or 0))
        self.max_hits_per_turn = max(1, min(32, int(self.max_hits_per_turn or 8)))
        self.max_pending_sessions = max(32, int(self.max_pending_sessions or 4096))
        self.pending_ttl_seconds = max(60, int(self.pending_ttl_seconds or (6 * 3600)))
        return self


class OpenClawSkillUsageTracker:
    """
    Best-effort usage tracker for OpenClaw plugin runtime.

    Counters are persisted by delegating to the active AutoSkill store implementation.
    """

    def __init__(self, *, sdk: Any, config: Optional[OpenClawUsageTrackingConfig] = None) -> None:
        self.sdk = sdk
        self.config = (config or OpenClawUsageTrackingConfig()).normalize()
        self._lock = threading.Lock()
        self._pending_by_session: Dict[str, Dict[str, Any]] = {}
        self._inferred_stats_by_user: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._inferred_stats_path = self._resolve_inferred_stats_path()
        self._load_inferred_stats_manifest()

    def status(self) -> Dict[str, Any]:
        with self._lock:
            pending = len(self._pending_by_session)
            inferred_users = len(self._inferred_stats_by_user)
        return {
            "enabled": bool(self.config.enabled),
            "infer_enabled": bool(self.config.infer_enabled),
            "infer_from_selected_ids": bool(self.config.infer_from_selected_ids),
            "infer_from_message_mentions": bool(self.config.infer_from_message_mentions),
            "infer_max_message_chars": int(self.config.infer_max_message_chars),
            "infer_manifest_path": str(self._inferred_stats_path or ""),
            "prune_enabled": bool(self.config.prune_enabled),
            "prune_require_explicit_used_signal": bool(self.config.prune_require_explicit_used_signal),
            "prune_min_retrieved": int(self.config.prune_min_retrieved),
            "prune_max_used": int(self.config.prune_max_used),
            "max_hits_per_turn": int(self.config.max_hits_per_turn),
            "pending_sessions": int(pending),
            "inferred_users": int(inferred_users),
        }

    def _resolve_inferred_stats_path(self) -> str:
        explicit = str(self.config.infer_manifest_path or "").strip()
        if explicit:
            return os.path.abspath(os.path.expanduser(explicit))
        store = getattr(self.sdk, "store", None)
        store_path = _safe_text(getattr(store, "path", ""))
        if not store_path:
            return ""
        root = os.path.abspath(os.path.expanduser(store_path))
        return os.path.join(root, "index", "openclaw_usage_inferred_stats.json")

    def _load_inferred_stats_manifest(self) -> None:
        path = str(self._inferred_stats_path or "").strip()
        if not path:
            self._inferred_stats_by_user = {}
            return
        try:
            if not os.path.exists(path):
                self._inferred_stats_by_user = {}
                return
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f) or {}
            raw_users = payload.get("users") if isinstance(payload, dict) else {}
            out: Dict[str, Dict[str, Dict[str, Any]]] = {}
            if isinstance(raw_users, dict):
                for user_id, raw_bucket in raw_users.items():
                    uid = _safe_text(user_id)
                    if not uid or not isinstance(raw_bucket, dict):
                        continue
                    bucket: Dict[str, Dict[str, Any]] = {}
                    for skill_id, raw_row in raw_bucket.items():
                        sid = _safe_text(skill_id)
                        if not sid or not isinstance(raw_row, dict):
                            continue
                        bucket[sid] = {
                            "retrieved": max(0, _safe_int(raw_row.get("retrieved"), 0)),
                            "relevant": max(0, _safe_int(raw_row.get("relevant"), 0)),
                            "used": max(0, _safe_int(raw_row.get("used"), 0)),
                            "name": _safe_text(raw_row.get("name")),
                            "description": _safe_text(raw_row.get("description")),
                            "last_query_key": _safe_text(raw_row.get("last_query_key")),
                            "last_query_at": max(0, _safe_int(raw_row.get("last_query_at"), 0)),
                            "updated_at": max(0, _safe_int(raw_row.get("updated_at"), 0)),
                            "recent_query_ts": dict(raw_row.get("recent_query_ts") or {}),
                        }
                    if bucket:
                        out[uid] = bucket
            self._inferred_stats_by_user = out
        except Exception:
            self._inferred_stats_by_user = {}

    def _save_inferred_stats_manifest_locked(self) -> None:
        path = str(self._inferred_stats_path or "").strip()
        if not path:
            return
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            payload = {
                "object": "openclaw_usage_inferred_stats",
                "updated_at": int(time.time() * 1000),
                "users": self._inferred_stats_by_user,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        except Exception:
            return

    def _ensure_inferred_row_locked(self, *, user_id: str, skill_id: str, hit: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        uid = _safe_text(user_id)
        sid = _safe_text(skill_id)
        bucket = self._inferred_stats_by_user.setdefault(uid, {})
        row = bucket.setdefault(
            sid,
            {
                "retrieved": 0,
                "relevant": 0,
                "used": 0,
                "name": _safe_text((hit or {}).get("name")),
                "description": _safe_text((hit or {}).get("description")),
                "last_query_key": "",
                "last_query_at": 0,
                "updated_at": 0,
                "recent_query_ts": {},
            },
        )
        if hit:
            name = _safe_text(hit.get("name"))
            desc = _safe_text(hit.get("description"))
            if name:
                row["name"] = name
            if desc:
                row["description"] = desc
        return row

    def _session_key(self, *, user_id: str, session_id: str) -> str:
        return f"{_safe_text(user_id).lower()}::{_safe_text(session_id).lower()}"

    def _evict_expired_locked(self, *, now_ms: int) -> None:
        if not self._pending_by_session:
            return
        ttl_ms = max(1000, int(self.config.pending_ttl_seconds) * 1000)
        stale_keys = []
        for key, item in self._pending_by_session.items():
            ts = _safe_int(item.get("event_time"), 0)
            if ts <= 0 or (now_ms - ts) > ttl_ms:
                stale_keys.append(key)
        for key in stale_keys:
            self._pending_by_session.pop(key, None)

        if len(self._pending_by_session) <= int(self.config.max_pending_sessions):
            return
        # Remove oldest snapshots first.
        ordered = sorted(
            self._pending_by_session.items(),
            key=lambda kv: _safe_int(kv[1].get("event_time"), 0),
        )
        overflow = len(self._pending_by_session) - int(self.config.max_pending_sessions)
        for key, _item in ordered[:overflow]:
            self._pending_by_session.pop(key, None)

    def remember_retrieval(
        self,
        *,
        user_id: str,
        session_id: str,
        retrieval: Dict[str, Any],
    ) -> Dict[str, Any]:
        uid = _safe_text(user_id)
        sid = _safe_text(session_id)
        if not self.config.enabled:
            return {"enabled": False, "status": "skipped", "reason": "usage_tracking_disabled"}
        if not uid or not sid:
            return {"enabled": True, "status": "skipped", "reason": "missing_user_or_session"}

        snapshot = _snapshot_from_retrieval(retrieval or {}, max_hits=int(self.config.max_hits_per_turn))
        if not list(snapshot.get("hits") or []):
            return {"enabled": True, "status": "skipped", "reason": "no_hits_to_track"}

        key = self._session_key(user_id=uid, session_id=sid)
        now_ms = int(time.time() * 1000)
        with self._lock:
            self._evict_expired_locked(now_ms=now_ms)
            self._pending_by_session[key] = {
                **snapshot,
                "event_time": int(snapshot.get("event_time") or now_ms),
                "user_id": uid,
                "session_id": sid,
            }
        return {
            "enabled": True,
            "status": "remembered",
            "reason": "",
            "tracked_hits": len(list(snapshot.get("hits") or [])),
            "session_id": sid,
        }

    def _pop_pending_retrieval(self, *, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        key = self._session_key(user_id=user_id, session_id=session_id)
        with self._lock:
            self._evict_expired_locked(now_ms=int(time.time() * 1000))
            item = self._pending_by_session.pop(key, None)
        return dict(item) if isinstance(item, dict) else None

    @staticmethod
    def _extract_used_ids_from_payload(used_skill_ids: Any) -> List[str]:
        if isinstance(used_skill_ids, list):
            raw = []
            for item in used_skill_ids:
                if isinstance(item, dict):
                    sid = _safe_text(item.get("id") or item.get("skill_id"))
                    if sid:
                        raw.append(sid)
                else:
                    raw.append(_safe_text(item))
            return _dedupe_ids(raw, max_items=64)
        return []

    @staticmethod
    def _extract_inferred_ids_from_payload(inferred_used_skill_ids: Any) -> List[str]:
        if isinstance(inferred_used_skill_ids, list):
            raw = []
            for item in inferred_used_skill_ids:
                if isinstance(item, dict):
                    sid = _safe_text(
                        item.get("id")
                        or item.get("skill_id")
                        or item.get("skillId")
                        or item.get("name")
                    )
                    if sid:
                        raw.append(sid)
                else:
                    raw.append(_safe_text(item))
            return _dedupe_ids(raw, max_items=64)
        return []

    @staticmethod
    def _build_synthetic_snapshot(
        *,
        skill_ids: List[str],
        query: str = "",
    ) -> Dict[str, Any]:
        ids = _dedupe_ids(list(skill_ids or []), max_items=64)
        hits = [{"id": sid, "name": "", "description": "", "score": 1.0} for sid in ids]
        now_ms = int(time.time() * 1000)
        return {
            "query": str(query or ""),
            "hits": hits,
            "selected_for_context_ids": list(ids),
            "selected_for_use_ids": list(ids),
            "event_time": now_ms,
        }

    def _infer_used_ids_from_messages(
        self,
        *,
        snapshot: Dict[str, Any],
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        if not bool(self.config.infer_from_message_mentions):
            return []
        limit = max(256, int(self.config.infer_max_message_chars or 6000))
        chunks: List[str] = []
        used = 0
        for msg in list(messages or []):
            role = _safe_text((msg or {}).get("role")).lower()
            if role == "user":
                continue
            text = _message_to_text(msg).strip()
            if not text:
                continue
            left = max(0, limit - used)
            if left <= 0:
                break
            piece = text[:left]
            chunks.append(piece)
            used += len(piece)
            if used >= limit:
                break
        body = _normalize_match_text("\n".join(chunks))
        if not body:
            return []

        out: List[str] = []
        seen: set[str] = set()
        for hit in list(snapshot.get("hits") or []):
            sid = _skill_id_from_hit(hit)
            if not sid:
                continue
            sid_key = sid.lower()
            sid_norm = _normalize_match_text(sid)
            name_norm = _normalize_match_text(_safe_text((hit or {}).get("name")))
            matched = False
            if sid_norm and len(sid_norm) >= 4 and sid_norm in body:
                matched = True
            if (not matched) and name_norm and len(name_norm) >= 4 and name_norm in body:
                matched = True
            if not matched:
                continue
            if sid_key in seen:
                continue
            seen.add(sid_key)
            out.append(sid)
        return out

    def _resolve_inferred_used_ids(
        self,
        *,
        snapshot: Dict[str, Any],
        explicit_used_ids: List[str],
        payload_inferred_ids: List[str],
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        explicit_set = {sid.lower() for sid in list(explicit_used_ids or [])}
        out: List[str] = []
        seen: set[str] = set()

        def _add(raw_ids: List[str]) -> None:
            for sid in list(raw_ids or []):
                val = _safe_text(sid)
                if not val:
                    continue
                key = val.lower()
                if key in explicit_set or key in seen:
                    continue
                seen.add(key)
                out.append(val)

        _add(_dedupe_ids(list(payload_inferred_ids or []), max_items=64))
        if bool(self.config.infer_from_selected_ids):
            _add(_dedupe_ids(list(snapshot.get("selected_for_use_ids") or []), max_items=64))
            _add(_dedupe_ids(list(snapshot.get("selected_for_context_ids") or []), max_items=64))
        _add(self._infer_used_ids_from_messages(snapshot=snapshot, messages=messages))
        return out[:64]

    def _build_judgments(
        self,
        *,
        snapshot: Dict[str, Any],
        used_ids: List[str],
        mode: str = "explicit",
    ) -> List[Dict[str, Any]]:
        hits = list(snapshot.get("hits") or [])
        if not hits:
            return []
        selected_context = _dedupe_ids(list(snapshot.get("selected_for_context_ids") or []), max_items=64)
        selected_use = _dedupe_ids(list(snapshot.get("selected_for_use_ids") or []), max_items=64)
        selected_set = {sid.lower() for sid in [*selected_context, *selected_use]}
        used_set = {sid.lower() for sid in list(used_ids or [])}
        query_key = build_query_key(str(snapshot.get("query") or ""))

        judgments: List[Dict[str, Any]] = []
        for hit in hits:
            sid = _skill_id_from_hit(hit)
            if not sid:
                continue
            key = sid.lower()
            relevant = bool(key in selected_set) or (not selected_set)
            used = bool(key in used_set) and relevant
            judgments.append(
                {
                    "id": sid,
                    "relevant": bool(relevant),
                    "used": bool(used),
                    "query_key": query_key,
                    "mode": str(mode or "explicit"),
                    "reason": (
                        f"openclaw_{mode}_used"
                        if used
                        else (
                            f"openclaw_{mode}_selected"
                            if relevant
                            else f"openclaw_{mode}_not_selected"
                        )
                    ),
                }
            )
        return judgments

    def _record_inferred_judgments(
        self,
        *,
        user_id: str,
        judgments: List[Dict[str, Any]],
        snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        uid = _safe_text(user_id)
        if not uid:
            return {"status": "skipped", "reason": "missing_user_id", "updated": 0, "stats": {}}
        if not judgments:
            return {"status": "skipped", "reason": "no_judgments", "updated": 0, "stats": {}}
        now_ms = int(time.time() * 1000)
        updated = 0
        touched: List[str] = []
        with self._lock:
            bucket = self._inferred_stats_by_user.setdefault(uid, {})
            for item in list(judgments or []):
                sid = _safe_text(item.get("id"))
                if not sid:
                    continue
                hit = None
                for h in list(snapshot.get("hits") or []):
                    if _skill_id_from_hit(h).lower() == sid.lower():
                        hit = h
                        break
                row = self._ensure_inferred_row_locked(user_id=uid, skill_id=sid, hit=hit)
                qkey = _safe_text(item.get("query_key"))
                recent_map = dict(row.get("recent_query_ts") or {})
                normalized_recent: Dict[str, int] = {}
                for key, value in recent_map.items():
                    kk = _safe_text(key)
                    if not kk:
                        continue
                    vv = _safe_int(value, 0)
                    if vv > 0:
                        normalized_recent[kk] = vv
                cutoff = now_ms - _INFER_DUP_WINDOW_MS
                normalized_recent = {k: v for k, v in normalized_recent.items() if int(v) >= cutoff}
                duplicate_query = bool(
                    qkey
                    and (qkey in normalized_recent)
                    and int(normalized_recent.get(qkey, 0)) > 0
                    and (now_ms - int(normalized_recent.get(qkey, 0))) <= _INFER_DUP_WINDOW_MS
                )
                if not duplicate_query:
                    row["retrieved"] = int(row.get("retrieved", 0)) + 1
                relevant = bool(item.get("relevant", False))
                used = bool(item.get("used", False)) and relevant
                if relevant and not duplicate_query:
                    row["relevant"] = int(row.get("relevant", 0)) + 1
                if used and ((not duplicate_query) or int(row.get("used", 0) or 0) <= 0):
                    row["used"] = int(row.get("used", 0)) + 1
                if qkey:
                    row["last_query_key"] = qkey
                    row["last_query_at"] = now_ms
                    normalized_recent[qkey] = now_ms
                if len(normalized_recent) > 64:
                    pairs = sorted(normalized_recent.items(), key=lambda kv: int(kv[1]), reverse=True)[:32]
                    normalized_recent = {k: int(v) for k, v in pairs}
                row["recent_query_ts"] = normalized_recent
                row["updated_at"] = now_ms
                bucket[sid] = row
                touched.append(sid)
                updated += 1
            self._save_inferred_stats_manifest_locked()

            stats: Dict[str, Dict[str, int]] = {}
            for sid in touched:
                row = bucket.get(sid)
                if not isinstance(row, dict):
                    continue
                stats[sid] = {
                    "retrieved": int(row.get("retrieved", 0) or 0),
                    "relevant": int(row.get("relevant", 0) or 0),
                    "used": int(row.get("used", 0) or 0),
                }
        return {"status": "recorded", "reason": "", "updated": int(updated), "stats": stats}

    def _read_inferred_stats(self, *, user_id: str, skill_id: str = "") -> Dict[str, Any]:
        uid = _safe_text(user_id)
        sid = _safe_text(skill_id)
        with self._lock:
            bucket = dict(self._inferred_stats_by_user.get(uid) or {})
        if sid:
            row = bucket.get(sid)
            if not isinstance(row, dict):
                return {"skills": {}}
            return {
                "skills": {
                    sid: {
                        "retrieved": int(row.get("retrieved", 0) or 0),
                        "relevant": int(row.get("relevant", 0) or 0),
                        "used": int(row.get("used", 0) or 0),
                    }
                }
            }
        out: Dict[str, Dict[str, int]] = {}
        for key, row in bucket.items():
            if not isinstance(row, dict):
                continue
            out[str(key)] = {
                "retrieved": int(row.get("retrieved", 0) or 0),
                "relevant": int(row.get("relevant", 0) or 0),
                "used": int(row.get("used", 0) or 0),
            }
        return {"skills": out}

    def record_agent_end(
        self,
        *,
        user_id: str,
        session_id: str,
        retrieval: Optional[Dict[str, Any]] = None,
        used_skill_ids: Optional[List[Any]] = None,
        inferred_used_skill_ids: Optional[List[Any]] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        uid = _safe_text(user_id)
        sid = _safe_text(session_id)
        if not self.config.enabled:
            return {"enabled": False, "status": "skipped", "reason": "usage_tracking_disabled"}
        if not uid:
            return {"enabled": True, "status": "skipped", "reason": "missing_user_id"}

        recorder = getattr(getattr(self.sdk, "store", None), "record_skill_usage_judgments", None)
        if not callable(recorder):
            return {
                "enabled": True,
                "status": "skipped",
                "reason": "store_usage_tracking_unsupported",
            }

        explicit_snapshot: Dict[str, Any] = {}
        if isinstance(retrieval, dict):
            explicit_snapshot = _snapshot_from_retrieval(
                retrieval,
                max_hits=int(self.config.max_hits_per_turn),
            )
        cached_snapshot = self._pop_pending_retrieval(user_id=uid, session_id=sid) if sid else None

        snapshot = explicit_snapshot if list(explicit_snapshot.get("hits") or []) else (cached_snapshot or {})
        used_ids = self._extract_used_ids_from_payload(list(used_skill_ids or []))
        payload_inferred_ids = self._extract_inferred_ids_from_payload(list(inferred_used_skill_ids or []))

        source = (
            "agent_end_payload"
            if list(explicit_snapshot.get("hits") or [])
            else ("before_agent_start_cache" if cached_snapshot else "none")
        )
        if not list(snapshot.get("hits") or []):
            fallback_ids = list(used_ids or []) or list(payload_inferred_ids or [])
            if fallback_ids:
                snapshot = self._build_synthetic_snapshot(
                    skill_ids=fallback_ids,
                    query="openclaw_used_signal_fallback",
                )
                source = (
                    "explicit_used_fallback"
                    if list(used_ids or [])
                    else "inferred_used_fallback"
                )
            else:
                return {"enabled": True, "status": "skipped", "reason": "no_retrieval_hits"}

        judgments = self._build_judgments(snapshot=snapshot, used_ids=used_ids, mode="explicit")
        if not judgments:
            return {"enabled": True, "status": "skipped", "reason": "no_judgments"}

        prune_allowed = bool(self.config.prune_enabled)
        if prune_allowed and bool(self.config.prune_require_explicit_used_signal) and not list(used_ids or []):
            prune_allowed = False
        prune_min = int(self.config.prune_min_retrieved) if prune_allowed else 0
        prune_max = int(self.config.prune_max_used) if prune_allowed else 0
        try:
            result = recorder(
                user_id=uid,
                judgments=list(judgments),
                prune_min_retrieved=prune_min,
                prune_max_used=prune_max,
            )
        except Exception as e:
            return {
                "enabled": True,
                "status": "failed",
                "reason": f"record_failed:{e}",
            }

        inferred_ids: List[str] = []
        infer_status: Dict[str, Any] = {
            "enabled": bool(self.config.infer_enabled),
            "status": "skipped",
            "reason": "infer_disabled",
            "updated": 0,
            "stats": {},
        }
        if bool(self.config.infer_enabled):
            if list(used_ids or []):
                infer_status = {
                    "enabled": True,
                    "status": "skipped",
                    "reason": "explicit_used_present",
                    "updated": 0,
                    "stats": {},
                }
            else:
                inferred_ids = self._resolve_inferred_used_ids(
                    snapshot=snapshot,
                    explicit_used_ids=used_ids,
                    payload_inferred_ids=payload_inferred_ids,
                    messages=messages,
                )
                inferred_judgments = self._build_judgments(
                    snapshot=snapshot,
                    used_ids=inferred_ids,
                    mode="inferred",
                )
                infer_result = self._record_inferred_judgments(
                    user_id=uid,
                    judgments=inferred_judgments,
                    snapshot=snapshot,
                )
                infer_status = {
                    "enabled": True,
                    "status": str(infer_result.get("status") or "skipped"),
                    "reason": str(infer_result.get("reason") or ""),
                    "updated": int(infer_result.get("updated", 0) or 0),
                    "stats": dict(infer_result.get("stats") or {}),
                }

        return {
            "enabled": True,
            "status": "recorded",
            "reason": "",
            "tracked_hits": len(list(snapshot.get("hits") or [])),
            "updated": int((result or {}).get("updated", 0) or 0),
            "deleted_skill_ids": [str(x) for x in ((result or {}).get("deleted_skill_ids") or []) if str(x)],
            "stats": dict((result or {}).get("stats") or {}),
            "used_skill_ids": list(used_ids),
            "inferred_used_skill_ids": list(inferred_ids),
            "usage_inference": infer_status,
            "prune_applied": bool(prune_allowed),
            "source": source,
        }

    def get_stats(self, *, user_id: str, skill_id: str = "") -> Dict[str, Any]:
        uid = _safe_text(user_id)
        sid = _safe_text(skill_id)
        if not self.config.enabled:
            return {"enabled": False, "skills": {}}
        reader = getattr(getattr(self.sdk, "store", None), "get_skill_usage_stats", None)
        if not callable(reader):
            return {"enabled": True, "skills": {}, "reason": "store_usage_tracking_unsupported"}
        try:
            payload = reader(user_id=uid, skill_id=sid)
        except Exception as e:
            return {"enabled": True, "skills": {}, "reason": f"stats_failed:{e}"}
        out = dict(payload or {})
        explicit_skills = dict(out.get("skills") or {})
        inferred_payload = self._read_inferred_stats(user_id=uid, skill_id=sid)
        inferred_skills = dict(inferred_payload.get("skills") or {})
        all_ids = sorted(set(explicit_skills.keys()) | set(inferred_skills.keys()))
        combined: Dict[str, Dict[str, Any]] = {}
        for skill in all_ids:
            explicit_row = dict(explicit_skills.get(skill) or {})
            inferred_row = dict(inferred_skills.get(skill) or {})
            combined[skill] = {
                "retrieved": int(explicit_row.get("retrieved", 0) or 0)
                + int(inferred_row.get("retrieved", 0) or 0),
                "relevant": int(explicit_row.get("relevant", 0) or 0)
                + int(inferred_row.get("relevant", 0) or 0),
                "used": int(explicit_row.get("used", 0) or 0)
                + int(inferred_row.get("used", 0) or 0),
                "explicit": {
                    "retrieved": int(explicit_row.get("retrieved", 0) or 0),
                    "relevant": int(explicit_row.get("relevant", 0) or 0),
                    "used": int(explicit_row.get("used", 0) or 0),
                },
                "inferred": {
                    "retrieved": int(inferred_row.get("retrieved", 0) or 0),
                    "relevant": int(inferred_row.get("relevant", 0) or 0),
                    "used": int(inferred_row.get("used", 0) or 0),
                },
            }
        out["enabled"] = True
        out["skills_explicit"] = explicit_skills
        out["skills_inferred"] = inferred_skills
        out["skills_combined"] = combined
        out["prune_source"] = "skills_explicit"
        return out
