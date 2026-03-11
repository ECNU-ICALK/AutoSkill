from __future__ import annotations

import tempfile
import unittest

from autoskill.management.formats.agent_skill import build_agent_skill_files, load_agent_skill_dir
from autoskill.models import Skill, SkillExample


class AgentSkillFormatTest(unittest.TestCase):
    def test_examples_round_trip_through_skill_md(self) -> None:
        skill = Skill(
            id="skill-1",
            user_id="u1",
            name="doc skill",
            description="Rich document-derived skill.",
            instructions="Use the structured counseling prompt.",
            triggers=["When intake starts"],
            tags=["psychology"],
            examples=[
                SkillExample(
                    input="Client says they feel stuck and overwhelmed.",
                    output="Reflect the overwhelm, then ask which part feels most urgent today.",
                    notes="Keep the intervention concrete.",
                )
            ],
        )

        files = build_agent_skill_files(skill)
        self.assertIn("examples:", files["SKILL.md"])

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = tmpdir
            with open(f"{skill_dir}/SKILL.md", "w", encoding="utf-8") as handle:
                handle.write(files["SKILL.md"])

            loaded = load_agent_skill_dir(skill_dir, user_id="u1")

        self.assertEqual(len(loaded.examples), 1)
        self.assertEqual(loaded.examples[0].input, "Client says they feel stuck and overwhelmed.")


if __name__ == "__main__":
    unittest.main()
