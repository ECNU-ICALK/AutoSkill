from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN_DIR = _REPO_ROOT / "AutoSkill4OpenClaw"
if str(_PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_prompt_profile import (  # noqa: E402
    _build_openclaw_agentic_extract_prompt,
    _build_openclaw_agentic_repair_prompt,
    _decide_candidate_action_with_llm_agentic,
    _merge_with_llm_agentic,
)
from autoskill.management.extraction import SkillCandidate  # noqa: E402
from autoskill.models import Skill, SkillExample  # noqa: E402


class _FakeLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.system = ""
        self.user = ""
        self.temperature = 0.0

    def complete(self, *, system: str, user: str, temperature: float = 0.0) -> str:
        self.system = str(system)
        self.user = str(user)
        self.temperature = float(temperature)
        return self.response


class OpenClawAgenticPromptProfileTest(unittest.TestCase):
    def test_extract_prompt_targets_standard_agent_skill_without_examples_field(self) -> None:
        prompt = _build_openclaw_agentic_extract_prompt(max_candidates=3)

        self.assertIn("standard agent skill artifact used by OpenClaw", prompt)
        self.assertIn("SKILL.md plus optional scripts/, references/, and assets/", prompt)
        self.assertIn("Triggerability matters: name and description are the always-loaded metadata", prompt)
        self.assertIn("move bulky schemas, policies, and examples into references/", prompt)
        self.assertIn("Do not invent README/installation/changelog style files.", prompt)
        self.assertIn('resources shape: {"scripts": [...], "references": [...], "assets": [...]}', prompt)
        self.assertIn('files shape: {"scripts/...": "...", "references/...": "...", "assets/...": "..."}', prompt)
        self.assertIn("Do not invent metadata examples.", prompt)
        self.assertNotIn("  - examples:", prompt)

    def test_repair_prompt_keeps_standard_agent_skill_schema(self) -> None:
        prompt = _build_openclaw_agentic_repair_prompt(max_candidates=2)

        self.assertIn(
            "Keep schema fields: name, description, prompt, triggers, tags, confidence; optional resources/files are allowed.",
            prompt,
        )
        self.assertIn("standard agent skill format used by OpenClaw", prompt)
        self.assertIn("name/description are the future trigger metadata", prompt)
        self.assertIn("move detailed reusable guidance into references/", prompt)
        self.assertIn("Never invent auxiliary docs like README.md or installation guides.", prompt)
        self.assertIn("scripts/, references/, or assets/", prompt)
        self.assertNotIn("tags, examples, confidence", prompt)

    def test_decision_prompt_prefers_merge_for_resource_additions(self) -> None:
        llm = _FakeLLM('{"action":"discard","target_skill_id":null,"reason":"not needed"}')
        cand = SkillCandidate(
            name="OpenClaw release workflow",
            description="Release workflow with checks.",
            instructions="# Goal\nShip safely.\n",
            triggers=["release workflow"],
            tags=["release"],
            examples=[],
            files={"scripts/release-check.sh": "echo ok"},
        )

        _decide_candidate_action_with_llm_agentic(
            llm,
            cand,
            [],
            user_id="u-test",
            dedupe_threshold=0.8,
        )

        self.assertIn(
            "If candidate mainly adds reusable scripts/references/assets for the same capability, prefer merge.",
            llm.system,
        )
        self.assertIn(
            "If candidate only contributes copied one-off payload files or bulky inline references, prefer discard.",
            llm.system,
        )
        self.assertIn(
            "Favor skills whose name/description will be easy for OpenClaw to route in future similar requests.",
            llm.system,
        )

    def test_merge_prompt_ignores_examples_from_llm_output(self) -> None:
        llm = _FakeLLM(
            json.dumps(
                {
                    "name": "OpenClaw release workflow",
                    "description": "Use for recurring release runs.",
                    "prompt": "# Goal\nShip safely.\n\n# Constraints & Style\n- Verify before deploy.\n",
                    "triggers": ["release workflow", "deployment checklist"],
                    "tags": ["release", "ops"],
                    "examples": [{"input": "this should be ignored"}],
                }
            )
        )
        existing = Skill(
            id="skill-1",
            user_id="u-test",
            name="Release process",
            description="Existing release process.",
            instructions="# Goal\nRelease.\n",
            triggers=["release process"],
            tags=["ops"],
            examples=[SkillExample(input="keep existing example")],
        )
        cand = SkillCandidate(
            name="OpenClaw release workflow",
            description="Release workflow with checks.",
            instructions="# Goal\nShip safely.\n",
            triggers=["release workflow"],
            tags=["release"],
            examples=[],
            files={"references/release.md": "checklist"},
        )

        merged = _merge_with_llm_agentic(llm, existing, cand)

        self.assertIn(
            "Output ONLY strict JSON with fields: name, description, prompt, triggers, tags.",
            llm.system,
        )
        self.assertIn(
            "Do not add example sections or example payloads; examples are not part of the required output schema.",
            llm.system,
        )
        self.assertIn("Execute script: scripts/... or Read reference: references/...", llm.system)
        self.assertIn("Keep name/description highly triggerable because they are the primary routing metadata.", llm.system)
        self.assertIn("Keep detailed schemas, policies, and examples out of the prompt body", llm.system)
        self.assertIn(
            "Do not introduce auxiliary files or documentation concepts outside SKILL.md plus optional scripts/references/assets.",
            llm.system,
        )
        self.assertEqual(len(merged.examples), 1)
        self.assertEqual(merged.examples[0].input, "keep existing example")


if __name__ == "__main__":
    unittest.main()
