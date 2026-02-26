"""
Headless interactive session.

This module implements the same core orchestration as `InteractiveChatApp`, but without console IO.
It is intended for programmatic frontends (e.g., a web UI) that want:
- chat + retrieval each turn
- optional query rewriting, skill selection, and extraction gating
- structured outputs for rendering (retrieval hits, extracted skills, etc.)
"""

from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from ..client import AutoSkill
from ..llm.base import LLM
from ..models import Skill, SkillHit
from ..render import render_skills_context, select_skills_for_context
from .commands import Command, parse_command
from .config import InteractiveConfig
from .retrieval import retrieve_hits_by_scope
from .rewriting import LLMQueryRewriter
from .selection import LLMSkillSelector


@dataclass
class _PendingExtraction:
    # Snapshot of the latest assistant turn waiting for user feedback.
    latest_user: str
    latest_assistant: str
    messages: List[Dict[str, Any]]

@dataclass
class _BgExtractJob:
    # One asynchronous extraction task. `epoch` guards against stale jobs after /clear.
    job_id: str
    window: List[Dict[str, Any]]
    trigger: str
    hint: Optional[str]
    epoch: int
    retrieval_reference: Optional[Dict[str, Any]] = None


def _skill_source_label(skill: Skill) -> str:
    """Returns a compact source label used by retrieval diagnostics."""

    owner = str(getattr(skill, "user_id", "") or "").strip()
    if owner.startswith("library:"):
        return owner
    if owner:
        return f"user:{owner}"
    return "user"


def _format_hit(hit: SkillHit, *, rank: int) -> Dict[str, Any]:
    """Normalizes a `SkillHit` into a stable JSON-ready dict."""

    skill = getattr(hit, "skill", None)
    score = float(getattr(hit, "score", 0.0) or 0.0)
    if skill is None:
        return {"rank": int(rank), "score": score}
    return {
        "rank": int(rank),
        "score": score,
        "id": str(skill.id),
        "name": str(skill.name),
        "description": str(skill.description),
        "source": _skill_source_label(skill),
        "owner": str(getattr(skill, "user_id", "") or ""),
        "version": str(getattr(skill, "version", "") or ""),
    }


def _top_reference_from_hits(hits: List[SkillHit], *, user_id: str) -> Optional[Dict[str, Any]]:
    if not hits:
        return None
    top = hits[0]
    skill = getattr(top, "skill", None)
    if skill is None:
        return None
    owner = str(getattr(skill, "user_id", "") or "").strip()
    scope = "library" if owner.startswith("library:") else ("user" if owner == str(user_id or "").strip() else "other")
    return {
        "id": str(getattr(skill, "id", "") or "").strip(),
        "name": str(getattr(skill, "name", "") or "").strip(),
        "description": str(getattr(skill, "description", "") or "").strip(),
        "triggers": [str(t).strip() for t in (getattr(skill, "triggers", []) or []) if str(t).strip()][:20],
        "scope": scope,
        "score": float(getattr(top, "score", 0.0) or 0.0),
    }


def _truncate_text(text: str, *, max_chars: int) -> str:
    """UI-safe truncation helper for large markdown payloads."""

    s = str(text or "")
    if max_chars <= 0 or len(s) <= max_chars:
        return s
    return s[:max_chars].rstrip() + "\n\n...(truncated)...\n"


def _now_ms() -> int:
    return int(time.time() * 1000)


class InteractiveSession:
    """
    Stateful session for interactive chat with retrieval and optional extraction.

    The session stores:
    - conversation messages (for chat history)
    - a pending extraction window, evaluated on the NEXT user message as feedback
    """

    def __init__(
        self,
        *,
        sdk: AutoSkill,
        config: Optional[InteractiveConfig] = None,
        chat_llm: Optional[LLM] = None,
        query_rewriter: Optional[LLMQueryRewriter] = None,
        skill_selector: Optional[LLMSkillSelector] = None,
    ) -> None:
        self.sdk = sdk
        self.config = (config or InteractiveConfig()).normalize()
        self.chat_llm = chat_llm
        self.query_rewriter = query_rewriter
        self.skill_selector = skill_selector

        self.messages: List[Dict[str, Any]] = []
        self._pending: Optional[_PendingExtraction] = None
        self._turns_at_last_extract_check: int = 0
        self._epoch: int = 0
        self._bg_extract_sema = threading.BoundedSemaphore(1)
        self._bg_lock = threading.Lock()
        # FIFO queue for extraction jobs that arrive while a worker is running.
        self._queued_extract: List[_BgExtractJob] = []
        self._events: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        # Optional caller-level system instructions injected by API adapters (e.g., proxy).
        self._caller_system_prompt: str = ""
        self._schedule_vector_prewarm()

    def state(self) -> Dict[str, Any]:
        """Returns lightweight session state for web clients."""

        return {
            "config": asdict(self.config),
            "messages": list(self.messages),
            "pending": bool(self._pending),
        }

    def poll(self) -> Dict[str, Any]:
        """
        Returns and clears background events (e.g., completed extraction results).
        """

        events: List[Dict[str, Any]] = []
        while True:
            try:
                events.append(self._events.get_nowait())
            except queue.Empty:
                break
        return {"events": {"extraction": events}}

    def handle_input(self, text: str) -> Dict[str, Any]:
        """
        Handles one input frame in non-stream mode.

        Command parsing is intentionally limited to single-line input to avoid surprises when users
        paste multi-line content.
        """

        raw = str(text or "")
        if not raw.strip():
            return {"kind": "noop", "chat_append": [], "config": asdict(self.config)}

        # Commands are intentionally single-line to avoid surprising behavior when users paste text.
        if "\n" not in raw and "\r" not in raw:
            cmd = parse_command(raw)
            if cmd is not None:
                return self._handle_command(cmd)

        return self._handle_user_message(raw)

    def handle_input_stream(self, text: str) -> Iterator[Dict[str, Any]]:
        """
        Handles one input frame in stream mode.

        Emits assistant deltas first, then a final `result` event with retrieval/extraction metadata.
        """

        raw = str(text or "")
        if not raw.strip():
            yield {"type": "result", "result": {"kind": "noop", "chat_append": [], "config": asdict(self.config)}}
            return

        # Commands are intentionally single-line to avoid surprising behavior when users paste text.
        if "\n" not in raw and "\r" not in raw:
            cmd = parse_command(raw)
            if cmd is not None:
                out = self._handle_command(cmd)
                yield {"type": "result", "result": out}
                return

        for ev in self._handle_user_message_stream(raw):
            yield ev

    def run_chat_turn(
        self,
        *,
        history_messages: List[Dict[str, Any]],
        latest_user: str,
        caller_system: str = "",
    ) -> Dict[str, Any]:
        """
        Programmatic chat turn API without command parsing.

        This is intended for adapters (proxy/web backends) that already parsed transport-level
        messages and want a stable, non-private session entrypoint.
        """

        latest = str(latest_user or "").strip()
        if not latest:
            raise ValueError("latest user message is empty")
        self.messages = [dict(m) for m in (history_messages or [])]
        self._pending = None
        self._caller_system_prompt = str(caller_system or "").strip()
        try:
            return self._handle_user_message(latest)
        finally:
            self._caller_system_prompt = ""

    def run_chat_turn_stream(
        self,
        *,
        history_messages: List[Dict[str, Any]],
        latest_user: str,
        caller_system: str = "",
    ) -> Iterator[Dict[str, Any]]:
        """
        Streaming variant of `run_chat_turn` without command parsing.
        """

        latest = str(latest_user or "").strip()
        if not latest:
            raise ValueError("latest user message is empty")
        self.messages = [dict(m) for m in (history_messages or [])]
        self._pending = None
        self._caller_system_prompt = str(caller_system or "").strip()

        def _gen() -> Iterator[Dict[str, Any]]:
            try:
                for ev in self._handle_user_message_stream(latest):
                    yield ev
            finally:
                self._caller_system_prompt = ""

        return _gen()

    def _drain_latest_event(self, *, kind: str) -> Optional[Dict[str, Any]]:
        """
        Drains and returns only the latest queued event of a given kind.

        Current use-case is extraction event coalescing for responsive UIs.
        """

        if kind != "extraction":
            return None
        latest: Optional[Dict[str, Any]] = None
        while True:
            try:
                ev = self._events.get_nowait()
            except queue.Empty:
                break
            else:
                latest = ev
        return latest

    def _handle_command(self, cmd: Command) -> Dict[str, Any]:
        name = cmd.name
        arg = cmd.arg

        if name in {"/help"}:
            return {
                "kind": "command",
                "command": name,
                "chat_append": [
                    {
                        "role": "system",
                        "content": self._help_text(),
                    }
                ],
                "config": asdict(self.config),
            }

        if name in {"/clear"}:
            self.messages = []
            self._pending = None
            self._turns_at_last_extract_check = 0
            self._epoch += 1
            self._events = queue.Queue()
            with self._bg_lock:
                self._queued_extract = []
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": "Conversation cleared."}],
                "config": asdict(self.config),
            }

        if name == "/rewrite":
            mode = (arg or "").strip().lower()
            if mode in {"auto", "always", "never"}:
                self.config.rewrite_mode = mode
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": f"Rewrite mode: {self.config.rewrite_mode}"}],
                    "config": asdict(self.config),
                }
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": "Usage: /rewrite auto|always|never"}],
                "config": asdict(self.config),
            }

        if name == "/extract":
            mode = (arg or "").strip().lower()
            if mode in {"auto", "always", "never"}:
                self.config.extract_mode = mode
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": f"Extraction mode: {self.config.extract_mode}"}],
                    "config": asdict(self.config),
                }
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": "Usage: /extract auto|always|never"}],
                "config": asdict(self.config),
            }

        if name == "/extract_every":
            raw = (arg or "").strip()
            try:
                n = int(raw)
            except Exception:
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": "Usage: /extract_every <n>"}],
                    "config": asdict(self.config),
                }
            n = max(1, int(n))
            self.config.extract_turn_limit = n
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": f"Extraction interval (turns): {self.config.extract_turn_limit}"}],
                "config": asdict(self.config),
            }

        if name == "/scope":
            scope = (arg or "").strip().lower()
            if scope == "common":
                scope = "library"
            if scope in {"all", "user", "library"}:
                self.config.skill_scope = scope
                self._schedule_vector_prewarm()
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": f"Skill scope: {self.config.skill_scope}"}],
                    "config": asdict(self.config),
                }
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": "Usage: /scope user|common|all"}],
                "config": asdict(self.config),
            }

        if name == "/skills":
            skills = self.sdk.list(user_id=self.config.user_id)
            if not skills:
                content = "(no skills)"
            else:
                lines = [f"- {s.id} | v{s.version} | {s.name}" for s in skills[:400]]
                content = "Skills:\n" + "\n".join(lines)
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": content}],
                "config": asdict(self.config),
            }

        if name == "/search":
            q = str(arg or "").strip()
            if not q:
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": "Usage: /search <query>"}],
                    "config": asdict(self.config),
                }
            retrieved = retrieve_hits_by_scope(
                sdk=self.sdk,
                query=q,
                user_id=self.config.user_id,
                scope=self.config.skill_scope,
                top_k=self.config.top_k,
                min_score=float(getattr(self.config, "min_score", 0.0) or 0.0),
                allow_partial_vectors=False,
            )
            hits = list(retrieved.get("hits") or [])
            hits_user = list(retrieved.get("hits_user") or [])
            hits_library = list(retrieved.get("hits_library") or [])
            retrieval = self._build_retrieval_info(
                original_query=q,
                rewritten_query=None,
                search_query=q,
                hits=hits,
                hits_user=hits_user,
                hits_library=hits_library,
                selected_for_use=[h.skill for h in hits],
                selected_for_context=[h.skill for h in hits],
                context_injected=False,
                error=(str(retrieved.get("error") or "") or None),
            )
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": f"Search: {q}"}],
                "retrieval": retrieval,
                "config": asdict(self.config),
            }

        if name == "/export":
            sid = str(arg or "").strip()
            if not sid:
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": "Usage: /export <skill_id>"}],
                    "config": asdict(self.config),
                }
            md = self.sdk.export_skill_md(sid)
            if not md:
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [{"role": "system", "content": "(not found)"}],
                    "config": asdict(self.config),
                }
            md2 = _truncate_text(md, max_chars=20_000)
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": md2}],
                "config": asdict(self.config),
            }

        if name == "/extract_now":
            window: Optional[List[Dict[str, Any]]] = None
            if self._pending is not None and self._pending.messages:
                window = list(self._pending.messages)
            elif self.messages:
                window = list(self.messages[-self.config.ingest_window :])

            if not window:
                return {
                    "kind": "command",
                    "command": name,
                    "chat_append": [
                        {"role": "system", "content": "(no conversation context to extract from)"}
                    ],
                    "config": asdict(self.config),
                }

            hint = (arg or "").strip() or None
            self._pending = None
            job_id = self._start_background_extraction(window, trigger="extract_now", hint=hint)
            extraction = {
                "trigger": "extract_now",
                "job_id": str(job_id or ""),
                "event_time": _now_ms(),
                "status": "scheduled",
                "error": "",
                "upserted": [],
                "skill_mds": [],
            }
            content = "[extract_now] scheduled in background"
            if hint:
                content += f" (hint: {hint})"
            return {
                "kind": "command",
                "command": name,
                "chat_append": [{"role": "system", "content": content}],
                "extraction": extraction,
                "config": asdict(self.config),
            }

        return {
            "kind": "command",
            "command": name,
            "chat_append": [{"role": "system", "content": "Unknown command. Use /help."}],
            "config": asdict(self.config),
        }

    def _handle_user_message(self, text: str) -> Dict[str, Any]:
        """
        Main non-stream turn pipeline.

        Stages:
        1) drain background extraction result
        2) rewrite query + retrieve/select skills
        3) (auto mode) schedule extraction using retrieval query/top1 reference
        4) generate assistant response
        5) stage latest window for the next-turn extraction
        """

        latest_user = str(text or "").strip()

        extraction_event = self._drain_latest_event(kind="extraction")
        extraction_scheduled: Optional[Dict[str, Any]] = None

        # Treat the current user message as feedback for the previous assistant response, but run
        # extraction asynchronously so chat latency is not impacted.
        extract_window = self._pop_pending_extraction_window(user_feedback=latest_user)

        self.messages.append({"role": "user", "content": latest_user})

        # Build extraction window early, but schedule only after rewrite+retrieval so the
        # extraction input can use the same rewritten query and top-1 retrieval reference.
        early_window = (
            list(extract_window)
            if extract_window is not None
            else list(self.messages[-self.config.ingest_window :])
        )
        has_assistant_in_window = any(
            str(m.get("role") or "").strip().lower() == "assistant" for m in (early_window or [])
        )

        # 1) Rewrite query (optional) then retrieve Skills for this turn.
        original_query = latest_user
        search_query = latest_user
        rewritten_query: Optional[str] = None

        rewrite_mode = (self.config.rewrite_mode or "auto").strip().lower()
        if rewrite_mode != "never" and self.query_rewriter is not None:
            rewritten = self.query_rewriter.rewrite(query=latest_user, messages=self.messages)
            if rewritten and rewritten.strip():
                rewritten_query = rewritten.strip()
                if rewrite_mode in {"auto", "always"}:
                    search_query = rewritten_query

        retrieved = retrieve_hits_by_scope(
            sdk=self.sdk,
            query=search_query,
            user_id=self.config.user_id,
            scope=self.config.skill_scope,
            top_k=self.config.top_k,
            min_score=float(getattr(self.config, "min_score", 0.0) or 0.0),
            allow_partial_vectors=False,
        )
        hits = list(retrieved.get("hits") or [])
        hits_user = list(retrieved.get("hits_user") or [])
        hits_library = list(retrieved.get("hits_library") or [])
        retrieval_error = str(retrieved.get("error") or "")

        if self._should_trigger_auto_extraction() and has_assistant_in_window and early_window:
            total_turns_abs = sum(
                1
                for m in (self.messages or [])
                if str(m.get("role") or "").strip().lower() == "assistant"
            )
            self._turns_at_last_extract_check = int(total_turns_abs)
            top_ref = _top_reference_from_hits(hits, user_id=self.config.user_id)
            job_id = self._start_background_extraction(
                early_window,
                trigger="auto",
                retrieval_reference=top_ref,
            )
            extraction_scheduled = {
                "trigger": "auto",
                "job_id": str(job_id or ""),
                "event_time": _now_ms(),
                "status": "scheduled",
                "error": "",
                "upserted": [],
                "skill_mds": [],
            }

        skills_for_use = [h.skill for h in hits]
        selected_for_use = list(skills_for_use)
        if self.skill_selector is not None and skills_for_use:
            selected = self.skill_selector.select(
                query=latest_user, messages=self.messages, skills=skills_for_use
            )
            selected_for_use = list(selected or [])

        selected_for_context = select_skills_for_context(
            selected_for_use,
            query=search_query,
            max_chars=self.sdk.config.max_context_chars,
        )
        use_skills = bool(selected_for_context)
        context = (
            render_skills_context(
                selected_for_context,
                query=search_query,
                max_chars=self.sdk.config.max_context_chars,
            )
            if use_skills
            else ""
        )

        # 2) Generate assistant response.
        assistant = self._generate_assistant_response(context=context, use_skills=use_skills)
        self.messages.append({"role": "assistant", "content": assistant})

        # 3) Stage the latest window for potential extraction on the next turn.
        window = self.messages[-self.config.ingest_window :]
        self._pending = _PendingExtraction(
            latest_user=latest_user,
            latest_assistant=assistant,
            messages=list(window),
        )

        retrieval = self._build_retrieval_info(
            original_query=original_query,
            rewritten_query=rewritten_query,
            search_query=search_query,
            hits=hits,
            hits_user=hits_user,
            hits_library=hits_library,
            selected_for_use=selected_for_use,
            selected_for_context=selected_for_context,
            context_injected=use_skills,
            error=retrieval_error or None,
        )

        chat_append = [
            {"role": "user", "content": latest_user},
            {"role": "assistant", "content": assistant},
        ]

        return {
            "kind": "chat",
            "chat_append": chat_append,
            "retrieval": retrieval,
            "extraction": (extraction_scheduled if extraction_scheduled is not None else extraction_event),
            "config": asdict(self.config),
        }

    def _handle_user_message_stream(self, text: str) -> Iterator[Dict[str, Any]]:
        """
        Streaming variant of `_handle_user_message`.

        Retrieval and extraction scheduling are identical; only response emission differs.
        """

        latest_user = str(text or "").strip()

        extraction_event = self._drain_latest_event(kind="extraction")
        extraction_scheduled: Optional[Dict[str, Any]] = None

        # Treat the current user message as feedback for the previous assistant response, but run
        # extraction asynchronously so chat latency is not impacted.
        extract_window = self._pop_pending_extraction_window(user_feedback=latest_user)

        self.messages.append({"role": "user", "content": latest_user})

        # Build extraction window early, but schedule only after rewrite+retrieval so the
        # extraction input can use the same rewritten query and top-1 retrieval reference.
        early_window = (
            list(extract_window)
            if extract_window is not None
            else list(self.messages[-self.config.ingest_window :])
        )
        has_assistant_in_window = any(
            str(m.get("role") or "").strip().lower() == "assistant" for m in (early_window or [])
        )

        # Emit completed extraction updates from previous jobs early so Web UI can refresh.
        if extraction_event is not None:
            yield {"type": "extraction", "extraction": extraction_event}

        # 1) Rewrite query (optional) then retrieve Skills for this turn.
        original_query = latest_user
        search_query = latest_user
        rewritten_query: Optional[str] = None

        rewrite_mode = (self.config.rewrite_mode or "auto").strip().lower()
        if rewrite_mode != "never" and self.query_rewriter is not None:
            rewritten = self.query_rewriter.rewrite(query=latest_user, messages=self.messages)
            if rewritten and rewritten.strip():
                rewritten_query = rewritten.strip()
                if rewrite_mode in {"auto", "always"}:
                    search_query = rewritten_query

        retrieved = retrieve_hits_by_scope(
            sdk=self.sdk,
            query=search_query,
            user_id=self.config.user_id,
            scope=self.config.skill_scope,
            top_k=self.config.top_k,
            min_score=float(getattr(self.config, "min_score", 0.0) or 0.0),
            allow_partial_vectors=False,
        )
        hits = list(retrieved.get("hits") or [])
        hits_user = list(retrieved.get("hits_user") or [])
        hits_library = list(retrieved.get("hits_library") or [])
        retrieval_error = str(retrieved.get("error") or "")

        if self._should_trigger_auto_extraction() and has_assistant_in_window and early_window:
            total_turns_abs = sum(
                1
                for m in (self.messages or [])
                if str(m.get("role") or "").strip().lower() == "assistant"
            )
            self._turns_at_last_extract_check = int(total_turns_abs)
            top_ref = _top_reference_from_hits(hits, user_id=self.config.user_id)
            job_id = self._start_background_extraction(
                early_window,
                trigger="auto",
                retrieval_reference=top_ref,
            )
            extraction_scheduled = {
                "trigger": "auto",
                "job_id": str(job_id or ""),
                "event_time": _now_ms(),
                "status": "scheduled",
                "error": "",
                "upserted": [],
                "skill_mds": [],
            }

        skills_for_use = [h.skill for h in hits]
        selected_for_use = list(skills_for_use)
        if self.skill_selector is not None and skills_for_use:
            selected = self.skill_selector.select(
                query=latest_user, messages=self.messages, skills=skills_for_use
            )
            selected_for_use = list(selected or [])

        selected_for_context = select_skills_for_context(
            selected_for_use,
            query=search_query,
            max_chars=self.sdk.config.max_context_chars,
        )
        use_skills = bool(selected_for_context)
        context = (
            render_skills_context(
                selected_for_context,
                query=search_query,
                max_chars=self.sdk.config.max_context_chars,
            )
            if use_skills
            else ""
        )

        retrieval = self._build_retrieval_info(
            original_query=original_query,
            rewritten_query=rewritten_query,
            search_query=search_query,
            hits=hits,
            hits_user=hits_user,
            hits_library=hits_library,
            selected_for_use=selected_for_use,
            selected_for_context=selected_for_context,
            context_injected=use_skills,
            error=retrieval_error or None,
        )
        # Emit retrieval diagnostics as soon as retrieval is complete.
        yield {"type": "retrieval", "retrieval": retrieval}
        if extraction_scheduled is not None:
            yield {"type": "extraction", "extraction": extraction_scheduled}

        # 2) Generate assistant response (streaming).
        assistant_parts: List[str] = []
        for part in self._generate_assistant_response_stream(context=context, use_skills=use_skills):
            s = str(part or "")
            if not s:
                continue
            assistant_parts.append(s)
            yield {"type": "assistant_delta", "delta": s}
        assistant = "".join(assistant_parts).strip()
        if not assistant:
            assistant = "(empty response)"
        self.messages.append({"role": "assistant", "content": assistant})

        # 3) Stage the latest window for potential extraction on the next turn.
        window = self.messages[-self.config.ingest_window :]
        self._pending = _PendingExtraction(
            latest_user=latest_user,
            latest_assistant=assistant,
            messages=list(window),
        )

        chat_append = [
            {"role": "user", "content": latest_user},
            {"role": "assistant", "content": assistant},
        ]
        result = {
            "kind": "chat",
            "chat_append": chat_append,
            "retrieval": retrieval,
            "extraction": (extraction_scheduled if extraction_scheduled is not None else extraction_event),
            "config": asdict(self.config),
        }
        yield {"type": "result", "result": result}

    def _help_text(self) -> str:
        return (
            "Commands:\n"
            "  /help\n"
            "  /skills\n"
            "  /search <query>\n"
            "  /export <skill_id>\n"
            "  /rewrite auto|always|never\n"
            "  /extract auto|always|never\n"
            "  /extract_every <n>\n"
            "  /extract_now [hint]\n"
            "  /scope user|common|all\n"
            "  /clear\n"
            "\nNotes:\n"
            "  - In /extract auto mode, extraction is attempted once every N turns (N=extract_turn_limit).\n"
            "    Set N=1 to attempt extraction every turn.\n"
            "  - /extract_now [hint] schedules extraction in background (non-blocking).\n"
        )

    def _build_retrieval_info(
        self,
        *,
        original_query: str,
        rewritten_query: Optional[str],
        search_query: str,
        hits: List[SkillHit],
        selected_for_use: List[Skill],
        selected_for_context: List[Skill],
        context_injected: bool,
        hits_user: Optional[List[SkillHit]] = None,
        hits_library: Optional[List[SkillHit]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Builds a retrieval diagnostics payload consumed by CLI/Web views."""

        hits_out = [_format_hit(h, rank=i) for i, h in enumerate(hits or [], start=1)]
        hits_user_out = [_format_hit(h, rank=i) for i, h in enumerate(hits_user or [], start=1)]
        hits_library_out = [_format_hit(h, rank=i) for i, h in enumerate(hits_library or [], start=1)]
        return {
            "original_query": str(original_query or ""),
            "rewritten_query": (str(rewritten_query) if rewritten_query else None),
            "search_query": str(search_query or ""),
            "event_time": _now_ms(),
            "scope": str(self.config.skill_scope),
            "top_k": int(self.config.top_k),
            "min_score": float(self.config.min_score),
            "hits": hits_out,
            "hits_user": hits_user_out,
            "hits_library": hits_library_out,
            "selected_for_use_ids": [str(s.id) for s in (selected_for_use or [])],
            "selected_for_context_ids": [str(s.id) for s in (selected_for_context or [])],
            "context_injected": bool(context_injected),
            "error": (str(error) if error else None),
        }

    def _build_extraction_info(
        self,
        updated: List[Skill],
        *,
        job_id: str,
        event_time: int,
        trigger: str,
        max_md_chars: int = 8000,
    ) -> Dict[str, Any]:
        """Builds extraction completion payload including optional SKILL.md previews."""

        skills = list(updated or [])
        summaries = [{"id": s.id, "name": s.name, "version": s.version, "owner": s.user_id} for s in skills]
        md_items: List[Dict[str, Any]] = []
        skill_items: List[Dict[str, Any]] = []
        for s in skills[:3]:
            md = self.sdk.export_skill_md(str(s.id)) or ""
            # Web editor should receive full SKILL.md content (no "(truncated)" marker).
            # Keep `max_md_chars` in signature for backward compatibility.
            _ = max_md_chars
            md_items.append({"id": s.id, "md": md})
            examples_out: List[Dict[str, Any]] = []
            for ex in list(getattr(s, "examples", []) or [])[:6]:
                examples_out.append(
                    {
                        "input": str(getattr(ex, "input", "") or ""),
                        "output": (
                            str(getattr(ex, "output", "")) if getattr(ex, "output", None) is not None else None
                        ),
                        "notes": (
                            str(getattr(ex, "notes", "")) if getattr(ex, "notes", None) is not None else None
                        ),
                    }
                )
            skill_items.append(
                {
                    "id": str(s.id),
                    "name": str(s.name),
                    "description": str(s.description),
                    "version": str(s.version),
                    "owner": str(s.user_id),
                    "triggers": [str(t) for t in (s.triggers or [])],
                    "tags": [str(t) for t in (s.tags or [])],
                    "instructions": str(s.instructions or ""),
                    "examples": examples_out,
                    "skill_md": md,
                }
            )
        return {
            "trigger": str(trigger),
            "job_id": str(job_id or ""),
            "event_time": int(event_time or _now_ms()),
            "status": "completed",
            "error": "",
            "upserted": summaries,
            "skills": skill_items,
            "skill_mds": md_items,
        }

    def _build_assistant_inputs(self, *, context: str, use_skills: bool) -> Tuple[str, str]:
        """
        Assembles prompts for the chat model.

        When skills are injected, prompt explicitly requires ignoring unrelated retrieved skills.
        """

        if use_skills and (context or "").strip():
            system = (
                "You are a helpful assistant.\n"
                "You have access to a list of retrieved Skills (capabilities) below. \n"
                "**CRITICAL:** These Skills are retrieved automatically and may be irrelevant. \n"
                "1. **Evaluate:** Use a Skill ONLY if it directly matches the user's current intent.\n"
                "2. **Ignore:** If the Skills are unrelated to the query, YOU MUST IGNORE THEM COMPLETELY and answer normally.\n"
                "3. **Silence:** Do not mention the existence of these Skills.\n\n"
                f"Skills Context:\n{context}"
            )
        else:
            system = "You are a helpful assistant.\n"
        caller_system = str(getattr(self, "_caller_system_prompt", "") or "").strip()
        if caller_system:
            system += f"\n\nCaller System Instructions:\n{caller_system}"
        history = self._format_history(max_turns=self.config.history_turns)
        user = f"Conversation:\n{history}\n\nRespond to the latest user message."
        return system, user

    def _generate_assistant_response(self, *, context: str, use_skills: bool) -> str:
        """Blocking assistant generation with defensive error handling."""

        if self.chat_llm is None:
            return "Offline mode: no chat LLM configured."

        system, user = self._build_assistant_inputs(context=context, use_skills=use_skills)
        try:
            out = self.chat_llm.complete(
                system=system,
                user=user,
                temperature=float(self.config.assistant_temperature),
            )
        except Exception as e:
            msg = str(e).replace("\n", " ").strip()
            msg = (msg[:500] + "...") if len(msg) > 500 else msg
            return f"(LLM error: {msg})"
        return (out or "").strip() or "(empty response)"

    def _generate_assistant_response_stream(
        self,
        *,
        context: str,
        use_skills: bool,
    ) -> Iterator[str]:
        """Streaming assistant generation with chunk passthrough."""

        if self.chat_llm is None:
            yield "Offline mode: no chat LLM configured."
            return

        system, user = self._build_assistant_inputs(context=context, use_skills=use_skills)
        try:
            for chunk in self.chat_llm.stream_complete(
                system=system,
                user=user,
                temperature=float(self.config.assistant_temperature),
            ):
                s = str(chunk or "")
                if s:
                    yield s
        except Exception as e:
            msg = str(e).replace("\n", " ").strip()
            msg = (msg[:500] + "...") if len(msg) > 500 else msg
            yield f"(LLM error: {msg})"

    def _format_history(self, *, max_turns: int) -> str:
        """Formats recent turns into plain text history for LLM input."""

        if not self.messages:
            return ""
        max_msgs = max(0, int(max_turns)) * 2
        window = self.messages[-max_msgs:] if max_msgs else self.messages
        lines: List[str] = []
        for m in window:
            role = str(m.get("role") or "").strip().lower()
            content = str(m.get("content") or "").strip()
            if not content:
                continue
            if role == "user":
                lines.append(f"User: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
            else:
                lines.append(f"{role.title()}: {content}")
        return "\n".join(lines).strip()

    def _finalize_pending_extraction(self, *, user_feedback: str) -> Optional[Dict[str, Any]]:
        """Deprecated synchronous path kept for compatibility; extraction is now async."""

        # Kept for backward compatibility; extraction now runs in a background thread.
        extract_window = self._pop_pending_extraction_window(user_feedback=user_feedback)
        if extract_window is None:
            return None
        if not self._should_trigger_auto_extraction():
            return None
        total_turns_abs = sum(
            1
            for m in (self.messages or [])
            if str(m.get("role") or "").strip().lower() == "assistant"
        )
        self._turns_at_last_extract_check = int(total_turns_abs)
        self._start_background_extraction(extract_window, trigger="auto")
        return None

    def _pop_pending_extraction_window(self, *, user_feedback: str) -> Optional[List[Dict[str, Any]]]:
        """
        Converts pending turn snapshot into an extraction window.

        The current user message is appended as feedback so extractor/maintainer can decide whether
        the previous response should become or update a reusable skill.
        """

        pending = self._pending
        if pending is None:
            return None

        self._pending = None

        feedback = str(user_feedback or "").strip()
        window = list(pending.messages or [])
        if feedback:
            window.append({"role": "user", "content": feedback})
        return window

    def _should_trigger_auto_extraction(self) -> bool:
        """
        Returns whether this turn should schedule extraction in auto mode.

        Policy:
        - never: disabled
        - always: every turn
        - auto: once every `extract_turn_limit` assistant turns
        """

        mode = (self.config.extract_mode or "auto").lower()
        if mode == "never":
            return False
        if mode == "always":
            return True
        total_turns_abs = sum(
            1
            for m in (self.messages or [])
            if str(m.get("role") or "").strip().lower() == "assistant"
        )
        interval = max(1, int(getattr(self.config, "extract_turn_limit", 1) or 1))
        turns_since_check = max(0, int(total_turns_abs) - int(self._turns_at_last_extract_check or 0))
        return turns_since_check >= interval

    def _start_background_extraction(
        self,
        window: List[Dict[str, Any]],
        *,
        trigger: str,
        hint: Optional[str] = None,
        retrieval_reference: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Schedules asynchronous extraction work.

        Concurrency strategy:
        - at most one running extraction worker
        - while busy, enqueue jobs and process them in FIFO order
        """

        if not window:
            return None
        job_id = str(uuid.uuid4())
        job = _BgExtractJob(
            job_id=job_id,
            window=list(window),
            trigger=str(trigger or "auto"),
            hint=(str(hint).strip() if hint and str(hint).strip() else None),
            epoch=int(self._epoch),
            retrieval_reference=(dict(retrieval_reference) if isinstance(retrieval_reference, dict) else None),
        )

        with self._bg_lock:
            if self._bg_extract_sema.acquire(blocking=False):
                thread = threading.Thread(
                    target=self._background_extraction_worker,
                    args=(job,),
                    daemon=True,
                )
                thread.start()
                return job_id
            # A background extraction is already running: queue this job for FIFO processing.
            self._queued_extract.append(job)
            return job_id

    def _background_extraction_worker(self, job: _BgExtractJob) -> None:
        """
        Worker loop for extraction tasks.

        Processes the current job and then queued jobs in FIFO order; stale epochs are
        discarded so `/clear` can safely reset session state.
        """

        try:
            current = job
            while True:
                epoch = int(getattr(current, "epoch", 0) or 0)
                if epoch != int(self._epoch):
                    break

                try:
                    if epoch == int(self._epoch):
                        self._events.put(
                            {
                                "trigger": str(current.trigger),
                                "job_id": str(current.job_id),
                                "event_time": _now_ms(),
                                "status": "running",
                                "error": "",
                                "upserted": [],
                                "skill_mds": [],
                            }
                        )
                    updated = self.sdk.ingest(
                        user_id=self.config.user_id,
                        messages=list(current.window or []),
                        metadata={
                            "channel": "chat",
                            "trigger": str(current.trigger),
                            # Explicitly pass top-1 retrieval reference (or None).
                            "extraction_reference": (
                                dict(current.retrieval_reference)
                                if isinstance(current.retrieval_reference, dict)
                                else None
                            ),
                        },
                        hint=current.hint,
                    )
                    if not updated:
                        event = {
                            "trigger": str(current.trigger),
                            "job_id": str(current.job_id),
                            "event_time": _now_ms(),
                            "status": "completed",
                            "error": "",
                            "upserted": [],
                            "skill_mds": [],
                        }
                    else:
                        md_chars = 8000 if str(current.trigger) == "extract_now" else 3000
                        event = self._build_extraction_info(
                            updated,
                            job_id=str(current.job_id),
                            event_time=_now_ms(),
                            trigger=str(current.trigger),
                            max_md_chars=md_chars,
                        )
                except Exception as e:
                    event = {
                        "trigger": str(current.trigger),
                        "job_id": str(current.job_id),
                        "event_time": _now_ms(),
                        "status": "failed",
                        "error": str(e),
                        "upserted": [],
                        "skill_mds": [],
                    }

                # Only publish results if the session has not been cleared/reset since this job started.
                if epoch == int(self._epoch):
                    self._events.put(event)

                with self._bg_lock:
                    next_job = self._queued_extract.pop(0) if self._queued_extract else None
                if next_job is None:
                    break
                current = next_job
        finally:
            try:
                self._bg_extract_sema.release()
            except Exception:
                pass

    def _schedule_vector_prewarm(self) -> None:
        """
        Best-effort call into store prewarm API to reduce first-query retrieval latency.
        """

        store = getattr(self.sdk, "store", None)
        fn = getattr(store, "schedule_vector_prewarm", None)
        if not callable(fn):
            return
        try:
            fn(user_id=self.config.user_id, scope=self.config.skill_scope)
        except Exception:
            return
