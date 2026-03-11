from __future__ import annotations

import json
import unittest

from autoskill.models import SkillExample
from autoskill.offline.document.models import (
    DocumentRecord,
    DocumentSection,
    SkillDraft,
    SkillLifecycle,
    SkillSpec,
    SupportRecord,
    SupportRelation,
    TextSpan,
    VersionState,
)


class DocumentModelsTest(unittest.TestCase):
    def test_round_trip_serialization(self) -> None:
        document = DocumentRecord(
            doc_id="doc-1",
            source_type="markdown_document",
            title="Intake workflow",
            authors=["A. Author"],
            year=2025,
            domain="psychology",
            raw_text="# Intake\nBuild rapport first.",
            sections=[
                DocumentSection(
                    heading="Intake",
                    text="Build rapport first.",
                    level=1,
                    span=TextSpan(start=0, end=18),
                )
            ],
            metadata={"source_file": "/tmp/intake.md"},
            content_hash="hash-1",
        )
        support = SupportRecord(
            support_id="sup-1",
            doc_id=document.doc_id,
            source_file="/tmp/intake.md",
            section="Intake",
            span=TextSpan(start=0, end=18),
            excerpt="Build rapport first.",
            relation_type=SupportRelation.SUPPORT,
            confidence=0.8,
            metadata={"task_family": "questioning"},
        )
        draft = SkillDraft(
            draft_id="draft-1",
            doc_id=document.doc_id,
            name="rapport building / intake",
            description="Build rapport before deeper intervention.",
            asset_type="session_skill",
            granularity="session",
            objective="Establish rapport before deeper intervention.",
            domain="psychology",
            task_family="questioning",
            method_family="structured_interview",
            stage="intake",
            applicable_signals=["When the client is entering a first session."],
            contraindications=["Do not force disclosure during acute crisis."],
            intervention_moves=["Reflect the client's initial concern."],
            workflow_steps=["Build rapport first."],
            constraints=["Do not escalate prematurely."],
            examples=[
                SkillExample(
                    input="Client is quiet and guarded in the first session.",
                    output="Acknowledge the difficulty of opening up and invite the client to start anywhere that feels manageable.",
                    notes="Keep the pace slow.",
                )
            ],
            support_ids=[support.support_id],
            confidence=0.85,
        )
        skill = SkillSpec(
            skill_id="skill-1",
            name="rapport building / intake",
            description="Build rapport before deeper intervention.",
            skill_body="# Goal\nBuild rapport.",
            asset_type="session_skill",
            granularity="session",
            objective="Establish rapport before deeper intervention.",
            domain="psychology",
            task_family="questioning",
            method_family="structured_interview",
            stage="intake",
            applicable_signals=["When the client is entering a first session."],
            contraindications=["Do not force disclosure during acute crisis."],
            intervention_moves=["Reflect the client's initial concern."],
            workflow_steps=["Build rapport first."],
            constraints=["Do not escalate prematurely."],
            examples=[
                SkillExample(
                    input="Client is quiet and guarded in the first session.",
                    output="Acknowledge the difficulty of opening up and invite the client to start anywhere that feels manageable.",
                    notes="Keep the pace slow.",
                )
            ],
            support_ids=[support.support_id],
            version="0.1.0",
            status=VersionState.ACTIVE,
        )
        lifecycle = SkillLifecycle(
            lifecycle_id="life-1",
            skill_id=skill.skill_id,
            from_state=VersionState.DRAFT,
            to_state=VersionState.ACTIVE,
            reason="promote",
        )

        document2 = DocumentRecord.from_dict(json.loads(document.to_json()))
        support2 = SupportRecord.from_dict(json.loads(support.to_json()))
        draft2 = SkillDraft.from_dict(json.loads(draft.to_json()))
        skill2 = SkillSpec.from_dict(json.loads(skill.to_json()))
        lifecycle2 = SkillLifecycle.from_dict(json.loads(lifecycle.to_json()))

        self.assertEqual(document2.content_hash, document.content_hash)
        self.assertEqual(support2.relation_type, SupportRelation.SUPPORT)
        self.assertEqual(draft2.support_ids, [support.support_id])
        self.assertEqual(draft2.asset_type, "session_skill")
        self.assertEqual(draft2.granularity, "session")
        self.assertEqual(draft2.objective, "Establish rapport before deeper intervention.")
        self.assertEqual(draft2.intervention_moves, ["Reflect the client's initial concern."])
        self.assertEqual(len(draft2.examples), 1)
        self.assertEqual(skill2.status, VersionState.ACTIVE)
        self.assertEqual(skill2.applicable_signals, ["When the client is entering a first session."])
        self.assertEqual(len(skill2.examples), 1)
        self.assertEqual(lifecycle2.to_state, VersionState.ACTIVE)
        self.assertIn("title: Intake workflow", document.to_yaml())
        self.assertIn("relation_type: support", support.to_yaml())

    def test_validation_errors(self) -> None:
        with self.assertRaises(ValueError):
            SupportRecord(
                support_id="",
                doc_id="doc-1",
                source_file="/tmp/a.md",
                excerpt="x",
            )
        with self.assertRaises(ValueError):
            SkillDraft(
                draft_id="draft-1",
                doc_id="doc-1",
                name="",
                description="desc",
                workflow_steps=["step"],
                support_ids=["sup-1"],
            )
        with self.assertRaises(ValueError):
            SkillSpec(
                skill_id="skill-1",
                name="skill",
                description="desc",
                skill_body="",
                workflow_steps=["step"],
                support_ids=["sup-1"],
            )
        with self.assertRaises(ValueError):
            SkillLifecycle(
                lifecycle_id="life-1",
                skill_id="skill-1",
                from_state=VersionState.ACTIVE,
                to_state=VersionState.ACTIVE,
            )

    def test_intervention_only_micro_skill_is_valid(self) -> None:
        draft = SkillDraft(
            draft_id="draft-micro",
            doc_id="doc-1",
            name="emotion reflection move",
            description="Reflect the client's emotion without interpretation.",
            asset_type="micro_skill",
            granularity="micro",
            objective="Deliver a single emotion reflection move.",
            intervention_moves=["Name and reflect the client's core feeling in plain language."],
            support_ids=["sup-1"],
        )
        skill = SkillSpec(
            skill_id="skill-micro",
            name="emotion reflection move",
            description="Reflect the client's emotion without interpretation.",
            skill_body="# Goal\nReflect emotion.",
            asset_type="micro_skill",
            granularity="micro",
            objective="Deliver a single emotion reflection move.",
            intervention_moves=["Name and reflect the client's core feeling in plain language."],
            support_ids=["sup-1"],
        )

        self.assertEqual(draft.asset_type, "micro_skill")
        self.assertEqual(draft.granularity, "micro")
        self.assertEqual(skill.intervention_moves, ["Name and reflect the client's core feeling in plain language."])

    def test_bundle_and_safety_shapes_are_corrected(self) -> None:
        bundle = SkillSpec(
            skill_id="skill-bundle",
            name="基础助人技术组合包（关系建立期）",
            description="包含多个关系建立动作的组合包。",
            skill_body="在关系建立阶段使用开放式提问、非言语专注、情感反映与延迟回应。",
            asset_type="micro_skill",
            granularity="micro",
            objective="建立治疗联盟",
            task_family="rapport_building",
            method_family="person_centered",
            stage="intake",
            intervention_moves=["开放式提问", "非言语专注", "情感反映", "延迟回应", "去病理化语言"],
            workflow_steps=["开启话题", "反馈情绪", "等待继续", "避免建议"],
            support_ids=["sup-1"],
        )
        safety = SkillSpec(
            skill_id="skill-safety",
            name="高危个案不自杀承诺协商协议",
            description="高危危机阶段的安全承诺。",
            skill_body="确认风险等级后，明确承诺与求助路径。",
            asset_type="micro_skill",
            granularity="micro",
            objective="降低即刻风险",
            task_family="de_escalation",
            method_family="collaborative_agreement",
            stage="crisis",
            intervention_moves=["明确承诺语句", "口头复述", "同步支持资源"],
            workflow_steps=["确认风险等级", "解释承诺目的", "制定求助动作"],
            support_ids=["sup-2"],
            metadata={"risk_class": "high"},
        )

        self.assertEqual(bundle.asset_type, "session_skill")
        self.assertEqual(bundle.granularity, "session")
        self.assertEqual(safety.asset_type, "safety_rule")


if __name__ == "__main__":
    unittest.main()
