from __future__ import annotations

import json
import os
import tempfile
import unittest

from autoskill.llm.mock import MockLLM
from autoskill.offline.document.models import (
    DocumentRecord,
    SkillSpec,
    SupportRecord,
    SupportRelation,
    TextSpan,
    VersionState,
)
from autoskill.offline.document.registry import DocumentRegistry
from autoskill.offline.document.versioning import register_versions


def _version_llm_response(*, system: str | None, user: str, temperature: float = 0.0, mode: str = "default") -> str:
    _ = system, temperature
    if mode == "document_version":
        payload = json.loads(user)
        candidate = payload.get("candidate_skill") or {}
        existing = list(payload.get("existing_skills") or [])
        peers = list(payload.get("peer_candidates") or [])
        if not existing:
            return json.dumps({"action": "create", "target_skill_ids": [], "reason": "create"}, ensure_ascii=False)

        same_name = [
            skill for skill in existing
            if str(skill.get("name") or "").strip().lower() == str(candidate.get("name") or "").strip().lower()
        ]
        broad_parent = next(
            (
                skill for skill in existing
                if str(skill.get("name") or "").strip().lower() == "intake workflow"
                and len(list(skill.get("workflow_steps") or [])) >= 3
                and peers
            ),
            None,
        )
        if broad_parent is not None:
            return json.dumps(
                {
                    "action": "split",
                    "target_skill_ids": [broad_parent.get("skill_id")],
                    "reason": "split",
                    "resolved_skill": candidate,
                },
                ensure_ascii=False,
            )
        if len(same_name) >= 2:
            return json.dumps(
                {
                    "action": "merge",
                    "target_skill_ids": [skill.get("skill_id") for skill in same_name],
                    "reason": "merge",
                    "resolved_skill": candidate,
                },
                ensure_ascii=False,
            )
        target = same_name[0] if same_name else existing[0]
        candidate_steps = list(candidate.get("workflow_steps") or [])
        target_steps = list(target.get("workflow_steps") or [])
        candidate_constraints = list(candidate.get("constraints") or [])
        target_constraints = list(target.get("constraints") or [])
        has_conflict_support = any(
            item.get("relation_type") == "conflict"
            for item in list(candidate.get("support_excerpt_summaries") or [])
        )
        if has_conflict_support:
            action = "create"
        elif candidate_steps == target_steps and candidate_constraints == target_constraints:
            action = "strengthen"
        elif candidate.get("task_family") == target.get("task_family") and candidate.get("stage") == target.get("stage"):
            action = "revise"
        else:
            action = "create"
        target_ids = [target.get("skill_id")] if action != "create" else []
        return json.dumps(
            {
                "action": action,
                "target_skill_ids": target_ids,
                "reason": action,
                "resolved_skill": candidate,
            },
            ensure_ascii=False,
        )
    if mode == "document_conflict":
        payload = json.loads(user)
        incoming = list(payload.get("incoming_skills") or [])
        has_conflict = any(
            any(item.get("relation_type") == "conflict" for item in list(skill.get("support_excerpt_summaries") or []))
            for skill in incoming
        )
        if has_conflict:
            return json.dumps({"action": "deprecate", "reason": "deprecate"}, ensure_ascii=False)
        return json.dumps({"action": "keep", "reason": "keep"}, ensure_ascii=False)
    return json.dumps({"skills": []}, ensure_ascii=False)


class DocumentVersioningTest(unittest.TestCase):
    def _llm(self) -> MockLLM:
        return MockLLM(response=_version_llm_response)

    def _document(self, *, doc_id: str, title: str = "Doc") -> DocumentRecord:
        return DocumentRecord(
            doc_id=doc_id,
            source_type="markdown_document",
            title=title,
            raw_text="placeholder",
            content_hash=f"hash-{doc_id}",
            metadata={"source_file": f"/tmp/{doc_id}.md"},
        )

    def _support(
        self,
        *,
        support_id: str,
        doc_id: str,
        excerpt: str,
        relation_type: SupportRelation = SupportRelation.SUPPORT,
    ) -> SupportRecord:
        return SupportRecord(
            support_id=support_id,
            doc_id=doc_id,
            source_file=f"/tmp/{doc_id}.md",
            section="Method",
            span=TextSpan(start=0, end=len(excerpt)),
            excerpt=excerpt,
            relation_type=relation_type,
            confidence=0.85,
        )

    def _skill(
        self,
        *,
        skill_id: str,
        name: str,
        workflow_steps: list[str],
        support_ids: list[str],
        asset_type: str = "session_skill",
        granularity: str = "session",
        objective: str | None = None,
        domain: str = "psychology",
        task_family: str = "intake",
        method_family: str = "structured_interview",
        stage: str = "intake",
        constraints: list[str] | None = None,
        cautions: list[str] | None = None,
        intervention_moves: list[str] | None = None,
        version: str = "0.1.0",
        status: VersionState = VersionState.ACTIVE,
    ) -> SkillSpec:
        return SkillSpec(
            skill_id=skill_id,
            name=name,
            description=f"{name} description",
            skill_body="# Goal\nSkill body",
            asset_type=asset_type,
            granularity=granularity,
            objective=objective or f"{name} objective",
            domain=domain,
            task_family=task_family,
            method_family=method_family,
            stage=stage,
            intervention_moves=list(intervention_moves or []),
            workflow_steps=workflow_steps,
            constraints=list(constraints or []),
            cautions=list(cautions or []),
            support_ids=support_ids,
            version=version,
            status=status,
        )

    def _register(
        self,
        *,
        registry: DocumentRegistry,
        documents: list[DocumentRecord],
        supports: list[SupportRecord],
        skills: list[SkillSpec],
        dry_run: bool = False,
        target_state: VersionState = VersionState.ACTIVE,
    ):
        return register_versions(
            registry=registry,
            documents=documents,
            support_records=supports,
            skill_specs=skills,
            llm=self._llm(),
            user_id="u1",
            metadata={"channel": "offline_extract_from_doc"},
            dry_run=dry_run,
            target_state=target_state,
        )

    def test_create_new_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocumentRegistry(root_dir=os.path.join(tmpdir, "registry"))
            document = self._document(doc_id="doc-1")
            support = self._support(support_id="sup-1", doc_id=document.doc_id, excerpt="Build rapport first.")
            skill = self._skill(
                skill_id="cand-1",
                name="rapport building / intake",
                workflow_steps=["Build rapport first."],
                constraints=["Do not push interpretation too early."],
                support_ids=[support.support_id],
            )

            result = self._register(
                registry=registry,
                documents=[document],
                supports=[support],
                skills=[skill],
            )

            self.assertEqual(len(result.skill_specs), 1)
            self.assertEqual(result.skill_specs[0].version, "0.1.0")
            self.assertEqual(result.lifecycles[0].reason, "create")
            self.assertEqual(result.support_records[0].skill_id, result.skill_specs[0].skill_id)

    def test_same_skill_strengthens_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocumentRegistry(root_dir=os.path.join(tmpdir, "registry"))
            doc1 = self._document(doc_id="doc-1")
            sup1 = self._support(support_id="sup-1", doc_id=doc1.doc_id, excerpt="Build rapport first.")
            skill1 = self._skill(
                skill_id="cand-1",
                name="rapport building / intake",
                workflow_steps=["Build rapport first.", "Clarify the immediate concern."],
                constraints=["Do not push interpretation too early."],
                support_ids=[sup1.support_id],
            )
            first = self._register(registry=registry, documents=[doc1], supports=[sup1], skills=[skill1])
            existing_id = first.skill_specs[0].skill_id

            doc2 = self._document(doc_id="doc-2")
            sup2 = self._support(support_id="sup-2", doc_id=doc2.doc_id, excerpt="Clarify the immediate concern.")
            skill2 = self._skill(
                skill_id="cand-2",
                name="rapport building / intake",
                workflow_steps=["Build rapport first.", "Clarify the immediate concern."],
                constraints=["Do not push interpretation too early."],
                support_ids=[sup2.support_id],
            )
            second = self._register(registry=registry, documents=[doc2], supports=[sup2], skills=[skill2])

            self.assertEqual(len(second.skill_specs), 1)
            updated = second.skill_specs[0]
            self.assertEqual(updated.skill_id, existing_id)
            self.assertEqual(updated.version, "0.1.1")
            self.assertEqual(second.lifecycles[0].reason, "strengthen")
            self.assertEqual(second.support_records[0].skill_id, existing_id)

    def test_split_existing_skill_into_two_children(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocumentRegistry(root_dir=os.path.join(tmpdir, "registry"))
            parent_doc = self._document(doc_id="doc-parent")
            parent_support = self._support(
                support_id="sup-parent",
                doc_id=parent_doc.doc_id,
                excerpt="Build rapport, check acute risk, and set a session agenda.",
            )
            parent_skill = self._skill(
                skill_id="parent-skill",
                name="intake workflow",
                asset_type="macro_protocol",
                granularity="macro",
                objective="Run the full intake protocol.",
                workflow_steps=[
                    "Build rapport first.",
                    "Check acute risk.",
                    "Set a session agenda.",
                ],
                constraints=["Do not rush interpretation."],
                support_ids=[parent_support.support_id],
            )
            first = self._register(registry=registry, documents=[parent_doc], supports=[parent_support], skills=[parent_skill])
            existing_parent = first.skill_specs[0]

            doc_child = self._document(doc_id="doc-child")
            support_a = self._support(support_id="sup-a", doc_id=doc_child.doc_id, excerpt="Build rapport first.")
            support_b = self._support(support_id="sup-b", doc_id=doc_child.doc_id, excerpt="Check acute risk immediately.")
            child_a = self._skill(
                skill_id="child-a",
                name="rapport building / intake",
                asset_type="session_skill",
                granularity="session",
                objective="Establish rapport at the start of intake.",
                workflow_steps=["Build rapport first."],
                constraints=["Do not rush interpretation."],
                support_ids=[support_a.support_id],
            )
            child_b = self._skill(
                skill_id="child-b",
                name="intake workflow / risk screening",
                asset_type="session_skill",
                granularity="session",
                objective="Run the acute risk screening subflow during intake.",
                workflow_steps=["Check acute risk immediately."],
                constraints=["Do not rush interpretation."],
                support_ids=[support_b.support_id],
            )

            second = self._register(
                registry=registry,
                documents=[doc_child],
                supports=[support_a, support_b],
                skills=[child_a, child_b],
            )

            deprecated_parent = [skill for skill in second.skill_specs if skill.skill_id == existing_parent.skill_id and skill.status == VersionState.DEPRECATED]
            active_children = [skill for skill in second.skill_specs if skill.skill_id != existing_parent.skill_id]

            self.assertEqual(len(active_children), 2)
            self.assertTrue(deprecated_parent)
            self.assertTrue(any(event.reason == "split" for event in second.lifecycles))

    def test_merge_multiple_existing_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocumentRegistry(root_dir=os.path.join(tmpdir, "registry"))
            doc1 = self._document(doc_id="doc-1")
            sup1 = self._support(support_id="sup-1", doc_id=doc1.doc_id, excerpt="Build rapport and assess risk.")
            skill1 = self._skill(
                skill_id="skill-1",
                name="intake stabilization workflow",
                workflow_steps=["Build rapport first.", "Assess acute risk."],
                support_ids=[sup1.support_id],
            )
            registry.upsert_document(doc1)
            registry.upsert_support(self._support(support_id=sup1.support_id, doc_id=sup1.doc_id, excerpt=sup1.excerpt, relation_type=sup1.relation_type))
            registry.upsert_skill(skill1)

            doc2 = self._document(doc_id="doc-2")
            sup2 = self._support(support_id="sup-2", doc_id=doc2.doc_id, excerpt="Build rapport, assess risk, clarify concern.")
            skill2 = self._skill(
                skill_id="skill-2",
                name="intake stabilization workflow",
                workflow_steps=["Build rapport first.", "Assess acute risk.", "Clarify the immediate concern."],
                support_ids=[sup2.support_id],
            )
            registry.upsert_document(doc2)
            registry.upsert_support(self._support(support_id=sup2.support_id, doc_id=sup2.doc_id, excerpt=sup2.excerpt, relation_type=sup2.relation_type))
            registry.upsert_skill(skill2)

            doc3 = self._document(doc_id="doc-3")
            sup3 = self._support(support_id="sup-3", doc_id=doc3.doc_id, excerpt="Build rapport, assess risk, clarify concern.")
            merged_candidate = self._skill(
                skill_id="cand-merge",
                name="intake stabilization workflow",
                workflow_steps=["Build rapport first.", "Assess acute risk.", "Clarify the immediate concern."],
                support_ids=[sup3.support_id],
            )

            result = self._register(registry=registry, documents=[doc3], supports=[sup3], skills=[merged_candidate])

            self.assertTrue(any(log["action"] == "merge" for log in result.change_logs))
            self.assertTrue(any(skill.status == VersionState.DEPRECATED for skill in result.skill_specs))

    def test_conflicting_new_support_can_deprecate_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocumentRegistry(root_dir=os.path.join(tmpdir, "registry"))
            base_doc = self._document(doc_id="doc-base")
            base_support = self._support(
                support_id="sup-base",
                doc_id=base_doc.doc_id,
                excerpt="Challenge avoidance directly during crisis intake.",
            )
            base_skill = self._skill(
                skill_id="base-skill",
                name="direct challenge / crisis intake",
                workflow_steps=["Challenge avoidance directly.", "Push for cognitive restructuring."],
                constraints=["Keep the session moving quickly."],
                support_ids=[base_support.support_id],
                task_family="assessment",
                stage="crisis",
            )
            self._register(registry=registry, documents=[base_doc], supports=[base_support], skills=[base_skill])

            new_doc = self._document(doc_id="doc-new")
            conflict_support = self._support(
                support_id="sup-conflict",
                doc_id=new_doc.doc_id,
                excerpt="Do not challenge avoidance directly during acute crisis; stabilize first.",
                relation_type=SupportRelation.CONFLICT,
            )
            new_skill = self._skill(
                skill_id="cand-new",
                name="crisis stabilization / intake",
                workflow_steps=["Stabilize acute distress first.", "Avoid direct confrontation."],
                constraints=["Do not intensify affect before stabilization."],
                support_ids=[conflict_support.support_id],
                task_family="assessment",
                stage="crisis",
            )

            result = self._register(registry=registry, documents=[new_doc], supports=[conflict_support], skills=[new_skill])

            self.assertTrue(any(skill.status in {VersionState.WATCHLIST, VersionState.DEPRECATED} for skill in result.skill_specs))
            self.assertTrue(any(log["action"] == "deprecate" for log in result.change_logs))

    def test_cross_granularity_candidate_does_not_merge_into_existing_macro_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = DocumentRegistry(root_dir=os.path.join(tmpdir, "registry"))
            base_doc = self._document(doc_id="doc-base")
            base_support = self._support(
                support_id="sup-base",
                doc_id=base_doc.doc_id,
                excerpt="Build rapport, assess risk, and set a session agenda.",
            )
            macro_skill = self._skill(
                skill_id="base-macro",
                name="intake workflow",
                asset_type="macro_protocol",
                granularity="macro",
                objective="Run the full intake protocol.",
                workflow_steps=[
                    "Build rapport first.",
                    "Assess acute risk.",
                    "Set a session agenda.",
                ],
                support_ids=[base_support.support_id],
            )
            self._register(registry=registry, documents=[base_doc], supports=[base_support], skills=[macro_skill])

            new_doc = self._document(doc_id="doc-new")
            micro_support = self._support(
                support_id="sup-micro",
                doc_id=new_doc.doc_id,
                excerpt="Reflect the client's main feeling before asking the next question.",
            )
            micro_skill = self._skill(
                skill_id="cand-micro",
                name="intake workflow",
                asset_type="micro_skill",
                granularity="micro",
                objective="Deliver a single empathic reflection move.",
                workflow_steps=[],
                intervention_moves=["Reflect the client's main feeling before the next question."],
                support_ids=[micro_support.support_id],
            )

            result = self._register(registry=registry, documents=[new_doc], supports=[micro_support], skills=[micro_skill])

            active_created = [
                skill
                for skill in result.skill_specs
                if skill.status == VersionState.ACTIVE and skill.asset_type == "micro_skill"
            ]
            self.assertTrue(active_created)
            self.assertTrue(any(event.reason.startswith("create") for event in result.lifecycles))


if __name__ == "__main__":
    unittest.main()
