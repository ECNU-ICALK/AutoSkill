"""
Interactive chat application.

This module owns the orchestration logic:
- retrieve skills each turn
- generate assistant response (optional LLM)
- optionally extract/maintain skills (AutoSkill ingest)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..client import AutoSkill
from ..llm.base import LLM
from ..render import render_skills_context, select_skills_for_context
from .commands import Command, parse_command
from .config import InteractiveConfig
from .gating import (
    LLMExtractionGate,
    heuristic_is_ack_feedback,
    heuristic_should_extract,
    heuristic_topic_changed,
)
from .io import ConsoleIO, IO
from .rewriting import LLMQueryRewriter
from .selection import LLMSkillSelector


@dataclass
class _PendingExtraction:
    latest_user: str
    latest_assistant: str
    messages: List[Dict[str, Any]]


class InteractiveChatApp:
    def __init__(
        self,
        *,
        sdk: AutoSkill,
        config: InteractiveConfig,
        io: Optional[IO] = None,
        chat_llm: Optional[LLM] = None,
        extraction_gate: Optional[LLMExtractionGate] = None,
        query_rewriter: Optional[LLMQueryRewriter] = None,
        skill_selector: Optional[LLMSkillSelector] = None,
    ) -> None:
        self.sdk = sdk
        self.config = config.normalize()
        self.io: IO = io or ConsoleIO()
        self.chat_llm = chat_llm
        self.extraction_gate = extraction_gate
        self.query_rewriter = query_rewriter
        self.skill_selector = skill_selector

        self.messages: List[Dict[str, Any]] = []
        self._pending: Optional[_PendingExtraction] = None
        self._turns_at_last_extract_check: int = 0

    def run(self) -> None:
        self._print_banner()
        self._print_help()
        while True:
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
        online = "online" if self.chat_llm is not None else "offline"
        self.io.print("AutoSkill interactive chat")
        self.io.print("Store dir:", self.config.store_dir)
        self.io.print("User id:", self.config.user_id)
        self.io.print("Skill scope:", self.config.skill_scope)
        self.io.print("Mode:", online)
        self.io.print("Existing skills:", len(self.sdk.list(user_id=self.config.user_id)))

    def _print_help(self) -> None:
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
            "  /extract_now [hint]  (alias: extract_now [hint])\n"
            "  /scope user|common|all\n"
            "  /clear\n"
        )

    def _handle_command(self, cmd: Command) -> bool:
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
            self.io.print("Conversation cleared.")
            return False

        if name == "/extract":
            mode = (arg or "").strip().lower()
            if mode in {"auto", "always", "never"}:
                self.config.extract_mode = mode
                self.io.print("Extraction mode:", self.config.extract_mode)
            else:
                self.io.print("Usage: /extract auto|always|never")
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
            try:
                updated = self.sdk.ingest(
                    user_id=self.config.user_id,
                    messages=window,
                    metadata={"channel": "chat", "trigger": "extract_now"},
                    hint=hint,
                )
            except Exception as e:
                self.io.print("\n[extract_now] failed:", str(e))
                self._pending = None
                return False

            if updated:
                self.io.print("\n[extract_now] upserted:", len(updated))
                for s in updated[:20]:
                    self.io.print(f"- {s.id} | v{s.version} | {s.name}")
                for s in updated[:3]:
                    self._print_skill_md(s.id, label="extract_now")
            else:
                self.io.print("\n[extract_now] no skills extracted")

            self._pending = None
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
                filters={"scope": self.config.skill_scope},
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

    def _handle_user_message(self, text: str) -> None:
        latest_user = text.strip()

        # Before processing the new user message, treat it as feedback for the previous turn.
        # This allows us to extract only when the user confirms usefulness (or to avoid extracting
        # when the user reports the solution did not work).
        self._finalize_pending_extraction(user_feedback=latest_user)

        self.messages.append({"role": "user", "content": latest_user})

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
                filters={"scope": self.config.skill_scope},
            )
        except Exception as e:
            self.io.print("\n[retrieve] failed:", str(e))
            hits = []
        min_score = float(getattr(self.config, "min_score", 0.0) or 0.0)
        if hits and min_score > 0:
            hits = [h for h in hits if float(getattr(h, "score", 0.0) or 0.0) >= min_score]
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
        latest_assistant = self._generate_assistant_response(context=context, use_skills=use_skills)
        self.io.print("\nAssistant> " + latest_assistant)
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

    def _generate_assistant_response(self, *, context: str, use_skills: bool) -> str:
        if self.chat_llm is None:
            return "Offline mode: no chat LLM configured."

        if use_skills and (context or "").strip():
            system = (
                "You are a helpful assistant.\n"
                "You will be given a list of selected Skills retrieved for the current user query.\n"
                "If a Skill is relevant, follow its Prompt to answer.\n"
                "Do not mention the Skills block unless the user asks.\n\n"
                f"{context}"
            )
        else:
            system = "You are a helpful assistant.\n"
        history = self._format_history(max_turns=self.config.history_turns)
        user = f"Conversation:\n{history}\n\nRespond to the latest user message."
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

    def _format_history(self, *, max_turns: int) -> str:
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

    def _finalize_pending_extraction(self, *, user_feedback: str) -> None:
        pending = self._pending
        if pending is None:
            return

        mode = (self.config.extract_mode or "auto").lower()
        if mode == "never":
            self._pending = None
            return

        feedback = str(user_feedback or "").strip()
        total_turns_abs = sum(
            1
            for m in (self.messages or [])
            if str(m.get("role") or "").strip().lower() == "assistant"
        )
        turn_limit = int(getattr(self.config, "extract_turn_limit", 0) or 0)
        turns_since_check = max(0, int(total_turns_abs) - int(self._turns_at_last_extract_check or 0))
        turn_limit_reached = bool(turn_limit > 0 and turns_since_check >= turn_limit)
        topic_changed = (
            heuristic_topic_changed(pending.latest_user, pending.latest_assistant, feedback)
            if feedback
            else False
        )
        feedback_is_ack = heuristic_is_ack_feedback(feedback) if feedback else False

        should_extract = mode == "always"
        if mode == "auto":
            should_check = bool(topic_changed or feedback_is_ack or turn_limit_reached)
            if not should_check:
                # Not a topic boundary and not a periodic checkpoint; skip extraction evaluation for this turn.
                self._pending = None
                return

            # Reset the checkpoint whenever we perform an extraction evaluation so periodic checks
            # do not fire repeatedly, and the counter measures turns since the last evaluation.
            self._turns_at_last_extract_check = int(total_turns_abs)

            gating = (self.config.gating_mode or "llm").lower()
            if gating == "llm" and self.extraction_gate is not None:
                should_extract = self.extraction_gate.should_extract(
                    latest_user=pending.latest_user,
                    latest_assistant=pending.latest_assistant,
                    user_feedback=feedback,
                    topic_changed=topic_changed,
                    total_turns=turns_since_check,
                    turn_limit=turn_limit,
                )
            else:
                # Heuristic gate is intentionally conservative.
                should_extract = heuristic_should_extract(
                    pending.latest_user,
                    pending.latest_assistant,
                    feedback,
                    topic_changed=topic_changed,
                    total_turns=turns_since_check,
                    turn_limit=turn_limit,
                )

        if not should_extract:
            self._pending = None
            return

        try:
            updated = self.sdk.ingest(
                user_id=self.config.user_id,
                messages=pending.messages,
                metadata={"channel": "chat"},
            )
        except Exception as e:
            self.io.print("\n[extract] failed:", str(e))
            self._pending = None
            return

        if updated:
            self.io.print("\n[extract] upserted:", len(updated))
            for s in updated[:20]:
                self.io.print(f"- {s.id} | v{s.version} | {s.name}")
            for s in updated[:3]:
                self._print_skill_md(s.id, label="extract")

        self._pending = None

    def _print_skill_md(self, skill_id: str, *, label: str) -> None:
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
