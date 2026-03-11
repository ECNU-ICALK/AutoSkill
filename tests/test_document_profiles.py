from __future__ import annotations

import json
import os
import tempfile
import unittest

from autoskill.offline.document.extractor import build_document_skill_extractor, extract_skills
from autoskill.offline.document.ingest import ingest_document
from autoskill.offline.document.profile import list_builtin_domain_profiles, load_domain_profile
from autoskill.offline.document.registry import DocumentRegistry


def _profile_extract_response(*, system: str | None, user: str, temperature: float = 0.0, mode: str = "default") -> str:
    _ = system, temperature
    if mode != "document_extract":
        return json.dumps({"skills": []}, ensure_ascii=False)
    payload = json.loads(user)
    profile = payload.get("domain_profile") or {}
    task_keywords = list(profile.get("task_keywords") or [])
    method_keywords = list(profile.get("method_keywords") or [])
    stage_keywords = list(profile.get("stage_keywords") or [])
    task_group = next(
        (
            item for item in task_keywords
            if str(item.get("label") or "").strip() == "scaling_question"
        ),
        (task_keywords[-1] if task_keywords else {}) or {},
    )
    method_group = next(
        (
            item for item in method_keywords
            if str(item.get("label") or "").strip() == "solution_focused"
        ),
        (method_keywords[-1] if method_keywords else {}) or {},
    )
    stage_group = next(
        (
            item for item in stage_keywords
            if str(item.get("label") or "").strip() == "intervention"
        ),
        (stage_keywords[-1] if stage_keywords else {}) or {},
    )
    return json.dumps(
        {
            "skills": [
                {
                    "name": "Scaling question intervention",
                    "description": "Use a scaling question intervention.",
                    "prompt": "# Role & Objective\nUse a scaling question.\n\n# Rules & Constraints\n- Keep the intervention concise.\n\n# Core Workflow\n1. Ask the scaling question.\n\n# Output Format\n- Return the next-step summary.",
                    "domain": profile.get("domain") or "psychology",
                    "task_family": task_group.get("label") or "scaling_question",
                    "method_family": method_group.get("label") or "solution_focused",
                    "stage": stage_group.get("label") or "intervention",
                    "workflow_steps": ["Ask the scaling question."],
                    "constraints": ["Keep the intervention concise."],
                    "cautions": [],
                    "output_contract": ["Return the next-step summary."],
                    "relation_type": "support",
                    "risk_class": "low",
                    "triggers": ["When using a scaling question"],
                    "tags": ["scaling question", "solution focused"],
                    "confidence": 0.9,
                }
            ]
        },
        ensure_ascii=False,
    )


class DocumentProfilesTest(unittest.TestCase):
    def test_builtin_profiles_are_listed_and_loadable(self) -> None:
        names = list_builtin_domain_profiles()

        self.assertIn("default", names)
        self.assertIn("psychology", names)

        profile = load_domain_profile(domain="psychology")
        task_labels = [group.label for group in profile.task_keywords]
        method_labels = [group.label for group in profile.method_keywords]
        stage_labels = [group.label for group in profile.stage_keywords]

        self.assertEqual(profile.domain, "psychology")
        self.assertEqual(profile.default_task_family, "assessment")
        self.assertIn("rapport_building", task_labels)
        self.assertIn("goal_setting", task_labels)
        self.assertIn("cbt", method_labels)
        self.assertIn("systemic_family", method_labels)
        self.assertIn("risk_check", stage_labels)

    def test_custom_profile_override_is_used_by_extractor(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            profile_path = os.path.join(tmpdir, "custom_profile.json")
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "domain": "psychology",
                        "task_keywords": [
                            {"label": "scaling_question", "aliases": ["scaling question"]}
                        ],
                        "method_keywords": [
                            {"label": "solution_focused", "aliases": ["scaling question"]}
                        ],
                        "stage_keywords": [
                            {"label": "intervention", "aliases": ["session intervention"]}
                        ],
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            ingest_result = ingest_document(
                data="""
# Session Intervention
Use a scaling question to help the client rate progress and define the next step.
""".strip(),
                title="Scaling Question Note",
                domain="psychology",
                registry=DocumentRegistry(root_dir=os.path.join(tmpdir, "registry")),
                dry_run=True,
            )
            extracted = extract_skills(
                documents=ingest_result.documents,
                extractor=build_document_skill_extractor(
                    "llm",
                    llm_config={"provider": "mock", "response": _profile_extract_response},
                    domain_profile_path=profile_path,
                ),
            )

            self.assertEqual(len(extracted.skill_drafts), 1)
            draft = extracted.skill_drafts[0]
            self.assertEqual(draft.task_family, "scaling_question")
            self.assertEqual(draft.method_family, "solution_focused")
            self.assertEqual(draft.stage, "intervention")
            self.assertEqual(draft.metadata.get("domain_profile"), "psychology")


if __name__ == "__main__":
    unittest.main()
