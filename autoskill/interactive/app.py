"""
Interactive chat application.

This module owns the orchestration logic:
- retrieve skills each turn
- generate assistant response (optional LLM)
- optionally extract/maintain skills (AutoSkill ingest)
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Tuple

from ..client import AutoSkill
from ..llm.base import LLM
from ..render import render_skills_context, select_skills_for_context
from .commands import Command, parse_command
from .config import InteractiveConfig
from .io import ConsoleIO, IO
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
    window: List[Dict[str, Any]]
    trigger: str
    hint: Optional[str]
    epoch: int
    retrieval_reference: Optional[Dict[str, Any]] = None


def _top_reference_from_hits(hits: List[Any], *, user_id: str) -> Optional[Dict[str, Any]]:
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
        "scope": scope,
        "score": float(getattr(top, "score", 0.0) or 0.0),
    }


class InteractiveChatApp:
    def __init__(
        self,
        *,
        sdk: AutoSkill,
        config: InteractiveConfig,
        io: Optional[IO] = None,
        chat_llm: Optional[LLM] = None,
        query_rewriter: Optional[LLMQueryRewriter] = None,
        skill_selector: Optional[LLMSkillSelector] = None,
    ) -> None:
        """Creates a console chat app that orchestrates retrieval + response + async extraction."""

        self.sdk = sdk
        self.config = config.normalize()
        self.io: IO = io or ConsoleIO()
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

    def run(self) -> None:
        """Starts the blocking REPL loop."""

        self._print_banner()
        self._print_help()
        while True:
            self._drain_background_events()
            try:
                line = self.io.input("\nYou> ").strip()
            except (EOFError, KeyboardInterrupt):
                self.io.print("\nBye.")
                return

            if not line:
                continue

            cmd = parse_command(line)
            if cmd is not None:
                should_exit = self._handle_command(cmd)
                if should_exit:
                    return
                continue

            self._handle_user_message(line)

    def _print_banner(self) -> None:
        """Prints startup diagnostics and schedules best-effort vector prewarm."""

        online = "online" if self.chat_llm is not None else "offline"
        self.io.print("AutoSkill interactive chat")
        self.io.print("Store dir:", self.config.store_dir)
        self.io.print("User id:", self.config.user_id)
        self.io.print("Skill scope:", self.config.skill_scope)
        self.io.print("Extraction mode:", self.config.extract_mode)
        self.io.print("Extraction interval (turns):", self.config.extract_turn_limit)
        self.io.print("Mode:", online)
        self.io.print("Existing skills:", len(self.sdk.list(user_id=self.config.user_id)))
        self._schedule_vector_prewarm(log=True)

    def _print_help(self) -> None:
        """Prints command list and extraction behavior notes."""

        self.io.print(
            "\nCommands:\n"
            "  /help\n"
            "  /exit\n"
            "  /skills\n"
            "  /search <query>\n"
            "  /export <skill_id>\n"
            "  /write <dir>\n"
            "  /rewrite auto|always|never\n"
            "  /extract auto|always|never\n"
            "  /extract_every <n>\n"
            "  /extract_now [hint]  (alias: extract_now [hint])\n"
            "  /paste               (multi-line input; end with /end)\n"
            "  /file <path>         (send file content as a message)\n"
            "  /clip                (send clipboard content as a message)\n"
            "  /scope user|common|all\n"
            "  /clear\n"
            "\nNotes:\n"
            "  - In /extract auto mode, extraction is attempted once every N turns (N=extract_turn_limit).\n"
            "    Set N=1 to attempt extraction every turn.\n"
            "  - /extract_now [hint] schedules extraction in background (non-blocking).\n"
        )

    def _handle_command(self, cmd: Command) -> bool:
        """Handles slash commands; returns True only when the app should exit."""

        name = cmd.name
        arg = cmd.arg

        if name in {"/exit", "/quit"}:
            self.io.print("Bye.")
            return True

        if name == "/help":
            self._print_help()
            return False

        if name == "/clear":
            self.messages = []
            self._pending = None
            self._turns_at_last_extract_check = 0
            self._epoch += 1
            self._events = queue.Queue()
            with self._bg_lock:
                self._queued_extract = []
            self.io.print("Conversation cleared.")
            return False

        if name == "/paste":
            text = self._read_multiline_message()
            if text is None:
                return False
            if not text.strip():
                self.io.print("(empty)")
                return False
            self._handle_user_message(text)
            return False

        if name == "/file":
            if not arg:
                self.io.print("Usage: /file <path>")
                return False
            text = self._read_file_message(arg)
            if text is None:
                return False
            if not text.strip():
                self.io.print("(empty)")
                return False
            self._handle_user_message(text)
            return False

        if name == "/clip":
            text = self._read_clipboard_message()
            if text is None:
                return False
            if not text.strip():
                self.io.print("(empty)")
                return False
            self._handle_user_message(text)
            return False

        if name == "/extract":
            mode = (arg or "").strip().lower()
            if mode in {"auto", "always", "never"}:
                self.config.extract_mode = mode
                self.io.print("Extraction mode:", self.config.extract_mode)
            else:
                self.io.print("Usage: /extract auto|always|never")
            return False

        if name == "/extract_every":
            raw = (arg or "").strip()
            try:
                n = int(raw)
            except Exception:
                self.io.print("Usage: /extract_every <n>")
                return False
            n = max(1, n)
            self.config.extract_turn_limit = n
            self.io.print("Extraction interval (turns):", self.config.extract_turn_limit)
            return False

        if name == "/extract_now":
            window = None
            if self._pending is not None and self._pending.messages:
                window = list(self._pending.messages)
            elif self.messages:
                window = list(self.messages[-self.config.ingest_window :])

            if not window:
                self.io.print("(no conversation context to extract from)")
                return False

            hint = (arg or "").strip() or None
            self._pending = None
            self._start_background_extraction(window, trigger="extract_now", hint=hint)
            self.io.print("\n[extract_now] scheduled in background")
            if hint:
                self.io.print("[extract_now] hint:", hint)
            return False

        if name == "/rewrite":
            mode = (arg or "").strip().lower()
            if mode in {"auto", "always", "never"}:
                self.config.rewrite_mode = mode
                self.io.print("Rewrite mode:", self.config.rewrite_mode)
            else:
                self.io.print("Usage: /rewrite auto|always|never")
            return False

        if name == "/scope":
            scope = (arg or "").strip().lower()
            if scope == "common":
                scope = "library"
            if scope in {"all", "user", "library"}:
                self.config.skill_scope = scope
                self.io.print("Skill scope:", self.config.skill_scope)
                self._schedule_vector_prewarm(log=True)
            else:
                self.io.print("Usage: /scope user|common|all")
            return False

        if name == "/skills":
            skills = self.sdk.list(user_id=self.config.user_id)
            if not skills:
                self.io.print("(no skills)")
                return False
            for s in skills[:200]:
                self.io.print(f"- {s.id} | v{s.version} | {s.name}")
            return False

        if name == "/search":
            if not arg:
                self.io.print("Usage: /search <query>")
                return False
            hits = self.sdk.search(
                arg,
                user_id=self.config.user_id,
                limit=self.config.top_k,
                filters={"scope": self.config.skill_scope, "allow_partial_vectors": False},
            )
            if not hits:
                self.io.print("(no hits)")
                return False
            for h in hits:
                self.io.print(f"{h.score:.3f} - {h.skill.id} - {h.skill.name}")
            return False

        if name == "/export":
            if not arg:
                self.io.print("Usage: /export <skill_id>")
                return False
            md = self.sdk.export_skill_md(arg)
            if not md:
                self.io.print("(not found)")
                return False
            self.io.print(md)
            return False

        if name == "/write":
            if not arg:
                self.io.print("Usage: /write <dir>")
                return False
            out_dirs = self.sdk.write_skill_dirs(user_id=self.config.user_id, root_dir=arg)
            self.io.print("Wrote:", len(out_dirs), "skill directories")
            return False

        self.io.print("Unknown command. Use /help.")
        return False

    def _read_multiline_message(self) -> Optional[str]:
        """
        Reads a multi-line user message from the console.

        Termination:
        - end: /end
        - cancel: /cancel (or Ctrl-C)
        """

        self.io.print("\n[paste] Enter multi-line input. End with a single line: /end (cancel: /cancel)")
        lines: List[str] = []
        while True:
            try:
                line = self.io.input("... ").rstrip("\n")
            except (EOFError, KeyboardInterrupt):
                self.io.print("\n[paste] canceled")
                return None

            marker = line.strip()
            if marker in {"/end", "／end"}:
                break
            if marker in {"/cancel", "／cancel"}:
                self.io.print("[paste] canceled")
                return None
            lines.append(line)
        return "\n".join(lines)

    def _read_file_message(self, raw_path: str) -> Optional[str]:
        """Loads file content as message text, with size cap and UTF-8 replacement decode."""

        import os

        path = str(raw_path or "").strip()
        if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
            path = path[1:-1].strip()
        if not path:
            self.io.print("Usage: /file <path>")
            return None

        abs_path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
        if not os.path.isfile(abs_path):
            self.io.print("[file] not found:", abs_path)
            return None

        max_bytes = 2_000_000
        try:
            with open(abs_path, "rb") as f:
                data = f.read(max_bytes + 1)
        except Exception as e:
            self.io.print("[file] failed:", str(e))
            return None

        truncated = len(data) > max_bytes
        text = data[:max_bytes].decode("utf-8", errors="replace")
        if truncated:
            text = text.rstrip() + "\n\n...[truncated]...\n"
        self.io.print(
            f"[file] loaded: {abs_path} ({len(data[:max_bytes])} bytes{' truncated' if truncated else ''})"
        )
        return text

    def _read_clipboard_message(self) -> Optional[str]:
        """Loads clipboard text using platform-specific commands."""

        import subprocess

        def _try(cmd: list[str]) -> Optional[bytes]:
            try:
                return subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            except Exception:
                return None

        data = _try(["pbpaste"])
        if data is None:
            data = _try(["wl-paste", "--no-newline"])
        if data is None:
            data = _try(["xclip", "-o", "-selection", "clipboard"])
        if data is None:
            data = _try(["powershell.exe", "-NoProfile", "-Command", "Get-Clipboard -Raw"])
        if data is None:
            data = _try(["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"])

        if data is None:
            self.io.print("[clip] clipboard read not supported here (try /file <path>)")
            return None

        max_bytes = 2_000_000
        truncated = len(data) > max_bytes
        text = data[:max_bytes].decode("utf-8", errors="replace")
        if truncated:
            text = text.rstrip() + "\n\n...[truncated]...\n"
        self.io.print(f"[clip] loaded ({len(data[:max_bytes])} bytes{' truncated' if truncated else ''})")
        return text

    def _handle_user_message(self, text: str) -> None:
        """
        Main console turn pipeline.

        Stages:
        1) drain background extraction result
        2) rewrite query + retrieve/select skills
        3) schedule extraction with retrieval query/top1 reference (parallel with chat generation)
        4) stream assistant response
        5) stage latest window for next-turn feedback
        """

        latest_user = text.strip()

        # Drain any completed extraction results from background jobs.
        self._drain_background_events()

        # Treat the current user message as feedback for the previous turn, but run extraction
        # asynchronously so chat latency is not impacted.
        extract_window = self._pop_pending_extraction_window(user_feedback=latest_user)

        self.messages.append({"role": "user", "content": latest_user})

        # Build extraction window early, but schedule only after rewrite+retrieval so extraction
        # can consume the same rewritten query and top-1 retrieval reference.
        early_window = (
            list(extract_window)
            if extract_window is not None
            else list(self.messages[-self.config.ingest_window :])
        )
        has_assistant_in_window = any(
            str(m.get("role") or "").strip().lower() == "assistant" for m in (early_window or [])
        )
        # 1) Rewrite query (optional) then retrieve Skills for this turn.
        search_query = latest_user
        rewrite_mode = (self.config.rewrite_mode or "auto").strip().lower()
        if rewrite_mode != "never" and self.query_rewriter is not None:
            rewritten = self.query_rewriter.rewrite(query=latest_user, messages=self.messages)
            if rewritten and rewritten.strip():
                if rewritten.strip() != latest_user.strip():
                    self.io.print(f"\n[retrieve] rewritten query: {rewritten}")
                if rewrite_mode in {"auto", "always"}:
                    search_query = rewritten.strip()
        try:
            hits = self.sdk.search(
                search_query,
                user_id=self.config.user_id,
                limit=self.config.top_k,
                filters={"scope": self.config.skill_scope, "allow_partial_vectors": False},
            )
        except Exception as e:
            self.io.print("\n[retrieve] failed:", str(e))
            hits = []
        min_score = float(getattr(self.config, "min_score", 0.0) or 0.0)
        if hits and min_score > 0:
            hits = [h for h in hits if float(getattr(h, "score", 0.0) or 0.0) >= min_score]
        if self._should_trigger_auto_extraction() and has_assistant_in_window and early_window:
            total_turns_abs = sum(
                1
                for m in (self.messages or [])
                if str(m.get("role") or "").strip().lower() == "assistant"
            )
            self._turns_at_last_extract_check = int(total_turns_abs)
            top_ref = _top_reference_from_hits(hits, user_id=self.config.user_id)
            self._start_background_extraction(
                early_window,
                trigger="auto",
                retrieval_reference=top_ref,
            )
        self._print_retrieval(hits)

        skills_for_use = [h.skill for h in hits]
        if self.skill_selector is not None and skills_for_use:
            selected_for_use = self.skill_selector.select(
                query=latest_user, messages=self.messages, skills=skills_for_use
            )
            if selected_for_use:
                self._print_selected_for_use(selected_for_use)
                skills_for_use = selected_for_use
            else:
                self.io.print("[retrieve] no skills selected for use")
                skills_for_use = []

        selected = select_skills_for_context(
            skills_for_use,
            query=search_query,
            max_chars=self.sdk.config.max_context_chars,
        )
        if len(selected) != len(skills_for_use):
            self._print_selected_for_context(selected)
        use_skills = bool(selected)
        context = (
            render_skills_context(
                selected,
                query=search_query,
                max_chars=self.sdk.config.max_context_chars,
            )
            if use_skills
            else ""
        )
        # 2) Generate assistant response.
        self.io.print("\nAssistant> ", end="")
        assistant_parts: List[str] = []
        for chunk in self._generate_assistant_response_stream(context=context, use_skills=use_skills):
            s = str(chunk or "")
            if not s:
                continue
            assistant_parts.append(s)
            self.io.print(s, end="", flush=True)
        latest_assistant = "".join(assistant_parts).strip() or "(empty response)"
        self.io.print("")
        self.messages.append({"role": "assistant", "content": latest_assistant})

        # 3) Stage the latest window for potential extraction on the next turn, when we may have
        # explicit user feedback about whether this response helped.
        window = self.messages[-self.config.ingest_window :]
        self._pending = _PendingExtraction(
            latest_user=latest_user,
            latest_assistant=latest_assistant,
            messages=list(window),
        )

    def _print_retrieval(self, hits: List[Any]) -> None:
        """Renders retrieval hits to console with score and source info."""

        if not hits:
            self.io.print("\n[retrieve] no skills")
            return
        self.io.print("\n[retrieve] top skills:")
        for i, h in enumerate(hits, start=1):
            s = getattr(h, "skill", None)
            if s is None:
                continue
            owner = str(getattr(s, "user_id", "") or "").strip()
            source = owner
            if owner.startswith("library:"):
                source = owner
            elif owner:
                source = f"user:{owner}"
            score = float(getattr(h, "score", 0.0) or 0.0)
            self.io.print(f"- {i}. {source} | {s.id} | {s.name} | {score:.4f}")

    def _print_selected_for_context(self, skills: List[Any]) -> None:
        """Renders skills that survived context-length selection."""

        if not skills:
            self.io.print("[retrieve] selected for context: none (max_chars limit)")
            return
        self.io.print(f"[retrieve] selected for context: {len(skills)}")
        for i, s in enumerate(skills, start=1):
            owner = str(getattr(s, "user_id", "") or "").strip()
            source = owner
            if owner.startswith("library:"):
                source = owner
            elif owner:
                source = f"user:{owner}"
            self.io.print(f"- {i}. {source} | {s.id} | {s.name}")

    def _print_selected_for_use(self, skills: List[Any]) -> None:
        """Renders skills chosen by optional LLM selector before context truncation."""

        if not skills:
            self.io.print("[retrieve] selected for use: none")
            return
        self.io.print(f"[retrieve] selected for use: {len(skills)}")
        for i, s in enumerate(skills, start=1):
            owner = str(getattr(s, "user_id", "") or "").strip()
            source = owner
            if owner.startswith("library:"):
                source = owner
            elif owner:
                source = f"user:{owner}"
            self.io.print(f"- {i}. {source} | {s.id} | {s.name}")

    def _build_assistant_inputs(self, *, context: str, use_skills: bool) -> Tuple[str, str]:
        """
        Assembles prompts for chat generation.

        When skills are injected, prompt explicitly requires ignoring irrelevant retrieved skills.
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
        history = self._format_history(max_turns=self.config.history_turns)
        user = f"Conversation:\n{history}\n\nRespond to the latest user message."
        return system, user

    def _generate_assistant_response(self, *, context: str, use_skills: bool) -> str:
        """Blocking response generation with defensive error formatting."""

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
            msg = str(e)
            msg = msg.replace("\n", " ").strip()
            msg = (msg[:500] + "...") if len(msg) > 500 else msg
            return f"(LLM error: {msg})"
        return (out or "").strip() or "(empty response)"

    def _generate_assistant_response_stream(
        self,
        *,
        context: str,
        use_skills: bool,
    ) -> Iterator[str]:
        """Streaming response generation that yields chunks as they arrive."""

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
            msg = str(e)
            msg = msg.replace("\n", " ").strip()
            msg = (msg[:500] + "...") if len(msg) > 500 else msg
            yield f"(LLM error: {msg})"

    def _format_history(self, *, max_turns: int) -> str:
        """Formats recent turns into plain text conversation history."""

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
    ) -> None:
        """
        Schedules asynchronous extraction work.

        Concurrency strategy:
        - at most one running extraction worker
        - while busy, enqueue jobs and process them in FIFO order
        """

        if not window:
            return
        job = _BgExtractJob(
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
                return
            # A background extraction is already running: queue this job for FIFO processing.
            self._queued_extract.append(job)

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
                    updated = self.sdk.ingest(
                        user_id=self.config.user_id,
                        messages=list(current.window or []),
                        metadata={
                            "channel": "chat",
                            "trigger": str(current.trigger),
                            "extraction_reference": (
                                dict(current.retrieval_reference)
                                if isinstance(current.retrieval_reference, dict)
                                else None
                            ),
                        },
                        hint=current.hint,
                    )
                    if epoch == int(self._epoch):
                        self._events.put(
                            {"trigger": str(current.trigger), "updated": list(updated or []), "error": ""}
                        )
                except Exception as e:
                    if epoch == int(self._epoch):
                        self._events.put(
                            {"trigger": str(current.trigger), "updated": [], "error": str(e)}
                        )

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

    def _drain_background_events(self) -> None:
        """
        Prints completed background extraction results, if any.

        Note: Console input is blocking, so events that complete while the user is typing will be
        printed before the next prompt.
        """

        while True:
            try:
                ev = self._events.get_nowait()
            except queue.Empty:
                break

            trigger = str(ev.get("trigger") or "auto")
            err = str(ev.get("error") or "").strip()
            if err:
                self.io.print(f"\n[extract:{trigger}] failed:", err)
                continue

            updated = ev.get("updated") or []
            if not updated:
                self.io.print(f"\n[extract:{trigger}] attempted: no skills extracted")
                continue

            self.io.print(f"\n[extract:{trigger}] upserted:", len(updated))
            for s in updated[:20]:
                sid = getattr(s, "id", "")
                name = getattr(s, "name", "")
                ver = getattr(s, "version", "")
                self.io.print(f"- {sid} | v{ver} | {name}")
            # Keep auto mode lightweight for UX: only print full SKILL.md previews for explicit extract_now.
            if trigger == "extract_now":
                for s in updated[:3]:
                    sid = getattr(s, "id", "")
                    if sid:
                        self._print_skill_md(str(sid), label=f"extract:{trigger}")

    def _print_skill_md(self, skill_id: str, *, label: str) -> None:
        """Prints a capped SKILL.md preview for explicit extraction actions."""

        md = self.sdk.export_skill_md(str(skill_id))
        if not md:
            return
        md_s = str(md).strip()
        if not md_s:
            return
        max_chars = 8000
        if len(md_s) > max_chars:
            md_s = md_s[:max_chars].rstrip() + "\n\n...(truncated; use /export <skill_id> to view full SKILL.md)"
        self.io.print(f"\n[{label}] SKILL.md for {skill_id}:\n{md_s}")

    def _schedule_vector_prewarm(self, *, log: bool = False) -> None:
        """Best-effort vector prewarm to reduce first-query retrieval latency."""

        store = getattr(self.sdk, "store", None)
        fn = getattr(store, "schedule_vector_prewarm", None)
        if not callable(fn):
            return
        try:
            queued = int(
                fn(
                    user_id=self.config.user_id,
                    scope=self.config.skill_scope,
                )
            )
        except Exception:
            return
        if log and queued > 0:
            self.io.print("Vector prewarm scheduled:", queued)
