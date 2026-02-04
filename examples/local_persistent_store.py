"""
Local persistent store demo (offline).

This example uses:
- heuristic extraction (no network)
- hashing embeddings (no network)
- LocalSkillStore (directory-based persistence: one skill folder per skill)

Run it multiple times to verify skills persist across runs and merges happen instead of duplicates.
"""

from __future__ import annotations

import os

from autoskill import AutoSkill, AutoSkillConfig


def main() -> None:
    store_dir = os.getenv("AUTOSKILL_STORE_DIR") or os.getenv("AUTOSKILL_STORE_PATH") or "Skills"

    sdk = AutoSkill(
        AutoSkillConfig(
            llm={"provider": "mock"},
            embeddings={"provider": "hashing", "dims": 256},
            store={"provider": "local", "path": store_dir},
        )
    )

    existing = sdk.list(user_id="u1")
    print("Store dir:", store_dir)
    print("Existing skills:", len(existing))

    sdk.ingest(
        user_id="u1",
        messages=[
            {
                "role": "user",
                "content": "Before each release: run regression tests -> canary rollout -> monitor -> full rollout.",
            },
            {"role": "assistant", "content": "Understood."},
        ],
        metadata={"channel": "local-persistent-demo"},
    )

    skills = sdk.list(user_id="u1")
    print("Skills after ingest:", len(skills))

    query = "How should I do a release?"
    hits = sdk.search(query, user_id="u1", limit=3)
    for h in hits:
        print(f"{h.score:.3f} - {h.skill.name}")

    if hits:
        print("\n--- SKILL.md ---")
        print(sdk.export_skill_md(hits[0].skill.id) or "")


if __name__ == "__main__":
    main()
