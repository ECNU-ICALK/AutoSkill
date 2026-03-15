from __future__ import annotations

import json
import os
import tempfile
import unittest

from autoskill.llm.mock import MockLLM

from AutoSkill4Doc.document.windowing import build_windows_for_record
from AutoSkill4Doc.models import DocumentRecord, DocumentSection, TextSpan
from AutoSkill4Doc.prompts import OFFLINE_CHANNEL_DOC, build_offline_extract_prompt
from AutoSkill4Doc.stages.extractor import build_document_skill_extractor, extract_skills
from AutoSkill4Doc.taxonomy import list_builtin_skill_taxonomies, load_skill_taxonomy


def _chemistry_extract_response(*, system: str | None, user: str, temperature: float = 0.0, mode: str = "default") -> str:
    _ = system, temperature, user, mode
    return json.dumps(
        {
            "skills": [
                {
                    "name": "TLC analysis workflow",
                    "description": "Run a thin-layer chromatography analysis workflow.",
                    "prompt": "# Goal\nRun the TLC workflow.\n\n# Core Workflow\n1. Prepare the plate.\n2. Spot the sample.\n3. Develop the plate.\n4. Read the bands.\n\n# Output Format\n- Output the Rf summary.",
                    "asset_type": "experiment_workflow",
                    "granularity": "session",
                    "objective": "Run a TLC analysis workflow.",
                    "domain": "chemistry",
                    "task_family": "analysis",
                    "method_family": "tlc",
                    "stage": "analysis",
                    "workflow_steps": [
                        "Prepare the plate.",
                        "Spot the sample.",
                        "Develop the plate.",
                        "Read the bands.",
                    ],
                    "constraints": ["Use the configured solvent system."],
                    "output_contract": ["Output the Rf summary."],
                    "relation_type": "support",
                    "risk_class": "low",
                    "confidence": 0.9,
                }
            ]
        },
        ensure_ascii=False,
    )


class DocumentTaxonomyTest(unittest.TestCase):
    def test_builtin_taxonomies_are_listed(self) -> None:
        names = list_builtin_skill_taxonomies()
        self.assertIn("default", names)
        self.assertIn("psychology", names)
        self.assertIn("chemistry", names)

    def test_builtin_taxonomy_maps_aliases_to_internal_base_type(self) -> None:
        taxonomy = load_skill_taxonomy(domain_type="chemistry")
        self.assertEqual(taxonomy.domain_type, "chemistry")
        self.assertEqual(taxonomy.normalize_asset_type("experiment_workflow"), "session_skill")
        self.assertEqual(taxonomy.normalize_asset_type("reagent_safety_rule"), "safety_rule")
        self.assertEqual(taxonomy.resolve_axis_label(), "实验路线")
        self.assertEqual(taxonomy.resolve_family_name(), "通用化学流程")

    def test_psychology_taxonomy_uses_expected_family_candidates(self) -> None:
        taxonomy = load_skill_taxonomy(domain_type="psychology")

        self.assertEqual(
            [str(item.get("id") or "") for item in taxonomy.family_candidates],
            [
                "psychodynamic",
                "behaviorism",
                "cbt",
                "humanistic_existentialist",
                "postmodernist",
            ],
        )
        self.assertEqual(taxonomy.family_candidates[0]["name"], "Psychodynamic（心理动力学）")
        self.assertIn("行为主义", list(taxonomy.family_candidates[1].get("aliases") or []))
        self.assertIn("认知行为疗法", list(taxonomy.family_candidates[2].get("aliases") or []))
        self.assertIn("人本-存在主义", list(taxonomy.family_candidates[3].get("aliases") or []))
        self.assertIn("后现代主义", list(taxonomy.family_candidates[4].get("aliases") or []))

    def test_custom_taxonomy_path_overrides_aliases(self) -> None:
        payload = """
{
  "taxonomy_id": "geo_custom",
  "domain_type": "geography",
  "display_name": "Geography",
  "default_base_type": "knowledge_reference",
  "asset_types": [
    {
      "base_type": "session_skill",
      "label": "field_workflow",
      "description": "One reusable field workflow.",
      "aliases": ["field_workflow", "survey_workflow"]
    }
  ]
}
""".strip()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "taxonomy.yaml")
            with open(path, "w", encoding="utf-8") as f:
                f.write(payload)
            taxonomy = load_skill_taxonomy(domain_type="geography", taxonomy_path=path)

        self.assertEqual(taxonomy.taxonomy_id, "geo_custom")
        self.assertEqual(taxonomy.domain_type, "geography")
        self.assertEqual(taxonomy.normalize_asset_type("field_workflow"), "session_skill")
        self.assertEqual(taxonomy.normalize_asset_type(""), "knowledge_reference")
        self.assertEqual(taxonomy.derive_profile_id(family_name="地理专题"), "geo_custom::地理专题")

    def test_prompt_includes_domain_type_guidance(self) -> None:
        taxonomy = load_skill_taxonomy(domain_type="psychology")
        prompt = build_offline_extract_prompt(
            channel=OFFLINE_CHANNEL_DOC,
            max_candidates=2,
            taxonomy=taxonomy,
        )

        self.assertIn("Domain type is externally provided as `psychology`", prompt)
        self.assertIn("Do not infer or output domain_type", prompt)
        self.assertIn("session_intervention -> session_skill", prompt)

    def test_extractor_normalizes_taxonomy_alias_into_stable_asset_type(self) -> None:
        record = DocumentRecord(
            doc_id="chem-doc-1",
            source_type="markdown_document",
            title="TLC Notes",
            domain="chemistry",
            raw_text="# Analysis\nRun a TLC workflow.\n",
            sections=[
                DocumentSection(
                    heading="Analysis",
                    text="Run a TLC workflow with plate prep, spotting, development, and reading.",
                    span=TextSpan(start=0, end=72),
                )
            ],
            content_hash="chem-doc-1-hash",
        )
        windows = build_windows_for_record(record=record, strategy="strict")
        extractor = build_document_skill_extractor(
            "llm",
            llm=MockLLM(response=_chemistry_extract_response),
            domain_type="chemistry",
        )

        result = extract_skills(documents=[record], windows=windows, extractor=extractor)

        self.assertEqual(len(result.skill_drafts), 1)
        draft = result.skill_drafts[0]
        self.assertEqual(draft.asset_type, "session_skill")
        self.assertEqual(draft.metadata.get("domain_type"), "chemistry")
        self.assertEqual(draft.metadata.get("taxonomy_id"), "chemistry")
