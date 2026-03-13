"""
OpenClaw-focused AutoSkill runtime.

This runtime keeps retrieval/evolution APIs and disables chat-generation endpoints.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from autoskill.interactive.server import (
    AutoSkillProxyRuntime,
    _json_response,
    _normalize_messages,
    _normalize_scope,
    _openai_error,
    _parse_bool,
    _safe_float,
    _safe_int,
)
from openclaw_main_turn_proxy import (
    MainTurnSample,
    OpenClawMainTurnProxyConfig,
    OpenClawMainTurnStateManager,
    UpstreamChatProxy,
    parse_turn_context,
)
from openclaw_conversation_archive import (
    OpenClawConversationArchive,
    OpenClawConversationArchiveConfig,
)
from openclaw_skill_mirror import OpenClawSkillInstallConfig, OpenClawSkillMirror
from openclaw_usage_tracking import (
    OpenClawSkillUsageTracker,
    OpenClawUsageTrackingConfig,
)


@dataclass
class _OpenClawExtractJob:
    job_id: str
    user_id: str
    window: List[Dict[str, Any]]
    trigger: str
    hint: Optional[str]
    retrieval_reference: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    event_fields: Optional[Dict[str, Any]] = None
    dedupe_key: Optional[str] = None


class OpenClawSkillRuntime(AutoSkillProxyRuntime):
    """
    Runtime specialized for OpenClaw plugin mode.

    The service does not act as a chat model proxy. It focuses on:
    - query rewrite + skill retrieval
    - background extraction/update scheduling
    - skill management APIs
    """

    def __init__(
        self,
        *,
        sdk: Any,
        llm_config: Dict[str, Any],
        embeddings_config: Dict[str, Any],
        config: Optional[Any] = None,
        query_rewriter: Optional[Any] = None,
        skill_selector: Optional[Any] = None,
        main_turn_proxy_config: Optional[OpenClawMainTurnProxyConfig] = None,
        skill_install_config: Optional[OpenClawSkillInstallConfig] = None,
        conversation_archive_config: Optional[OpenClawConversationArchiveConfig] = None,
        usage_tracking_config: Optional[OpenClawUsageTrackingConfig] = None,
    ) -> None:
        """Run init."""
        super().__init__(
            sdk=sdk,
            llm_config=llm_config,
            embeddings_config=embeddings_config,
            config=config,
            query_rewriter=query_rewriter,
            skill_selector=skill_selector,
        )
        proxy_cfg = main_turn_proxy_config or OpenClawMainTurnProxyConfig(
            enabled=True,
            ingest_window=int(self.config.ingest_window),
            agent_end_extract_enabled=True,
        )
        if int(proxy_cfg.ingest_window or 0) <= 0:
            proxy_cfg.ingest_window = int(self.config.ingest_window)
        self.main_turn_proxy_config = proxy_cfg.normalize()
        self._main_turn_proxy = UpstreamChatProxy(config=self.main_turn_proxy_config)
        self._main_turn_state = OpenClawMainTurnStateManager(
            config=self.main_turn_proxy_config,
            schedule_extraction=self._schedule_main_turn_extraction_job,
        )
        self.conversation_archive_config = (
            conversation_archive_config or OpenClawConversationArchiveConfig()
        ).normalize()
        self._conversation_archive = OpenClawConversationArchive(config=self.conversation_archive_config)
        self.skill_install_config = (skill_install_config or OpenClawSkillInstallConfig()).normalize()
        self._skill_mirror = OpenClawSkillMirror(config=self.skill_install_config)
        self.usage_tracking_config = (usage_tracking_config or OpenClawUsageTrackingConfig()).normalize()
        self._usage_tracker = OpenClawSkillUsageTracker(
            sdk=self.sdk,
            config=self.usage_tracking_config,
        )
        self._openclaw_extract_dedupe_lock = threading.Lock()
        self._openclaw_extract_dedupe_seen: Dict[str, int] = {}
        self._openclaw_extract_dedupe_max_entries = max(
            512,
            int(self.main_turn_proxy_config.dedupe_max_entries or 4096),
        )
        self._sync_openclaw_installed_skills(
            user_id=str(self.skill_install_config.install_user_id or self.config.user_id or "").strip(),
            reason="runtime_startup",
        )

    def capabilities(self) -> Dict[str, Any]:
        """Run capabilities."""
        payload = dict(super().capabilities() or {})
        data = dict(payload.get("data") or {})
        if self.main_turn_proxy_config.chat_endpoint_enabled:
            data["chat"] = {
                "path": "/v1/chat/completions",
                "stream": True,
                "mode": "openclaw_main_turn_proxy",
            }
        else:
            data.pop("chat", None)
        data.pop("embeddings", None)
        data["openclaw"] = {
            "turn": "/v1/autoskill/openclaw/turn",
            "skills_sync": "/v1/autoskill/openclaw/skills/sync",
            "usage_stats": "/v1/autoskill/openclaw/usage/stats",
            "hooks_before_agent_start": "/v1/autoskill/openclaw/hooks/before_agent_start",
            "hooks_agent_end": "/v1/autoskill/openclaw/hooks/agent_end",
            "retrieve_preview": "/v1/autoskill/retrieval/preview",
            "import_conversations": "/v1/autoskill/conversations/import",
            "main_turn_proxy": {
                "chat": "/v1/chat/completions",
                "enabled": bool(self.main_turn_proxy_config.enabled),
                "target_configured": bool(self.main_turn_proxy_config.chat_endpoint_enabled),
                "agent_end_extract_enabled": bool(self.main_turn_proxy_config.agent_end_extract_enabled),
            },
            "conversation_archive": self._conversation_archive.status(),
            "skill_install_mirror": self._skill_mirror.status(),
            "usage_tracking": self._usage_tracker.status(),
        }
        payload["data"] = data
        return payload

    def openapi_spec(self) -> Dict[str, Any]:
        """Run openapi spec."""
        spec = dict(super().openapi_spec() or {})
        paths = dict(spec.get("paths") or {})
        if not self.main_turn_proxy_config.chat_endpoint_enabled:
            paths.pop("/v1/chat/completions", None)
        else:
            paths["/v1/chat/completions"] = {
                "post": {"summary": "OpenAI-compatible main-turn proxy to the real model backend"}
            }
        paths.pop("/v1/embeddings", None)
        paths["/v1/autoskill/openclaw/turn"] = {
            "post": {"summary": "Retrieve skills for a turn and schedule background extraction"}
        }
        paths["/v1/autoskill/openclaw/skills/sync"] = {
            "post": {"summary": "Sync active AutoSkill skills into the local OpenClaw skills folder"}
        }
        paths["/v1/autoskill/openclaw/usage/stats"] = {
            "post": {"summary": "Get OpenClaw skill retrieval/usage counters for one user"}
        }
        paths["/v1/autoskill/openclaw/hooks/before_agent_start"] = {
            "post": {"summary": "Hook adapter: retrieve skills and return context injection payload"}
        }
        paths["/v1/autoskill/openclaw/hooks/agent_end"] = {
            "post": {"summary": "Hook adapter: schedule asynchronous extraction/evolution after task end"}
        }
        spec["paths"] = paths
        return spec

    def _sync_openclaw_installed_skills(self, *, user_id: str, reason: str) -> Dict[str, Any]:
        """Mirror active user skills into the OpenClaw skill directory when enabled."""
        uid = str(user_id or "").strip()
        if not self.skill_install_config.enabled:
            return {
                "enabled": False,
                "skipped": True,
                "reason": "install_mode_disabled",
                "user_id": uid,
                "skills_dir": str(self.skill_install_config.skills_dir),
            }
        try:
            result = self._skill_mirror.sync_user_skills(
                sdk=self.sdk,
                user_id=uid,
                reason=reason,
            )
        except Exception as e:
            print(
                f"[openclaw-skill-mirror] sync failed user={uid or '<empty>'} "
                f"reason={reason} error={e}"
            )
            return {
                "enabled": True,
                "skipped": True,
                "reason": f"sync_failed:{e}",
                "user_id": uid,
                "skills_dir": str(self.skill_install_config.skills_dir),
                "synced_count": 0,
                "removed_count": 0,
                "folders": [],
            }
        return {
            "enabled": bool(result.enabled),
            "skipped": bool(result.skipped),
            "reason": str(result.reason or ""),
            "user_id": str(result.user_id or ""),
            "skills_dir": str(result.skills_dir or ""),
            "synced_count": int(result.synced_count),
            "removed_count": int(result.removed_count),
            "folders": list(result.folders or []),
        }

    def _resolve_turn_type(self, *, body: Dict[str, Any], headers: Any) -> str:
        metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
        raw = (
            headers.get("X-Turn-Type")
            or body.get("turn_type")
            or body.get("turnType")
            or metadata.get("turn_type")
            or metadata.get("turnType")
        )
        return str(raw or "").strip().lower()

    def _resolve_session_id(self, *, body: Dict[str, Any], headers: Any) -> str:
        metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
        raw = (
            headers.get("X-Session-Id")
            or body.get("session_id")
            or body.get("sessionId")
            or metadata.get("session_id")
            or metadata.get("sessionId")
        )
        return str(raw or "").strip()

    def _resolve_session_done(self, *, body: Dict[str, Any], headers: Any) -> bool:
        metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
        raw = (
            headers.get("X-Session-Done")
            or body.get("session_done")
            or body.get("sessionDone")
            or body.get("done")
            or metadata.get("session_done")
            or metadata.get("sessionDone")
        )
        return _parse_bool(raw, default=False)

    def _archive_conversation(
        self,
        *,
        user_id: str,
        source: str,
        messages: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            return self._conversation_archive.append_record(
                user_id=user_id,
                source=source,
                messages=list(messages or []),
                metadata=dict(metadata or {}),
            )
        except Exception as e:
            print(
                f"[openclaw-conversation-archive] append failed user={user_id or '<empty>'} "
                f"source={source} error={e}"
            )
            return {
                "enabled": bool(self.conversation_archive_config.enabled),
                "skipped": True,
                "reason": f"archive_failed:{e}",
                "user_id": str(user_id or ""),
            }

    def _extract_used_skill_ids(self, *, body: Dict[str, Any]) -> List[str]:
        """Resolve explicit used-skill ids from OpenClaw payload when available."""
        out: List[str] = []
        seen: set[str] = set()

        def _add(raw: Any) -> None:
            if raw is None:
                return
            if isinstance(raw, list):
                for item in raw:
                    _add(item)
                return
            sid = ""
            if isinstance(raw, dict):
                sid = str(raw.get("id") or raw.get("skill_id") or "").strip()
            else:
                sid = str(raw or "").strip()
            if not sid:
                return
            key = sid.lower()
            if key in seen:
                return
            seen.add(key)
            out.append(sid)

        candidates = [
            body.get("used_skill_ids"),
            body.get("usedSkillIds"),
            body.get("skills_used"),
            body.get("skillsUsed"),
        ]
        usage_block = body.get("usage")
        if isinstance(usage_block, dict):
            candidates.extend(
                [
                    usage_block.get("used_skill_ids"),
                    usage_block.get("usedSkillIds"),
                    usage_block.get("skills_used"),
                    usage_block.get("skillsUsed"),
                ]
            )
        metadata = body.get("metadata")
        if isinstance(metadata, dict):
            candidates.extend(
                [
                    metadata.get("used_skill_ids"),
                    metadata.get("usedSkillIds"),
                    metadata.get("skills_used"),
                    metadata.get("skillsUsed"),
                ]
            )
        for item in candidates:
            _add(item)
        return out[:64]

    def _extract_inferred_used_skill_ids(self, *, body: Dict[str, Any]) -> List[str]:
        """Resolve inferred used-skill ids from optional payload hints."""
        out: List[str] = []
        seen: set[str] = set()

        def _add(raw: Any) -> None:
            if raw is None:
                return
            if isinstance(raw, list):
                for item in raw:
                    _add(item)
                return
            sid = ""
            if isinstance(raw, dict):
                sid = str(
                    raw.get("id")
                    or raw.get("skill_id")
                    or raw.get("skillId")
                    or raw.get("name")
                    or ""
                ).strip()
            else:
                sid = str(raw or "").strip()
            if not sid:
                return
            key = sid.lower()
            if key in seen:
                return
            seen.add(key)
            out.append(sid)

        retrieval = body.get("retrieval") if isinstance(body.get("retrieval"), dict) else {}
        metadata = body.get("metadata") if isinstance(body.get("metadata"), dict) else {}
        usage_block = body.get("usage") if isinstance(body.get("usage"), dict) else {}
        candidates: List[Any] = [
            body.get("inferred_used_skill_ids"),
            body.get("inferredUsedSkillIds"),
            body.get("selected_for_use_ids"),
            body.get("selectedForUseIds"),
            body.get("selected_for_context_ids"),
            body.get("selectedForContextIds"),
            body.get("selected_skills"),
            body.get("selectedSkills"),
            retrieval.get("selected_for_use_ids"),
            retrieval.get("selectedForUseIds"),
            retrieval.get("selected_for_context_ids"),
            retrieval.get("selectedForContextIds"),
            retrieval.get("selected_skills"),
            retrieval.get("selectedSkills"),
            metadata.get("inferred_used_skill_ids"),
            metadata.get("inferredUsedSkillIds"),
            metadata.get("selected_for_use_ids"),
            metadata.get("selectedForUseIds"),
            usage_block.get("inferred_used_skill_ids"),
            usage_block.get("inferredUsedSkillIds"),
        ]
        for item in candidates:
            _add(item)
        return out[:64]

    def _track_openclaw_usage(
        self,
        *,
        user_id: str,
        session_id: str,
        retrieval: Optional[Dict[str, Any]],
        used_skill_ids: Optional[List[str]],
        inferred_used_skill_ids: Optional[List[str]],
        messages: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Record retrieval/usage counters in best-effort mode."""
        try:
            result = self._usage_tracker.record_agent_end(
                user_id=user_id,
                session_id=session_id,
                retrieval=(dict(retrieval) if isinstance(retrieval, dict) else None),
                used_skill_ids=list(used_skill_ids or []),
                inferred_used_skill_ids=list(inferred_used_skill_ids or []),
                messages=list(messages or []),
            )
        except Exception as e:
            print(
                f"[openclaw-usage-tracking] record failed user={user_id or '<empty>'} "
                f"session={session_id or '<empty>'} error={e}"
            )
            return {
                "enabled": bool(self.usage_tracking_config.enabled),
                "status": "failed",
                "reason": f"tracker_failed:{e}",
            }
        return dict(result or {})

    def openclaw_usage_stats_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """Get usage counters for one user (and optionally one skill)."""
        user_id = (
            str(body.get("user") or body.get("user_id") or "").strip()
            or self._resolve_user_id(body=body, headers=headers)
        )
        skill_id = str(body.get("skill_id") or body.get("skillId") or "").strip()
        payload = self._usage_tracker.get_stats(user_id=user_id, skill_id=skill_id)
        return {
            "object": "openclaw_usage_stats",
            "ok": True,
            "user": user_id,
            "skill_id": skill_id or None,
            "data": payload,
        }

    def openclaw_skill_sync_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """Force a mirror sync into the OpenClaw skills directory."""
        user_id = (
            str(body.get("user") or body.get("user_id") or "").strip()
            or str(self.skill_install_config.install_user_id or "").strip()
            or str(self.config.user_id or "").strip()
            or self._resolve_user_id(body=body, headers=headers)
        )
        result = self._sync_openclaw_installed_skills(
            user_id=user_id,
            reason="manual_api",
        )
        return {
            "object": "openclaw_skill_sync",
            "ok": not bool(result.get("skipped")),
            "data": result,
        }

    def save_skill_md_api(self, *, path: str, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """Sync OpenClaw-installed skills after manual SKILL.md edits."""
        payload = super().save_skill_md_api(path=path, body=body, headers=headers)
        if int(payload.get("_status", 200)) < 400 and payload.get("ok"):
            user_id = self._resolve_user_id(body=body, headers=headers)
            payload["openclaw_install"] = self._sync_openclaw_installed_skills(
                user_id=user_id,
                reason="save_skill_md",
            )
        return payload

    def rollback_skill_api(self, *, path: str, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """Sync OpenClaw-installed skills after rollbacks."""
        payload = super().rollback_skill_api(path=path, body=body, headers=headers)
        if int(payload.get("_status", 200)) < 400 and payload.get("ok"):
            user_id = self._resolve_user_id(body=body, headers=headers)
            payload["openclaw_install"] = self._sync_openclaw_installed_skills(
                user_id=user_id,
                reason="rollback_skill",
            )
        return payload

    def import_skills_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """Sync OpenClaw-installed skills after importing skill directories."""
        payload = super().import_skills_api(body=body, headers=headers)
        if int(payload.get("_status", 200)) < 400 and payload.get("ok"):
            user_id = self._resolve_user_id(body=body, headers=headers)
            payload["openclaw_install"] = self._sync_openclaw_installed_skills(
                user_id=user_id,
                reason="import_skills",
            )
        return payload

    def import_conversations_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """Sync OpenClaw-installed skills after offline conversation extraction."""
        payload = super().import_conversations_api(body=body, headers=headers)
        if int(payload.get("_status", 200)) < 400 and payload.get("ok"):
            user_id = self._resolve_user_id(body=body, headers=headers)
            payload["openclaw_install"] = self._sync_openclaw_installed_skills(
                user_id=user_id,
                reason="import_conversations",
            )
        return payload

    def delete_skill_api(self, *, path: str, headers: Any) -> Dict[str, Any]:
        """Sync OpenClaw-installed skills after deletes."""
        skill_id, _tail = self._parse_skill_path(path)
        skill = self.sdk.get(skill_id) if skill_id else None
        user_id = str(getattr(skill, "user_id", "") or "").strip()
        payload = super().delete_skill_api(path=path, headers=headers)
        if int(payload.get("_status", 200)) < 400 and payload.get("ok"):
            payload["openclaw_install"] = self._sync_openclaw_installed_skills(
                user_id=user_id,
                reason="delete_skill",
            )
        return payload

    def _build_agent_end_window(
        self,
        *,
        messages: List[Dict[str, str]],
        feedback: str,
    ) -> List[Dict[str, str]]:
        """
        Build extraction window for end-of-task hook.

        Unlike `/turn`, `agent_end` is often called when the last role is assistant.
        We keep a recent mixed window and optionally append user feedback.
        """

        out = list(messages or [])
        fb = str(feedback or "").strip()
        if fb:
            out.append({"role": "user", "content": fb})
        if not out:
            return []
        out = out[-int(self.config.ingest_window) :]
        has_user = any(str((m or {}).get("role") or "").strip().lower() == "user" for m in out)
        has_assistant = any(str((m or {}).get("role") or "").strip().lower() == "assistant" for m in out)
        if not has_user or not has_assistant:
            return []
        return out

    def _build_session_end_window(self, *, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Build extraction window for a closed session archive.

        Session-end extraction keeps the merged full session messages and only
        checks that user+assistant evidence exists.
        """

        out = list(messages or [])
        if not out:
            return []
        has_user = any(str((m or {}).get("role") or "").strip().lower() == "user" for m in out)
        has_assistant = any(str((m or {}).get("role") or "").strip().lower() == "assistant" for m in out)
        if not has_user or not has_assistant:
            return []
        return out

    @staticmethod
    def _merge_ended_sessions(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate ended-session records by `(session_id, path)`."""
        out: List[Dict[str, Any]] = []
        seen: set[Tuple[str, str]] = set()
        for item in list(items or []):
            sid = str(item.get("session_id") or "").strip()
            path = str(item.get("path") or "").strip()
            key = (sid, path)
            if not sid or not path or key in seen:
                continue
            seen.add(key)
            out.append(dict(item))
        return out

    def _session_has_main_turn_extraction_event(self, *, user_id: str, session_id: str) -> bool:
        """
        Return True when we already have non-failed main-turn extraction events for this session.

        This provides cross-trigger hard dedupe for:
        - main-turn proxy extraction
        - agent_end session-close extraction fallback
        """

        uid = str(user_id or "").strip() or self.config.user_id
        sid = str(session_id or "").strip()
        if not sid:
            return False
        with self._extract_events_lock:
            events = list(self._extract_events_by_user.get(uid) or [])
        for ev in reversed(events):
            if str(ev.get("trigger") or "").strip() != "openclaw_main_turn_proxy":
                continue
            if str(ev.get("session_id") or "").strip() != sid:
                continue
            status = str(ev.get("status") or "").strip().lower()
            if status in {"scheduled", "running", "completed"}:
                return True
        return False

    def _build_openclaw_extraction_dedupe_key(
        self,
        *,
        user_id: str,
        messages: List[Dict[str, Any]],
        trigger: str,
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Build a stable dedupe key for OpenClaw extraction scheduling."""

        meta = dict(metadata or {})
        explicit = str(meta.get("dedupe_key") or "").strip()
        if explicit:
            return explicit

        source = str(meta.get("source") or trigger or "").strip().lower()
        if source not in {"openclaw_main_turn_proxy", "openclaw_agent_end_session_end"}:
            return ""
        canonical_messages: List[Dict[str, str]] = []
        for item in list(messages or []):
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "").strip().lower()
            content = str(item.get("content") or "").strip()
            if not role or not content:
                continue
            canonical_messages.append({"role": role, "content": content})
        if not canonical_messages:
            return ""
        payload = {
            "user_id": str(user_id or "").strip(),
            "session_id": str(meta.get("session_id") or "").strip(),
            "messages": canonical_messages,
        }
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _mark_openclaw_extraction_dedupe(self, *, dedupe_key: str) -> bool:
        """Return False when dedupe key is already observed."""
        key = str(dedupe_key or "").strip()
        if not key:
            return True
        now_ms = int(time.time() * 1000)
        with self._openclaw_extract_dedupe_lock:
            if key in self._openclaw_extract_dedupe_seen:
                return False
            self._openclaw_extract_dedupe_seen[key] = now_ms
            if len(self._openclaw_extract_dedupe_seen) > int(self._openclaw_extract_dedupe_max_entries):
                ordered = sorted(self._openclaw_extract_dedupe_seen.items(), key=lambda item: item[1])
                keep = ordered[-int(self._openclaw_extract_dedupe_max_entries) :]
                self._openclaw_extract_dedupe_seen = {k: ts for k, ts in keep}
        return True

    def openclaw_before_agent_start_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """
        pre-run hook:
        - retrieve related skills
        - return context text + a ready-to-inject system message
        """

        messages = _normalize_messages(body.get("messages"))
        query = str(body.get("query") or body.get("q") or "").strip()
        if not messages and query:
            messages = [{"role": "user", "content": query}]
        if not messages:
            raise ValueError("messages or query is required")

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        limit = _safe_int(body.get("limit"), self.config.top_k) or self.config.top_k
        min_score = _safe_float(body.get("min_score"), self.config.min_score)

        retrieval = self._retrieve_context(
            messages=messages,
            user_id=user_id,
            scope=scope,
            limit=limit,
            min_score=min_score,
        )
        payload = self._retrieval_response_payload(retrieval)
        session_id = self._resolve_session_id(body=body, headers=headers)
        usage_remember = self._usage_tracker.remember_retrieval(
            user_id=user_id,
            session_id=session_id,
            retrieval=payload,
        )
        if usage_remember.get("status") == "remembered":
            print(
                f"[openclaw-usage-tracking] remembered retrieval user={user_id or '<empty>'} "
                f"session={session_id or '<empty>'} hits={usage_remember.get('tracked_hits', 0)}"
            )
        context = str(retrieval.get("context") or "")
        context_message = (
            {"role": "system", "content": context}
            if context.strip()
            else None
        )
        return {
            "object": "openclaw_hook_before_agent_start",
            "user": user_id,
            "scope": scope,
            **payload,
            "context": context,
            "context_message": context_message,
            "usage_tracking": usage_remember,
        }

    def openclaw_agent_end_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """
        Hook-style post-run callback:
        - optional success gate
        - schedule background extraction/evolution
        """
        messages = _normalize_messages(body.get("messages"))
        query = str(body.get("query") or body.get("q") or "").strip()
        if not messages and query:
            messages = [{"role": "user", "content": query}]
        if not messages:
            raise ValueError("messages or query is required")

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        turn_type = self._resolve_turn_type(body=body, headers=headers)
        session_id = self._resolve_session_id(body=body, headers=headers)
        session_done = self._resolve_session_done(body=body, headers=headers)
        used_skill_ids = self._extract_used_skill_ids(body=body)
        inferred_used_skill_ids = self._extract_inferred_used_skill_ids(body=body)
        retrieval_payload = body.get("retrieval") if isinstance(body.get("retrieval"), dict) else None

        hint_raw = body.get("hint")
        hint = str(hint_raw).strip() if hint_raw is not None and str(hint_raw).strip() else None
        feedback_raw = body.get("user_feedback")
        feedback = str(feedback_raw).strip() if feedback_raw is not None else ""

        success_raw = (
            body.get("success")
            if body.get("success") is not None
            else (
                body.get("task_success")
                if body.get("task_success") is not None
                else body.get("objective_met")
            )
        )
        success = _parse_bool(success_raw, default=True)
        archive_meta = {
            "source": "openclaw_agent_end",
            "scope": scope,
            "session_id": session_id,
            "turn_type": turn_type,
            "session_done": bool(session_done),
            "success": bool(success),
            "has_feedback": bool(feedback),
        }
        archive_result = self._archive_conversation(
            user_id=user_id,
            source="openclaw_agent_end",
            messages=messages,
            metadata=archive_meta,
        )
        print(
            f"[openclaw-conversation-archive] agent_end archived user={user_id or '<empty>'} "
            f"turn_type={turn_type or '<empty>'} skipped={int(bool(archive_result.get('skipped')))} "
            f"path={archive_result.get('path', '')}"
        )
        sweep = self._conversation_archive.sweep_inactive_sessions(user_id=user_id)
        sweep_ended = list(sweep.get("ended_sessions") or [])
        if sweep_ended:
            print(
                f"[openclaw-session-archive] idle timeout closed user={user_id or '<empty>'} "
                f"count={len(sweep_ended)}"
            )
        session_archive = self._conversation_archive.append_session_record(
            user_id=user_id,
            session_id=session_id,
            turn_type=turn_type,
            messages=messages,
            metadata=archive_meta,
            session_done=bool(session_done),
            success=bool(success),
        )
        ended_sessions = self._merge_ended_sessions(
            list(sweep_ended or []) + list(session_archive.get("ended_sessions") or [])
        )
        print(
            f"[openclaw-session-archive] agent_end staged user={user_id or '<empty>'} "
            f"session={session_id or '<empty>'} turn_type={turn_type or '<empty>'} "
            f"ended={len(ended_sessions)} path={session_archive.get('path', '')}"
        )
        usage = self._track_openclaw_usage(
            user_id=user_id,
            session_id=session_id,
            retrieval=retrieval_payload,
            used_skill_ids=used_skill_ids,
            inferred_used_skill_ids=inferred_used_skill_ids,
            messages=messages,
        )
        if str(usage.get("status") or "") == "recorded":
            inference = usage.get("usage_inference") if isinstance(usage.get("usage_inference"), dict) else {}
            print(
                f"[openclaw-usage-tracking] recorded user={user_id or '<empty>'} "
                f"session={session_id or '<empty>'} updated={usage.get('updated', 0)} "
                f"deleted={len(list(usage.get('deleted_skill_ids') or []))} "
                f"infer_status={str(inference.get('status') or 'skipped')}"
            )
        deleted_by_usage = [str(x) for x in (usage.get("deleted_skill_ids") or []) if str(x).strip()]
        if deleted_by_usage:
            sync = self._sync_openclaw_installed_skills(
                user_id=user_id,
                reason="usage_tracking_prune",
            )
            usage["openclaw_install_sync"] = sync
        if not self.main_turn_proxy_config.agent_end_extract_enabled:
            return {
                "object": "openclaw_hook_agent_end",
                "user": user_id,
                "scope": scope,
                "usage": usage,
                "extraction": {
                    "job_id": None,
                    "status": "skipped",
                    "reason": "agent_end_disabled_by_config",
                },
            }
        if not session_id:
            return {
                "object": "openclaw_hook_agent_end",
                "user": user_id,
                "scope": scope,
                "usage": usage,
                "extraction": {
                    "job_id": None,
                    "status": "skipped",
                    "reason": "missing_session_id",
                },
            }
        if not ended_sessions:
            return {
                "object": "openclaw_hook_agent_end",
                "user": user_id,
                "scope": scope,
                "usage": usage,
                "extraction": {
                    "job_id": None,
                    "status": "skipped",
                    "reason": "session_not_finished",
                },
            }

        min_score = _safe_float(body.get("min_score"), self.config.min_score)
        scheduled_jobs: List[str] = []
        skipped_reasons: List[str] = []
        for ended in ended_sessions:
            ended_path = str(ended.get("path") or "").strip()
            ended_session_id = str(ended.get("session_id") or "").strip()
            if self._session_has_main_turn_extraction_event(
                user_id=user_id,
                session_id=ended_session_id,
            ):
                skipped_reasons.append(f"{ended_session_id or '<empty>'}:dedupe_main_turn_already_extracted")
                print(
                    f"[openclaw-extraction-dedupe] skip agent_end session={ended_session_id or '<empty>'} "
                    f"reason=main_turn_event_exists"
                )
                continue
            loaded = self._conversation_archive.load_session_for_extraction(path=ended_path)
            if not bool(loaded.get("ok")):
                skipped_reasons.append(
                    f"{ended_session_id or '<empty>'}:load_failed:{loaded.get('reason') or 'unknown'}"
                )
                continue
            if not bool(loaded.get("has_main_turn")):
                skipped_reasons.append(f"{ended_session_id or '<empty>'}:turn_type_not_main")
                continue
            if not bool(loaded.get("has_successful_main_turn")):
                skipped_reasons.append(f"{ended_session_id or '<empty>'}:task_not_successful")
                continue

            session_messages = list(loaded.get("messages") or [])
            extraction_window = self._build_session_end_window(messages=session_messages)
            if not extraction_window:
                skipped_reasons.append(f"{ended_session_id or '<empty>'}:window_not_ready")
                continue

            retrieval = self._retrieve_context(
                messages=extraction_window,
                user_id=user_id,
                scope=scope,
                limit=1,
                min_score=min_score,
            )
            top_ref = self._top_reference_from_retrieval_hits(
                retrieval_hits=list((retrieval or {}).get("hits") or []),
                user_id=user_id,
            )
            job_id = self._schedule_extraction_job(
                user_id=user_id,
                messages=extraction_window,
                trigger="openclaw_agent_end_session_end",
                hint=hint,
                retrieval_reference=top_ref,
                metadata={
                    "source": "openclaw_agent_end_session_end",
                    "session_id": ended_session_id,
                    "turn_type": "main",
                    "session_archive_path": ended_path,
                    "session_turn_count": int(loaded.get("turn_count") or 0),
                    "dedupe_key": self._build_openclaw_extraction_dedupe_key(
                        user_id=user_id,
                        messages=extraction_window,
                        trigger="openclaw_agent_end_session_end",
                        metadata={
                            "source": "openclaw_agent_end_session_end",
                            "session_id": ended_session_id,
                        },
                    ),
                },
                event_fields={
                    "session_id": ended_session_id,
                    "session_archive_path": ended_path,
                },
            )
            ev = self._get_extraction_event_by_job(job_id=job_id)
            status = str((ev or {}).get("status") or "scheduled").strip().lower()
            if status in {"scheduled", "running", "completed"}:
                scheduled_jobs.append(job_id)
                continue
            skipped_reasons.append(f"{ended_session_id or '<empty>'}:schedule_{status or 'unknown'}")

        if not scheduled_jobs:
            reason = ";".join(skipped_reasons) if skipped_reasons else "session_not_extractable"
            return {
                "object": "openclaw_hook_agent_end",
                "user": user_id,
                "scope": scope,
                "usage": usage,
                "extraction": {
                    "job_id": None,
                    "status": "skipped",
                    "reason": reason,
                },
            }

        latest_job_id = scheduled_jobs[-1]
        ev = self._get_extraction_event_by_job(job_id=latest_job_id)
        status = str((ev or {}).get("status") or "scheduled")
        return {
            "object": "openclaw_hook_agent_end",
            "user": user_id,
            "scope": scope,
            "usage": usage,
            "extraction": {
                "job_id": latest_job_id,
                "status": status,
                "reason": "",
                "jobs": list(scheduled_jobs),
            },
        }

    def openclaw_turn_api(self, *, body: Dict[str, Any], headers: Any) -> Dict[str, Any]:
        """
        Main OpenClaw integration endpoint.

        Input:
        - messages or query
        - optional scope/min_score/top_k
        - optional schedule_extraction (default true)
        - optional hint

        Output:
        - retrieval payload (rewritten query + hits + selected skill ids + context)
        - extraction scheduling status/job id
        """

        messages = _normalize_messages(body.get("messages"))
        query = str(body.get("query") or body.get("q") or "").strip()
        if not messages and query:
            messages = [{"role": "user", "content": query}]
        if not messages:
            raise ValueError("messages or query is required")

        user_id = self._resolve_user_id(body=body, headers=headers)
        scope_raw = str(body.get("scope") or "").strip()
        scope = _normalize_scope(scope_raw) if scope_raw else self._resolve_scope(headers=headers)
        limit = _safe_int(body.get("limit"), self.config.top_k) or self.config.top_k
        min_score = _safe_float(body.get("min_score"), self.config.min_score)
        retrieval = self._retrieve_context(
            messages=messages,
            user_id=user_id,
            scope=scope,
            limit=limit,
            min_score=min_score,
        )
        payload = self._retrieval_response_payload(retrieval)

        schedule = _parse_bool(body.get("schedule_extraction"), default=True)
        hint_raw = body.get("hint")
        hint = str(hint_raw).strip() if hint_raw is not None and str(hint_raw).strip() else None
        extraction_job_id: Optional[str] = None
        extraction_status = "disabled"
        extraction_reason = "schedule_extraction=false"

        if schedule:
            extraction_window = self._build_auto_extraction_window(messages)
            if extraction_window:
                top_ref = self._top_reference_from_retrieval_hits(
                    retrieval_hits=list((retrieval or {}).get("hits") or []),
                    user_id=user_id,
                )
                extraction_job_id = self._schedule_extraction_job(
                    user_id=user_id,
                    messages=extraction_window,
                    trigger="openclaw_turn",
                    hint=hint,
                    retrieval_reference=top_ref,
                )
                ev = self._get_extraction_event_by_job(job_id=extraction_job_id)
                extraction_status = str((ev or {}).get("status") or "scheduled")
                extraction_reason = ""
            else:
                extraction_status = "skipped"
                extraction_reason = "window_not_ready"

        return {
            "object": "openclaw_turn",
            "user": user_id,
            "scope": scope,
            **payload,
            "context": str(retrieval.get("context") or ""),
            "extraction": {
                "job_id": extraction_job_id,
                "status": extraction_status,
                "reason": extraction_reason,
            },
        }

    def _schedule_extraction_job(
        self,
        *,
        user_id: str,
        messages: List[Dict[str, Any]],
        trigger: str,
        hint: Optional[str] = None,
        retrieval_reference: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        event_fields: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule extraction while allowing plugin-specific metadata."""
        uid = str(user_id or "").strip() or self.config.user_id
        window = list(messages or [])
        job_id = str(uuid.uuid4())
        dedupe_key = self._build_openclaw_extraction_dedupe_key(
            user_id=uid,
            messages=window,
            trigger=str(trigger or "proxy_extract"),
            metadata=(dict(metadata) if isinstance(metadata, dict) else None),
        )
        if not self.config.extract_enabled:
            event = self._empty_extraction_event(
                job_id=job_id,
                trigger=str(trigger or "proxy_extract"),
                status="failed",
                error="extraction disabled",
            )
            if isinstance(event_fields, dict):
                event.update(dict(event_fields))
            self._record_extraction_event(user_id=uid, event=event)
            return job_id
        if not window:
            event = self._empty_extraction_event(
                job_id=job_id,
                trigger=str(trigger or "proxy_extract"),
                status="failed",
                error="empty extraction window",
            )
            if isinstance(event_fields, dict):
                event.update(dict(event_fields))
            self._record_extraction_event(user_id=uid, event=event)
            return job_id
        if dedupe_key and not self._mark_openclaw_extraction_dedupe(dedupe_key=dedupe_key):
            event = self._empty_extraction_event(
                job_id=job_id,
                trigger=str(trigger or "proxy_extract"),
                status="skipped",
                error="dedupe_skipped",
            )
            event["dedupe_key"] = dedupe_key
            if isinstance(event_fields, dict):
                event.update(dict(event_fields))
            self._record_extraction_event(user_id=uid, event=event)
            print(
                f"[openclaw-extraction-dedupe] skipped duplicate "
                f"user={uid} trigger={trigger} dedupe_key={dedupe_key}"
            )
            return job_id

        job = _OpenClawExtractJob(
            job_id=job_id,
            user_id=uid,
            window=window,
            trigger=str(trigger or "proxy_extract"),
            hint=(str(hint).strip() if hint and str(hint).strip() else None),
            retrieval_reference=(dict(retrieval_reference) if isinstance(retrieval_reference, dict) else None),
            metadata=(dict(metadata) if isinstance(metadata, dict) else None),
            event_fields=(dict(event_fields) if isinstance(event_fields, dict) else None),
            dedupe_key=dedupe_key or None,
        )
        scheduled = self._empty_extraction_event(
            job_id=job_id,
            trigger=str(trigger or "proxy_extract"),
            status="scheduled",
            error="",
        )
        if dedupe_key:
            scheduled["dedupe_key"] = dedupe_key
        if isinstance(job.event_fields, dict):
            scheduled.update(dict(job.event_fields))
        self._record_extraction_event(user_id=uid, event=scheduled)

        should_start_worker = False
        with self._extract_sched_lock:
            if uid in self._extract_running_users:
                q = self._extract_queued_by_user.get(uid)
                if q is None:
                    q = []
                    self._extract_queued_by_user[uid] = q
                q.append(job)
            else:
                self._extract_running_users.add(uid)
                should_start_worker = True

        if should_start_worker:
            threading.Thread(
                target=self._background_extraction_worker,
                args=(job,),
                daemon=True,
            ).start()
        return job_id

    def _background_extraction_worker(self, job: _OpenClawExtractJob) -> None:
        """Background worker shared by hook extraction and main-turn extraction."""
        uid = str(getattr(job, "user_id", "") or "").strip() or self.config.user_id
        acquired = False
        current = job
        try:
            self._extract_sema.acquire()
            acquired = True
            while True:
                running = self._empty_extraction_event(
                    job_id=str(current.job_id),
                    trigger=str(current.trigger),
                    status="running",
                    error="",
                )
                if isinstance(current.event_fields, dict):
                    running.update(dict(current.event_fields))
                self._record_extraction_event(user_id=uid, event=running)
                try:
                    ingest_metadata: Dict[str, Any] = {
                        "channel": "proxy_api",
                        "trigger": str(current.trigger),
                        "extraction_reference": (
                            dict(current.retrieval_reference)
                            if isinstance(current.retrieval_reference, dict)
                            else None
                        ),
                    }
                    if isinstance(current.metadata, dict):
                        ingest_metadata.update(dict(current.metadata))
                        if (
                            current.retrieval_reference is not None
                            and ingest_metadata.get("extraction_reference") is None
                        ):
                            ingest_metadata["extraction_reference"] = dict(current.retrieval_reference)

                    updated = self.sdk.ingest(
                        user_id=uid,
                        messages=list(current.window or []),
                        metadata=ingest_metadata,
                        hint=current.hint,
                    )
                    event = self._build_completed_extraction_event(
                        updated=list(updated or []),
                        job_id=str(current.job_id),
                        trigger=str(current.trigger),
                    )
                    if isinstance(current.event_fields, dict):
                        event.update(dict(current.event_fields))
                    self._record_extraction_event(user_id=uid, event=event)
                    if updated:
                        print(
                            f"[proxy] extraction upserted={len(updated)} user={uid} "
                            f"trigger={current.trigger} job={current.job_id}"
                        )
                    install_sync = self._sync_openclaw_installed_skills(
                        user_id=uid,
                        reason=f"background_extract:{current.trigger}",
                    )
                    if install_sync.get("enabled"):
                        print(
                            f"[openclaw-skill-mirror] sync status user={uid} "
                            f"synced={install_sync.get('synced_count', 0)} "
                            f"removed={install_sync.get('removed_count', 0)} "
                            f"reason={install_sync.get('reason') or '<none>'}"
                        )
                except Exception as e:
                    failed = self._empty_extraction_event(
                        job_id=str(current.job_id),
                        trigger=str(current.trigger),
                        status="failed",
                        error=str(e),
                    )
                    if isinstance(current.event_fields, dict):
                        failed.update(dict(current.event_fields))
                    self._record_extraction_event(user_id=uid, event=failed)
                    print(
                        f"[proxy] extraction failed user={uid} "
                        f"trigger={current.trigger} job={current.job_id}: {e}"
                    )

                with self._extract_sched_lock:
                    q = self._extract_queued_by_user.get(uid)
                    next_job = q.pop(0) if q else None
                    if q is not None and not q:
                        self._extract_queued_by_user.pop(uid, None)
                    if next_job is None:
                        self._extract_running_users.discard(uid)
                        break
                current = next_job
        finally:
            if acquired:
                try:
                    self._extract_sema.release()
                except Exception:
                    pass

    def _schedule_main_turn_extraction_job(self, sample: MainTurnSample) -> Optional[str]:
        """Run schedule main turn extraction job."""
        job_id = self._schedule_extraction_job(
            user_id=str(sample.user_id or "").strip() or self.config.user_id,
            messages=list(sample.messages or []),
            trigger="openclaw_main_turn_proxy",
            hint=None,
            retrieval_reference=sample.retrieval_reference,
            metadata=dict(sample.metadata or {}),
            event_fields=dict(sample.metadata or {}),
        )
        ev = self._get_extraction_event_by_job(job_id=job_id)
        status = str((ev or {}).get("status") or "scheduled")
        print(
            f"[openclaw-main-turn-proxy] extraction scheduled "
            f"job_id={job_id} status={status} session={sample.metadata.get('session_id')}"
        )
        return job_id

    def handle_chat_completion_proxy(self, handler: Any, *, body: Dict[str, Any], headers: Any) -> None:
        """Forward `/v1/chat/completions` while sampling main turns."""
        if not self.main_turn_proxy_config.chat_endpoint_enabled:
            return _json_response(
                handler,
                _openai_error(
                    "OpenClaw main-turn proxy target is not configured",
                    code="proxy_target_missing",
                ),
                status=503,
            )

        ctx = parse_turn_context(
            body=body,
            headers=headers,
            default_user_id=self._resolve_user_id(body=body, headers=headers),
            ingest_window=int(self.main_turn_proxy_config.ingest_window),
        )

        with self._main_turn_state.session_guard(ctx.session_id):
            self._main_turn_state.prepare_request(ctx)
            print(
                f"[openclaw-main-turn-proxy] forwarded session={ctx.session_id or '<missing>'} "
                f"turn_type={ctx.turn_type or '<empty>'} stream={int(ctx.stream)} "
                f"target={self.main_turn_proxy_config.target_base_url}"
            )
            success, response_sent, assistant, error = self._main_turn_proxy.forward(
                handler,
                body=body,
                headers=headers,
            )
            self._main_turn_state.finalize_request(
                ctx=ctx,
                assistant=assistant,
                success=bool(success),
                error=str(error or ""),
            )
            archived_messages = list(ctx.messages or [])
            if assistant is not None and getattr(assistant, "as_message", None) is not None:
                assistant_message = assistant.as_message()
                if isinstance(assistant_message, dict):
                    archived_messages.append(dict(assistant_message))
            archive_result = self._archive_conversation(
                user_id=ctx.user_id,
                source="openclaw_chat_proxy",
                messages=archived_messages,
                metadata={
                    "session_id": ctx.session_id,
                    "turn_type": ctx.turn_type,
                    "session_done": bool(ctx.session_done),
                    "turn_index": int(ctx.turn_index),
                    "request_seq": int(ctx.request_seq),
                    "request_id": str(ctx.request_id),
                    "stream": bool(ctx.stream),
                    "success": bool(success),
                    "error": str(error or ""),
                },
            )
            print(
                f"[openclaw-conversation-archive] chat_proxy archived session={ctx.session_id or '<empty>'} "
                f"turn_type={ctx.turn_type or '<empty>'} skipped={int(bool(archive_result.get('skipped')))} "
                f"path={archive_result.get('path', '')}"
            )
            if success or response_sent:
                return
            return _json_response(
                handler,
                _openai_error(str(error or "upstream proxy request failed"), code="upstream_error"),
                status=502,
            )

    def make_handler(self) -> type:
        """Run make handler."""
        base_handler = super().make_handler()
        runtime = self

        class Handler(base_handler):
            def do_POST(self) -> None:  # noqa: N802
                """Run do POST."""
                parsed = urlparse(self.path or "/")
                path = parsed.path or "/"

                if path == "/v1/chat/completions":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    return runtime.handle_chat_completion_proxy(self, body=body, headers=self.headers)

                # This plugin is not an embeddings proxy.
                if path == "/v1/embeddings":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    return _json_response(
                        self,
                        _openai_error(
                            "Endpoint disabled in OpenClaw skill service",
                            code="not_supported",
                        ),
                        status=404,
                    )

                if path == "/v1/autoskill/openclaw/turn":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    try:
                        payload = runtime.openclaw_turn_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/openclaw/skills/sync":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    try:
                        payload = runtime.openclaw_skill_sync_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/openclaw/usage/stats":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    try:
                        payload = runtime.openclaw_usage_stats_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/openclaw/hooks/before_agent_start":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    try:
                        payload = runtime.openclaw_before_agent_start_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                if path == "/v1/autoskill/openclaw/hooks/agent_end":
                    if path.startswith("/v1/") and not self._authorized():
                        return
                    body = self._read_body_safely()
                    if body.get("_error"):
                        return
                    try:
                        payload = runtime.openclaw_agent_end_api(body=body, headers=self.headers)
                    except Exception as e:
                        return _json_response(
                            self,
                            _openai_error(str(e), code="invalid_request"),
                            status=400,
                        )
                    return _json_response(self, payload)

                return super().do_POST()

        return Handler
