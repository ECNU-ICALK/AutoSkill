from __future__ import annotations

import json
import os
import tempfile
import unittest

from autoskill import AutoSkill, AutoSkillConfig
from AutoSkill4Doc.stages.compiler import _identity_key_for_skill, build_skill_compiler, compile_skills
from AutoSkill4Doc.stages.extractor import build_document_skill_extractor, extract_skills
from AutoSkill4Doc.extract import extract_from_doc
from AutoSkill4Doc.models import SkillDraft, SupportRecord, SupportRelation, TextSpan, VersionState
from AutoSkill4Doc.pipeline import build_default_document_pipeline
from AutoSkill4Doc.prompts import OFFLINE_CHANNEL_DOC, build_offline_extract_prompt
from AutoSkill4Doc.store.layout import intermediate_runs_root


_DOC_TEXT = """
# Intake
1. Build rapport before deeper intervention.
2. Clarify the client's immediate concern.

# Constraints
Do not push interpretation before the client is ready.
Always check for acute risk before intensive exploration.

# Output
Output a short session direction summary.
""".strip()


def _document_llm_response(*, system: str | None, user: str, temperature: float = 0.0, mode: str = "default") -> str:
    _ = system, temperature
    if mode == "document_extract":
        payload = json.loads(user)
        document = payload.get("document", {})
        excerpt = str(payload.get("excerpt") or "").strip()
        return json.dumps(
            {
                "skills": [
                    {
                        "name": f"{document.get('domain') or 'document'} intake workflow",
                        "description": "Reusable workflow extracted from the document.",
                        "prompt": (
                            "# Role & Objective\n"
                            "Guide the operator through the reusable workflow.\n\n"
                            "# Rules & Constraints\n"
                            "- Keep the process safe and structured.\n\n"
                            "# Core Workflow\n"
                            "1. Build rapport first.\n"
                            "2. Clarify the immediate concern.\n"
                            "3. Check acute risk before deeper exploration.\n\n"
                            "# Output Format\n"
                            "- Output a short session direction summary."
                        ),
                        "asset_type": "session_skill",
                        "granularity": "session",
                        "objective": "Run a structured first-session intake.",
                        "domain": document.get("domain") or "psychology",
                        "task_family": "intake",
                        "method_family": "structured_interview",
                        "stage": "intake",
                        "applicable_signals": [
                            "When the client is entering an initial consultation.",
                        ],
                        "intervention_moves": [
                            "Reflect the client's main concern before moving deeper.",
                        ],
                        "contraindications": [
                            "Do not skip acute risk screening when crisis cues are present.",
                        ],
                        "workflow_steps": [
                            "Build rapport first.",
                            "Clarify the immediate concern.",
                            "Check acute risk before deeper exploration.",
                        ],
                        "constraints": [
                            "Keep the process safe and structured.",
                        ],
                        "cautions": [
                            "Avoid intensive interpretation too early.",
                        ],
                        "output_contract": [
                            "Output a short session direction summary.",
                        ],
                        "examples": [
                            {
                                "input": "Client says they feel overwhelmed and do not know where to start.",
                                "output": "Reflect the overwhelm first, then ask for the most urgent concern to focus the session.",
                                "notes": "Use a calm, non-rushing tone.",
                            }
                        ],
                        "relation_type": "conflict" if "do not" in excerpt.lower() else "support",
                        "risk_class": "medium",
                        "triggers": [
                            "When starting intake",
                            "When clarifying a first session",
                            "When documenting session direction",
                        ],
                        "tags": ["psychology", "intake", "workflow"],
                        "confidence": 0.92,
                    }
                ]
            },
            ensure_ascii=False,
        )
    if mode == "document_compile":
        payload = json.loads(user)
        drafts = list(payload.get("drafts") or [])
        first = drafts[0]
        support_ids: list[str] = []
        for draft in drafts:
            support_ids.extend(list(draft.get("support_ids") or []))
        return json.dumps(
            {
                "skills": [
                    {
                        "name": first.get("name") or "document intake workflow",
                        "description": "Canonical reusable workflow compiled from document drafts.",
                        "prompt": first.get("metadata", {}).get("prompt") or first.get("name") or "prompt",
                        "asset_type": first.get("asset_type") or "session_skill",
                        "granularity": first.get("granularity") or "session",
                        "objective": first.get("objective") or first.get("description") or "objective",
                        "domain": first.get("domain") or "psychology",
                        "task_family": first.get("task_family") or "intake",
                        "method_family": first.get("method_family") or "structured_interview",
                        "stage": first.get("stage") or "intake",
                        "applicable_signals": first.get("applicable_signals") or [],
                        "intervention_moves": first.get("intervention_moves") or [],
                        "contraindications": first.get("contraindications") or [],
                        "triggers": first.get("triggers") or [],
                        "workflow_steps": first.get("workflow_steps") or [],
                        "constraints": first.get("constraints") or [],
                        "cautions": first.get("cautions") or [],
                        "output_contract": first.get("output_contract") or [],
                        "examples": first.get("examples") or [],
                        "tags": first.get("metadata", {}).get("tags") or ["psychology", "intake"],
                        "confidence": 0.9,
                        "risk_class": first.get("risk_class") or "medium",
                        "support_ids": support_ids,
                        "source_draft_ids": [draft.get("draft_id") for draft in drafts],
                    }
                ]
            },
            ensure_ascii=False,
        )
    if mode == "document_version":
        payload = json.loads(user)
        candidate = payload.get("candidate_skill") or {}
        existing = list(payload.get("existing_skills") or [])
        if not existing:
            return json.dumps({"action": "create", "target_skill_ids": [], "reason": "new skill"}, ensure_ascii=False)
        target = existing[0]
        action = "strengthen"
        candidate_steps = list(candidate.get("workflow_steps") or [])
        target_steps = list(target.get("workflow_steps") or [])
        if len(candidate_steps) > len(target_steps):
            action = "revise"
        return json.dumps(
            {
                "action": action,
                "target_skill_ids": [target.get("skill_id")],
                "reason": action,
                "resolved_skill": candidate,
            },
            ensure_ascii=False,
        )
    if mode == "document_conflict":
        return json.dumps({"action": "keep", "reason": "no conflict review needed"}, ensure_ascii=False)
    return json.dumps({"skills": []}, ensure_ascii=False)


class DocumentPipelineTest(unittest.TestCase):
    def _build_sdk(self, *, store_path: str) -> AutoSkill:
        return AutoSkill(
            AutoSkillConfig(
                llm={"provider": "mock", "response": _document_llm_response},
                embeddings={"provider": "hashing", "dims": 64},
                store={"provider": "local", "path": store_path},
                maintenance_strategy="heuristic",
            )
        )

    def test_full_build_persists_registry_and_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            logs: list[str] = []
            pipeline = build_default_document_pipeline(sdk=sdk, logger=logs.append)

            result = pipeline.build(
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
            )

            self.assertEqual(len(result.ingest.documents), 1)
            self.assertGreater(len(result.extracted.support_records), 0)
            self.assertGreater(len(result.extracted.skill_drafts), 0)
            self.assertGreater(len(result.compiled.skill_specs), 0)
            self.assertGreater(len(result.registration.lifecycles), 0)
            self.assertGreaterEqual(len(result.registration.upserted_store_skills), 1)
            self.assertEqual(pipeline.registry.manifest()["entities"]["documents"]["count"], 1)
            self.assertGreaterEqual(pipeline.registry.manifest()["entities"]["supports"]["count"], 1)
            self.assertGreaterEqual(pipeline.registry.manifest()["entities"]["skills"]["count"], 1)
            stored_skills = sdk.store.list(user_id="u1")
            self.assertGreaterEqual(len(stored_skills), 1)
            self.assertIn("## Applicable Signals", stored_skills[0].instructions)
            self.assertIn("## Example Therapist Responses", stored_skills[0].instructions)
            self.assertGreaterEqual(len(stored_skills[0].examples), 1)
            self.assertTrue(os.path.isdir(result.intermediate.get("run_dir", "")))
            self.assertTrue(os.path.isfile(os.path.join(result.intermediate["run_dir"], "ingest", "result.json")))
            self.assertTrue(os.path.isfile(os.path.join(result.intermediate["run_dir"], "extract", "result.json")))
            self.assertTrue(os.path.isfile(os.path.join(result.intermediate["run_dir"], "compile", "result.json")))
            self.assertTrue(os.path.isfile(os.path.join(result.intermediate["run_dir"], "register", "result.json")))
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        result.intermediate["run_dir"],
                        "extract",
                        "documents",
                        f"{result.ingest.documents[0].doc_id}.json",
                    )
                )
            )
            self.assertTrue(any("[ingest_document]" in line for line in logs))
            self.assertTrue(any("[extract_skills]" in line for line in logs))
            self.assertTrue(any("[compile_skills]" in line for line in logs))

    def test_incremental_build_skips_unchanged_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)

            first = pipeline.build(
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
            )
            second = pipeline.build(
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
            )

            self.assertEqual(len(first.ingest.documents), 1)
            self.assertEqual(len(second.ingest.documents), 0)
            self.assertEqual(len(second.ingest.skipped_documents), 1)
            self.assertEqual(len(second.registration.skill_specs), 0)

    def test_dry_run_does_not_persist_registry_or_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)

            result = pipeline.build(
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
                dry_run=True,
            )

            manifest = pipeline.registry.manifest()
            self.assertTrue(result.dry_run)
            self.assertGreaterEqual(len(result.registration.lifecycles), 0)
            self.assertEqual(manifest["entities"]["documents"]["count"], 0)
            self.assertEqual(manifest["entities"]["skills"]["count"], 0)
            self.assertEqual(len(sdk.store.list(user_id="u1")), 0)
            self.assertEqual(result.intermediate, {})
            self.assertFalse(os.path.isdir(intermediate_runs_root(tmpdir)))

    def test_full_build_writes_visible_parent_child_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)

            result = pipeline.build(
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={
                    "channel": "offline_extract_from_doc",
                    "family_name": "认知行为疗法",
                    "profile_id": "test_therapy_v2",
                    "taxonomy_axis": "疗法",
                },
            )

            parent_md = os.path.join(tmpdir, "认知行为疗法", "总技能", "SKILL.md")
            child_root = os.path.join(tmpdir, "认知行为疗法", "子技能")
            self.assertTrue(os.path.isfile(parent_md))
            self.assertTrue(os.path.isdir(child_root))
            self.assertTrue(result.registration.visible_tree.get("parent_paths"))
            self.assertTrue(result.registration.visible_tree.get("child_paths"))
            self.assertGreaterEqual(len(list(result.registration.staging_runs or [])), 1)

    def test_extract_from_doc_returns_stage_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)

            result = extract_from_doc(
                sdk=sdk,
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
                dry_run=True,
            )

            self.assertEqual(result["total_documents"], 1)
            self.assertGreaterEqual(result["total_windows"], 1)
            self.assertGreater(result["total_support_records"], 0)
            self.assertGreater(result["total_skill_drafts"], 0)
            self.assertGreater(result["total_skill_specs"], 0)
            self.assertEqual(result["upserted_count"], 0)
            self.assertTrue(result["dry_run"])
            self.assertEqual(result["skills"][0]["asset_type"], "session_skill")
            self.assertEqual(result["skills"][0]["granularity"], "session")
            self.assertEqual(result["intermediate"], {})

    def test_extract_from_doc_uses_internal_default_user_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)

            result = extract_from_doc(
                sdk=sdk,
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
                dry_run=False,
            )

            self.assertEqual(result["total_documents"], 1)
            self.assertGreaterEqual(len(sdk.store.list(user_id="u1")), 1)

    def test_extract_from_doc_derives_profile_and_axis_from_taxonomy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)

            result = extract_from_doc(
                sdk=sdk,
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                domain_type="psychology",
                family_name="认知行为疗法",
                dry_run=False,
            )

            self.assertEqual(result["visible_tree"]["affected_families"], ["认知行为疗法"])
            manifest_path = os.path.join(tmpdir, ".runtime", "library_manifest.json")
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            self.assertEqual(manifest.get("active_family_name"), "认知行为疗法")
            self.assertEqual(manifest.get("active_profile_id"), "psychology::认知行为疗法")

    def test_document_build_result_dict_includes_windows_and_compiled_supports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)

            result = pipeline.build(
                user_id="u1",
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
                dry_run=True,
            )
            payload = result.to_dict()

            self.assertGreaterEqual(payload["windows"], 1)
            self.assertEqual(payload["support_records"], len(result.compiled.support_records))
            self.assertEqual(payload["skill_specs"], len(result.compiled.skill_specs))
            self.assertIn("staging_runs", payload)

    def test_document_prompt_requires_multi_asset_single_goal_extraction(self) -> None:
        prompt = build_offline_extract_prompt(channel=OFFLINE_CHANNEL_DOC, max_candidates=3)

        self.assertIn("One document may produce zero, one, or MANY assets", prompt)
        self.assertIn("single-goal", prompt)
        self.assertIn("asset_type (macro_protocol|session_skill|micro_skill|safety_rule|knowledge_reference)", prompt)
        self.assertIn("never merge macro and micro assets", prompt)
        self.assertIn("micro_skill means one therapist move", prompt)
        self.assertIn("examples", prompt)

    def test_identity_key_distinguishes_macro_and_micro_assets(self) -> None:
        macro = _identity_key_for_skill(
            asset_type="macro_protocol",
            granularity="macro",
            objective="Run a full intake protocol.",
            domain="psychology",
            task_family="assessment",
            method_family="cbt",
            stage="intake",
            name="intake protocol",
        )
        micro = _identity_key_for_skill(
            asset_type="micro_skill",
            granularity="micro",
            objective="Deliver one empathic reflection.",
            domain="psychology",
            task_family="assessment",
            method_family="cbt",
            stage="intake",
            name="intake protocol",
        )

        self.assertNotEqual(macro, micro)

    def test_short_section_is_used_as_default_extraction_unit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)
            text = """
# Intake
Build rapport before deeper intervention.

Clarify the client's immediate concern and summarize the goal for this session.
""".strip()

            ingest_result = pipeline.ingest_document(
                data=text,
                title="Short Intake Section",
                domain="psychology",
                dry_run=True,
            )
            extracted = pipeline.extract_skills(documents=ingest_result.documents)

            self.assertEqual(len(ingest_result.documents), 1)
            self.assertEqual(len(extracted.support_records), 1)
            self.assertEqual(extracted.support_records[0].metadata.get("extraction_unit"), "section")

    def test_pipeline_extract_uses_ingest_windows_when_provided(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)
            text = """
# Intake
Build rapport before deeper intervention.

Clarify the client's immediate concern and summarize the goal for this session.
""".strip()

            ingest_result = pipeline.ingest_document(
                data=text,
                title="Window Driven Intake",
                domain="psychology",
                dry_run=True,
            )
            extracted = pipeline.extract_skills(
                documents=ingest_result.documents,
                windows=ingest_result.windows,
            )

            self.assertEqual(len(ingest_result.windows), 1)
            self.assertEqual(len(extracted.support_records), 1)
            self.assertEqual(extracted.support_records[0].metadata.get("extraction_unit"), "window")
            self.assertEqual(
                extracted.support_records[0].metadata.get("window_strategy"),
                ingest_result.windows[0].strategy,
            )
            self.assertEqual(
                extracted.skill_drafts[0].metadata.get("window_id"),
                ingest_result.windows[0].window_id,
            )

    def test_long_section_falls_back_to_multiple_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)
            text = """
# Intake
Build rapport before deeper intervention.

Clarify the client's immediate concern and summarize the goal for this session.

Always assess acute risk before intensive exploration.

Do not push interpretation before the client is ready.
""".strip()

            ingest_result = pipeline.ingest_document(
                data=text,
                title="Long Intake Section",
                domain="psychology",
                dry_run=True,
            )
            extracted = extract_skills(
                documents=ingest_result.documents,
                extractor=build_document_skill_extractor(
                    "llm",
                    llm_config={"provider": "mock", "response": _document_llm_response},
                    max_section_chars=120,
                    overlap_chars=20,
                ),
            )

            self.assertGreater(len(extracted.support_records), 1)
            self.assertTrue(
                any(record.metadata.get("extraction_unit") == "chunk" for record in extracted.support_records)
            )

    def test_budgeted_extraction_prioritizes_relevant_sections(self) -> None:
        def _budget_response(*, system: str | None, user: str, temperature: float = 0.0, mode: str = "default") -> str:
            _ = system, temperature
            if mode != "document_extract":
                return json.dumps({"skills": []}, ensure_ascii=False)
            payload = json.loads(user)
            excerpt = str(payload.get("excerpt") or "").strip().lower()
            if "scaling question" not in excerpt:
                return json.dumps({"skills": []}, ensure_ascii=False)
            document = payload.get("document") or {}
            return json.dumps(
                {
                    "skills": [
                        {
                            "name": "Scaling question intervention",
                            "description": "Use a scaling question intervention.",
                            "prompt": (
                                "# Role & Objective\n"
                                "Use a scaling question.\n\n"
                                "# Rules & Constraints\n"
                                "- Keep the intervention concise.\n\n"
                                "# Core Workflow\n"
                                "1. Ask the scaling question.\n\n"
                                "# Output Format\n"
                                "- Return the next-step summary."
                            ),
                            "asset_type": "micro_skill",
                            "granularity": "micro",
                            "objective": "Deliver a single scaling-question intervention move.",
                            "domain": document.get("domain") or "psychology",
                            "task_family": "goal_setting",
                            "method_family": "solution_focused",
                            "stage": "intervention",
                            "applicable_signals": ["When progress needs to be scaled concretely."],
                            "intervention_moves": ["Ask the scaling question."],
                            "contraindications": [],
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

        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)

            text = """
# Demographics
This section only describes age, school, and family facts.

# Growth History
This section only narrates background experiences.

# Session Intervention
Use a scaling question to help the client rate progress and define the next step.
""".strip()

            ingest_result = pipeline.ingest_document(
                data=text,
                title="Budgeted Section Priority",
                domain="psychology",
                dry_run=True,
            )
            extracted = extract_skills(
                documents=ingest_result.documents,
                extractor=build_document_skill_extractor(
                    "llm",
                    llm_config={"provider": "mock", "response": _budget_response},
                    max_units_per_document=1,
                ),
            )

            self.assertEqual(len(extracted.skill_drafts), 1)
            self.assertEqual(extracted.support_records[0].section, "Session Intervention")
            self.assertEqual(extracted.skill_drafts[0].stage, "intervention")
            self.assertEqual(extracted.skill_drafts[0].asset_type, "micro_skill")

    def test_compile_stage_keeps_support_content_outside_skill_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)

            ingest_result = pipeline.ingest_document(
                data=_DOC_TEXT,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
                dry_run=True,
            )
            extracted_result = pipeline.extract_skills(documents=ingest_result.documents)
            compiled_result = pipeline.compile_skills(
                skill_drafts=extracted_result.skill_drafts,
                support_records=extracted_result.support_records,
            )

            spec = compiled_result.skill_specs[0]
            support = next(
                (item for item in compiled_result.support_records if item.support_id in spec.support_ids),
                None,
            )

            self.assertIsNotNone(support)
            assert support is not None
            self.assertIn(support.support_id, spec.support_ids)
            self.assertNotIn(support.support_id, spec.skill_body)
            self.assertNotIn(support.excerpt, spec.metadata.get("identity_key", ""))

    def test_compile_groups_distinct_drafts_from_same_document_separately(self) -> None:
        def _compile_response(*, system: str | None, user: str, temperature: float = 0.0, mode: str = "default") -> str:
            _ = system, temperature
            if mode != "document_compile":
                return json.dumps({"skills": []}, ensure_ascii=False)
            payload = json.loads(user)
            drafts = list(payload.get("drafts") or [])
            first = drafts[0]
            return json.dumps(
                {
                    "skills": [
                        {
                            "name": first.get("name") or "skill",
                            "description": first.get("description") or "desc",
                            "prompt": first.get("metadata", {}).get("prompt") or "# Goal\nPrompt",
                            "asset_type": first.get("asset_type") or "session_skill",
                            "granularity": first.get("granularity") or "session",
                            "objective": first.get("objective") or first.get("description") or "objective",
                            "domain": first.get("domain") or "psychology",
                            "task_family": first.get("task_family") or "intake",
                            "method_family": first.get("method_family") or "structured_interview",
                            "stage": first.get("stage") or "intake",
                            "workflow_steps": first.get("workflow_steps") or [],
                            "constraints": first.get("constraints") or [],
                            "cautions": first.get("cautions") or [],
                            "output_contract": first.get("output_contract") or [],
                            "support_ids": first.get("support_ids") or [],
                            "source_draft_ids": [first.get("draft_id")],
                            "confidence": 0.9,
                            "risk_class": "low",
                        }
                    ]
                },
                ensure_ascii=False,
            )

        support_a = SupportRecord(
            support_id="sup-a",
            doc_id="doc-1",
            source_file="/tmp/doc-1.md",
            section="Session 1",
            span=TextSpan(start=0, end=20),
            excerpt="Build rapport first.",
            relation_type=SupportRelation.SUPPORT,
            confidence=0.9,
        )
        support_b = SupportRecord(
            support_id="sup-b",
            doc_id="doc-1",
            source_file="/tmp/doc-1.md",
            section="Session 2",
            span=TextSpan(start=21, end=45),
            excerpt="Review homework next.",
            relation_type=SupportRelation.SUPPORT,
            confidence=0.9,
        )
        draft_a = SkillDraft(
            draft_id="draft-a",
            doc_id="doc-1",
            name="rapport building / intake",
            description="Build rapport before deeper intervention.",
            asset_type="session_skill",
            granularity="session",
            objective="Establish rapport before deeper intervention.",
            domain="psychology",
            task_family="intake",
            method_family="structured_interview",
            stage="intake",
            workflow_steps=["Build rapport first."],
            constraints=["Do not rush disclosure."],
            support_ids=["sup-a"],
            metadata={"prompt": "# Goal\nBuild rapport."},
        )
        draft_b = SkillDraft(
            draft_id="draft-b",
            doc_id="doc-1",
            name="homework review / session opening",
            description="Review homework before setting the agenda.",
            asset_type="session_skill",
            granularity="session",
            objective="Review homework before setting the agenda.",
            domain="psychology",
            task_family="homework_review",
            method_family="structured_interview",
            stage="follow_up",
            workflow_steps=["Review homework first."],
            constraints=["Check barriers before assigning more work."],
            support_ids=["sup-b"],
            metadata={"prompt": "# Goal\nReview homework."},
        )

        compiled = compile_skills(
            skill_drafts=[draft_a, draft_b],
            support_records=[support_a, support_b],
            compiler=build_skill_compiler(
                "llm",
                llm_config={"provider": "mock", "response": _compile_response},
            ),
            target_state=VersionState.DRAFT,
        )

        self.assertEqual(len(compiled.skill_specs), 2)
        self.assertEqual(
            {spec.name for spec in compiled.skill_specs},
            {"rapport building / intake", "homework review / session opening"},
        )

    def test_changed_document_bumps_registry_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = self._build_sdk(store_path=tmpdir)
            pipeline = build_default_document_pipeline(sdk=sdk)
            initial_text = """
# Intake
1. Build rapport before deeper intervention.

# Constraints
Do not push interpretation before the client is ready.
""".strip()
            revised_text = """
# Intake
1. Build rapport before deeper intervention.

# Constraints
Do not push interpretation before the client is ready.
Always check for acute risk before intensive exploration.
""".strip()

            first = pipeline.build(
                user_id="u1",
                data=initial_text,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
            )
            second = pipeline.build(
                user_id="u1",
                data=revised_text,
                title="Intake Workflow",
                domain="psychology",
                metadata={"channel": "offline_extract_from_doc"},
            )

            first_versions = {spec.skill_id: spec.version for spec in list(first.registration.skill_specs or [])}
            shared_skills = [
                spec for spec in list(second.registration.skill_specs or []) if spec.skill_id in first_versions
            ]

            self.assertTrue(shared_skills)
            self.assertTrue(any(spec.version != first_versions[spec.skill_id] for spec in shared_skills))
            self.assertTrue(any(spec.version == "0.1.1" for spec in shared_skills))
            self.assertTrue(any(event.reason in {"revise", "strengthen", "merge"} for event in second.registration.lifecycles))


if __name__ == "__main__":
    unittest.main()
