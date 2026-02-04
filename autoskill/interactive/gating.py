"""
Extraction gating: decide whether to ingest a new Skill after a chat turn.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..llm.base import LLM
from ..utils.json import json_from_llm_text
from ..utils.text import keywords

_ACK_PREFIXES = (
    "thanks",
    "thank you",
    "thx",
    "ty",
    "ok",
    "okay",
    "got it",
    "understood",
    "sounds good",
    "great",
    "cool",
    "nice",
    "perfect",
)

_REVISION_HINTS = (
    "rewrite",
    "rephrase",
    "revise",
    "edit",
    "modify",
    "change",
    "make it",
    "shorter",
    "longer",
    "simpler",
    "more formal",
    "more casual",
    "more concise",
    "improve",
    "polish",
)

_ASCII_WORD_RE = re.compile(r"[a-z0-9]+")


def _ascii_words(text_lower: str) -> set[str]:
    return {m.group(0) for m in _ASCII_WORD_RE.finditer(text_lower or "")}


def _looks_like_ack(text: str) -> bool:
    s = (text or "").strip().lower()
    if not s:
        return False
    if len(s) <= 40 and any(s.startswith(p) for p in _ACK_PREFIXES):
        return True
    return False


def heuristic_is_ack_feedback(text: str) -> bool:
    """
    Returns True when the user's message looks like a short acknowledgement/closure.

    This is used as a weak topic-boundary signal for extraction timing.
    """

    return _looks_like_ack(text)


def heuristic_topic_changed(latest_user: str, latest_assistant: str, user_feedback: str) -> bool:
    """
    Best-effort topic change detector.

    Returns True when the user feedback likely starts a new (unrelated) topic rather than continuing the
    previous topic. This is intentionally conservative and should be treated as a weak signal.
    """

    fb = (user_feedback or "").strip()
    if not fb:
        return False

    if _looks_like_ack(fb):
        return False

    fb_low = fb.lower()
    fb_words = _ascii_words(fb_low)
    if any(h in fb_low for h in _REVISION_HINTS) and (fb_words & {"it", "this", "that", "above"}):
        return False

    prev_text = f"{(latest_user or '').strip()}\n{(latest_assistant or '').strip()}".strip()
    prev_kws = set(keywords(prev_text, limit=10))
    fb_kws = set(keywords(fb, limit=10))
    if not prev_kws or not fb_kws:
        return False

    overlap = len(prev_kws & fb_kws) / float(max(1, min(len(prev_kws), len(fb_kws))))
    if overlap >= 0.25:
        return False

    if any(h in fb_low for h in ("by the way", "new topic", "another question", "separate question", "unrelated")):
        return True

    has_followup_ref = bool(fb_words & {"it", "this", "that", "above", "previous", "earlier", "regarding"})
    has_followup_ref = has_followup_ref or any(p in fb_low for p in ("the above", "about that"))
    if overlap <= 0.10 and len(fb) >= 40 and not has_followup_ref:
        return True

    return False


def heuristic_should_extract(
    latest_user: str,
    latest_assistant: str,
    user_feedback: str | None = None,
    *,
    topic_changed: bool | None = None,
    total_turns: int | None = None,
    turn_limit: int | None = None,
) -> bool:
    exchange = f"{latest_user}\n{latest_assistant}".lower()
    structured = False
    if any(x in exchange for x in ["->", "=>", "steps", "checklist", "workflow", "sop", "process"]):
        structured = True
    if "\n" in (latest_user or "") and any(p in (latest_user or "") for p in ["- ", "* ", "1.", "1)"]):
        structured = True
    if not structured:
        return False

    fb = (user_feedback or "").strip()
    if fb:
        fb_low = fb.lower()
        fb_words = _ascii_words(fb_low)
        if any(x in fb_low for x in ("did not work", "doesn't work", "does not work", "error", "failed", "wrong")):
            return False
        if any(h in fb_low for h in _REVISION_HINTS) and (fb_words & {"it", "this", "that", "above"}):
            return False

    boundary = False
    if fb and _looks_like_ack(fb):
        boundary = True
    if topic_changed:
        boundary = True
    if (
        isinstance(total_turns, int)
        and isinstance(turn_limit, int)
        and int(turn_limit) > 0
        and int(total_turns) >= int(turn_limit)
    ):
        boundary = True

    return bool(boundary)


@dataclass
class LLMExtractionGate:
    llm: LLM

    def should_extract(
        self,
        *,
        latest_user: str,
        latest_assistant: str,
        user_feedback: str | None = None,
        topic_changed: bool | None = None,
        total_turns: int | None = None,
        turn_limit: int | None = None,
    ) -> bool:
        topic_changed_b = bool(topic_changed)
        turn_limit_reached = (
            isinstance(total_turns, int)
            and isinstance(turn_limit, int)
            and int(turn_limit) > 0
            and int(total_turns) >= int(turn_limit)
        )
        feedback_is_ack = _looks_like_ack(user_feedback) if user_feedback else False
        system = (
            "You are AutoSkill's extraction gate.\n"
            "Decide whether the provided user+assistant exchange contains a HIGH-QUALITY, REUSABLE Skill worth storing.\n"
            "Be conservative: default to false.\n"
            "\n"
            "A Skill is a modular, self-contained capability artifact (a SKILL.md package) that onboards another assistant instance with:\n"
            "- specialized workflows (multi-step procedures)\n"
            "- tool-specific operating procedures\n"
            "- domain constraints/decision rules\n"
            "- stable user/team preferences (style rubrics, conventions)\n"
            "\n"
            "Metadata quality matters: if you cannot write a concise name + a 1-2 sentence description that clearly signals WHEN the skill should be used, do not extract.\n"
            "\n"
            "User feedback (if provided) is the NEXT user message after the assistant response.\n"
            "Use feedback as a quality signal:\n"
            "- If the feedback indicates the solution did NOT work, set should_extract=false.\n"
            "- If the feedback indicates it worked / user is satisfied, that increases confidence.\n"
            "- If the feedback is a revision request (the user asks to change/edit/refine the assistant output), treat the previous exchange as NOT verified; default to should_extract=false.\n"
            "  - Exception: if the revision message contains an explicit, stable preference or constraint that should apply in future (e.g., \"From now on, always format X as Y\"), you may extract a preference Skill.\n"
            "- If the feedback starts a new, unrelated topic, treat the previous exchange as likely complete (verified=\"unknown\").\n"
            "  - This is a timing signal (topic boundary), not proof of quality.\n"
            "\n"
            "Prefer extracting when the solution is either:\n"
            "- personalized (stable user preference, environment constraint, or team convention), OR\n"
            "- non-obvious/specialized (edge-case handling, tricky debugging steps, tool-specific workflow), OR\n"
            "- a repeatable workflow that would benefit from being packaged (SKILL.md + optional scripts/references/assets), OR\n"
            "- something the base model is likely to be inconsistent at without this learned artifact.\n"
            "\n"
            "Long conversation signal:\n"
            "- If turns_since_last_check >= turn_limit, consider extracting at boundaries/checkpoints to avoid missing reusable preferences/workflows.\n"
            "  - This is a timing signal, not proof of quality.\n"
            "\n"
            "User-centered necessity:\n"
            "- Do NOT extract generic, first-draft outputs as Skills (e.g., a generic resume template the user is still editing).\n"
            "- Prefer extracting AFTER the user's requirements/preferences have been clarified and the assistant has produced a version that matches them.\n"
            "- For iterative writing tasks, the Skill to store is the user's editing rubric/style constraints (what 'good' means), not the draft text itself.\n"
            "\n"
            "Return should_extract=true ONLY if ALL are true:\n"
            "1) Reusable: likely to be useful again in future (not a one-off).\n"
            "2) Actionable: can be written as a standalone SKILL.md Prompt with clear steps/checks/output format.\n"
            "3) Generalizable: not tied to specific people/projects/secrets/URLs; not dependent on this conversation.\n"
            "4) Sufficient signal: more than trivial advice; not just a single sentence acknowledgement.\n"
            "\n"
            "Return should_extract=false for:\n"
            "- casual chat/acknowledgements\n"
            "- one-off facts, transient status updates, or highly specific debugging\n"
            "- generic platitudes (e.g., \"be careful\")\n"
            "- incomplete guidance that cannot form an executable Skill prompt\n"
            "\n"
            "Output ONLY strict JSON (no Markdown, no commentary):\n"
            "{\"should_extract\": true|false, \"type\": \"process|checklist|rule|template|preference|other\", \"quality\": 0.0-1.0, \"verified\": true|false|\"unknown\", \"reason\": \"...\"}\n"
            "Set should_extract=true only if quality >= 0.70.\n"
        )
        if user_feedback and user_feedback.strip():
            user = (
                "Signals:\n"
                f"- topic_changed: {str(topic_changed_b).lower()}\n"
                f"- feedback_is_ack: {str(feedback_is_ack).lower()}\n"
                f"- turns_since_last_check: {total_turns}\n"
                f"- turn_limit: {turn_limit}\n\n"
                f"User message:\n{latest_user.strip()}\n\n"
                f"Assistant response:\n{latest_assistant.strip()}\n\n"
                f"User feedback:\n{user_feedback.strip()}\n"
            )
        else:
            user = (
                "Signals:\n"
                f"- topic_changed: {str(topic_changed_b).lower()}\n"
                f"- feedback_is_ack: {str(feedback_is_ack).lower()}\n"
                f"- turns_since_last_check: {total_turns}\n"
                f"- turn_limit: {turn_limit}\n\n"
                f"User message:\n{latest_user.strip()}\n\n"
                f"Assistant response:\n{latest_assistant.strip()}\n"
            )
        try:
            text = self.llm.complete(system=system, user=user, temperature=0.0)
        except Exception:
            return heuristic_should_extract(
                latest_user,
                latest_assistant,
                user_feedback,
                topic_changed=topic_changed_b,
                total_turns=total_turns,
                turn_limit=turn_limit,
            )
        try:
            obj = json_from_llm_text(text)
        except Exception:
            return heuristic_should_extract(
                latest_user,
                latest_assistant,
                user_feedback,
                topic_changed=topic_changed_b,
                total_turns=total_turns,
                turn_limit=turn_limit,
            )
        if isinstance(obj, dict):
            v = obj.get("should_extract")
            q = obj.get("quality")
            verified = obj.get("verified")

            should = False
            if isinstance(v, bool):
                should = v
            elif isinstance(v, str):
                should = v.strip().lower() in {"true", "yes", "1"}
            elif isinstance(v, (int, float)):
                should = bool(v)

            quality: float | None = None
            if isinstance(q, (int, float)):
                quality = float(q)
            elif isinstance(q, str):
                try:
                    quality = float(q.strip())
                except ValueError:
                    quality = None

            verified_s: str = "unknown"
            if isinstance(verified, bool):
                verified_s = "true" if verified else "false"
            elif isinstance(verified, str):
                verified_s = verified.strip().lower()

            if user_feedback and verified_s == "false":
                return False

            if quality is not None:
                threshold = 0.70 if (user_feedback and verified_s == "true") else 0.85
                if str(obj.get("type") or "").strip().lower() == "preference":
                    threshold = 0.65 if (user_feedback and verified_s in {"true", "unknown"}) else 0.75
                if feedback_is_ack and verified_s == "unknown":
                    threshold = min(threshold, 0.80)
                return bool(should and quality >= threshold)

            return bool(should)
        return heuristic_should_extract(
            latest_user,
            latest_assistant,
            user_feedback,
            topic_changed=topic_changed_b,
            total_turns=total_turns,
            turn_limit=turn_limit,
        )
