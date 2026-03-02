"""
Offline example: heuristic extraction + hashing embeddings + inmemory store.

Validates the minimal SDK loop:
ingest -> search -> render_context -> export SKILL.md
"""

from autoskill import AutoSkill, AutoSkillConfig


def main() -> None:
    """Run main."""
    user_message = (
        "Before each release: run regression tests -> canary rollout -> monitor -> full rollout."
    )
    assistant_ack = "Got it."
    query = "How should I do a release?"

    sdk = AutoSkill(
        AutoSkillConfig(
            llm={"provider": "mock"},
            embeddings={"provider": "hashing", "dims": 256},
            store={"provider": "inmemory"},
        )
    )

    sdk.ingest(
        user_id="u1",
        messages=[
            {
                "role": "user",
                "content": user_message,
            },
            {"role": "assistant", "content": assistant_ack},
        ],
        metadata={"channel": "demo"},
    )

    hits = sdk.search(query, user_id="u1", limit=5)
    for h in hits:
        print(f"{h.score:.3f} - {h.skill.name}: {h.skill.description}")

    print("\n--- Rendered Context ---")
    print(f"Query: {query}")
    print(sdk.render_context(query, user_id="u1"))

    # Export as Agent Skill artifact (SKILL.md)
    if hits:
        exported = sdk.export_skill_md(hits[0].skill.id)
        print("\n--- SKILL.md ---")
        print(exported)


if __name__ == "__main__":
    main()
