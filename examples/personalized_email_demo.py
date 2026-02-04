"""
Offline interactive demo: extract a personalized email-writing Skill and verify retrieval.

This demo does NOT call real LLM APIs. It uses:
- hashing embeddings (offline)
- a tiny in-process LLM stub for chat responses
- a tiny in-process LLM stub for skill extraction JSON

Run:
  python3 -m examples.personalized_email_demo

Notes:
- Similarity scores with hashing embeddings are not comparable to real semantic embeddings.
  This demo sets min_score=0.0 so you can observe retrieval behavior offline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from autoskill import AutoSkill, AutoSkillConfig
from autoskill.interactive import InteractiveChatApp, InteractiveConfig
from autoskill.llm.base import LLM
from autoskill.skill_management.extraction import LLMSkillExtractor


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value is not None and value.strip() else default


def _last_user_message(conversation_block: str) -> str:
    lines = [ln.strip() for ln in (conversation_block or "").splitlines() if ln.strip()]
    for ln in reversed(lines):
        if ln.startswith("User:"):
            return ln.split(":", 1)[1].strip()
    return ""


@dataclass
class ScriptedIO:
    inputs: List[str]
    echo_inputs: bool = True

    def input(self, prompt: str) -> str:
        if not self.inputs:
            raise EOFError()
        line = self.inputs.pop(0)
        if self.echo_inputs:
            print(prompt + line)
        return line

    def print(self, *args, **kwargs) -> None:
        print(*args, **kwargs)


class EmailDemoChatLLM(LLM):
    """
    Tiny chat LLM stub.

    It detects whether Skills were injected and formats an email accordingly.
    """

    def complete(self, *, system: Optional[str], user: str, temperature: float = 0.0) -> str:
        latest_user = _last_user_message(user)
        has_skills = bool(system and "## AutoSkill Skills" in system)

        if not latest_user:
            return "(no user message)"

        if any(k in latest_user.lower() for k in ["make it", "more concise", "rewrite", "shorter"]):
            return (
                "Subject options:\n"
                "1) Quick question about <TOPIC>\n"
                "2) <COMPANY> x <YOUR_COMPANY>\n"
                "3) Idea to reduce <PAIN_POINT>\n\n"
                "Hi <RECIPIENT_NAME>,\n\n"
                "I noticed <CONTEXT_SIGNAL>. If you're looking to improve <GOAL>, "
                "we've helped teams like <PEER_GROUP> with:\n"
                "- <VALUE_PROP_1>\n"
                "- <VALUE_PROP_2>\n"
                "- <VALUE_PROP_3>\n\n"
                "Open to a 15-minute chat next week? If not, who is best to speak with?\n\n"
                "Best,\n"
                "<YOUR_NAME>\n"
            )

        if has_skills:
            return (
                "Subject options:\n"
                "1) <COMPANY> x <YOUR_COMPANY>\n"
                "2) Reduce <PAIN_POINT> for <TEAM>\n"
                "3) Quick idea for <GOAL>\n\n"
                "Hi <RECIPIENT_NAME>,\n\n"
                "Reaching out because <PERSONALIZED_CONTEXT>. If you're working on <GOAL>, "
                "a quick idea:\n"
                "- <VALUE_PROP_1>\n"
                "- <VALUE_PROP_2>\n\n"
                "If it helps, happy to share a 1-page summary. Would a quick 15 minutes work this week?\n\n"
                "Best,\n"
                "<YOUR_NAME>\n"
            )

        return (
            "Subject: Quick question about <TOPIC>\n\n"
            "Hi <RECIPIENT_NAME>,\n\n"
            "I’m reaching out because <REASON>. We help <AUDIENCE> achieve <OUTCOME> by <HOW>.\n\n"
            "Would you be open to a quick call to see if this is relevant?\n\n"
            "Best,\n"
            "<YOUR_NAME>\n"
        )


class HintAwareExtractionLLM(LLM):
    """
    Tiny extraction LLM stub.

    It reads DATA.hint from the extractor input and returns a single Skill JSON payload.
    """

    def complete(self, *, system: Optional[str], user: str, temperature: float = 0.0) -> str:
        hint = ""
        try:
            obj = json.loads(user)
            hint = str(obj.get("hint") or "").strip()
        except Exception:
            hint = ""

        hint_s = hint or "Write personalized cold outreach emails in a consistent style."
        slug = re.sub(r"[^a-z0-9]+", "-", hint_s.lower()).strip("-")
        slug = (slug[:48] or "personalized-email-writing").strip("-")
        name = slug
        description = (
            "This skill should be used when writing personalized outreach emails in the user's preferred style "
            "(concise, friendly, and action-oriented)."
        )
        prompt = (
            "Goal: Write a personalized outreach email in a consistent style.\n"
            "\n"
            "Inputs (ask if missing):\n"
            "- <RECIPIENT_NAME>, <RECIPIENT_ROLE>, <COMPANY>\n"
            "- <YOUR_COMPANY>, <OFFER>, <PROOF>, <CTA>\n"
            "- Any relevant context signal (<CONTEXT_SIGNAL>)\n"
            "\n"
            "Steps:\n"
            "1) Clarify the intent: cold outreach, follow-up, intro, or re-engagement.\n"
            "2) Identify ONE concrete reason for relevance using <CONTEXT_SIGNAL> (do not invent facts).\n"
            "3) Draft 3 subject lines (short, specific, non-salesy).\n"
            "4) Draft the email body:\n"
            "   - Greeting + relevance sentence\n"
            "   - 2–3 bullet value props\n"
            "   - Proof point (<PROOF>)\n"
            "   - Clear CTA (<CTA>)\n"
            "5) Quality checks:\n"
            "   - <= 120 words (unless user requests longer)\n"
            "   - Friendly, not overly promotional\n"
            "   - No jargon; concrete nouns/verbs\n"
            "   - Single clear ask\n"
            "\n"
            "Output format:\n"
            "- Subject options: 1) ... 2) ... 3) ...\n"
            "- Email:\n"
            "  Hi <RECIPIENT_NAME>, ...\n"
            "\n"
            f"Focus hint (from user): {hint_s}\n"
        )
        out = {
            "skills": [
                {
                    "name": name,
                    "description": description,
                    "prompt": prompt,
                    "triggers": [
                        "This skill should be used when writing a cold outreach email.",
                        "This skill should be used when the user asks for email tone/style consistency.",
                        "This skill should be used when generating subject lines plus a concise body.",
                    ],
                    "tags": ["email", "writing", "outreach"],
                    "examples": [],
                    "confidence": 0.9,
                }
            ]
        }
        return json.dumps(out, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline personalized email Skill demo")
    parser.add_argument("--store-dir", default=_env("AUTOSKILL_STORE_DIR", "SkillsEmailDemo"))
    parser.add_argument("--user-id", default=_env("AUTOSKILL_USER_ID", "email_demo"))
    args = parser.parse_args()

    sdk_cfg = AutoSkillConfig(
        llm={"provider": "mock"},
        embeddings={"provider": "hashing", "dims": 256},
        store={"provider": "local", "path": str(args.store_dir), "include_libraries": False},
        maintenance_strategy="heuristic",
    )

    extractor = LLMSkillExtractor(sdk_cfg, llm=HintAwareExtractionLLM())
    sdk = AutoSkill(sdk_cfg, extractor=extractor)

    interactive_cfg = InteractiveConfig(
        store_dir=str(args.store_dir),
        user_id=str(args.user_id),
        skill_scope="user",
        rewrite_mode="never",
        min_score=0.0,  # hashing embeddings produce small cosine scores; keep visible in demo.
        top_k=5,
        extract_mode="never",  # use /extract_now explicitly in this demo
    ).normalize()

    scripted_inputs = [
        "Help me write a cold outreach email to a CTO about our product.",
        "Make it more concise, include bullet points, and propose 3 subject lines. Keep it friendly and not salesy.",
        "Looks good, thanks.",
        "/extract_now A reusable skill for writing cold outreach emails in my preferred style: concise, friendly, 3 subject lines, 2-3 bullet value props, clear CTA, placeholders.",
        "Write another cold outreach email to a VP of Engineering. Keep the same style.",
        "/search cold outreach email subject lines",
        "/skills",
        "/exit",
    ]

    app = InteractiveChatApp(
        sdk=sdk,
        config=interactive_cfg,
        io=ScriptedIO(scripted_inputs),
        chat_llm=EmailDemoChatLLM(),
    )
    app.run()


if __name__ == "__main__":
    main()

