from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
import tempfile
import unittest

from autoskill.cli import main as autoskill_main
from autoskill.config import default_document_store_path
from autoskill.offline.document.extract import _build_sdk_from_args, build_parser, main


_DOC_TEXT = """
# Intake
1. Build rapport before deeper intervention.
2. Clarify the client's immediate concern.

# Constraints
Do not push interpretation before the client is ready.
""".strip()


class DocumentCliTest(unittest.TestCase):
    def _mock_response(self) -> str:
        return json.dumps(
            {
                "document_extract": {
                    "skills": [
                        {
                            "name": "document intake workflow",
                            "description": "Reusable workflow extracted from the document.",
                            "prompt": "# Role & Objective\nGuide the workflow.\n\n# Rules & Constraints\n- Keep the process safe.\n\n# Core Workflow\n1. Build rapport first.\n2. Clarify the immediate concern.\n\n# Output Format\n- Output a short summary.",
                            "domain": "psychology",
                            "task_family": "intake",
                            "method_family": "structured_interview",
                            "stage": "intake",
                            "workflow_steps": ["Build rapport first.", "Clarify the immediate concern."],
                            "constraints": ["Keep the process safe."],
                            "cautions": ["Avoid premature interpretation."],
                            "output_contract": ["Output a short summary."],
                            "relation_type": "support",
                            "risk_class": "medium",
                            "triggers": ["When starting intake"],
                            "tags": ["psychology", "intake"],
                            "confidence": 0.9,
                        }
                    ]
                },
                "document_compile": {
                    "skills": [
                        {
                            "name": "document intake workflow",
                            "description": "Reusable workflow extracted from the document.",
                            "prompt": "# Role & Objective\nGuide the workflow.\n\n# Rules & Constraints\n- Keep the process safe.\n\n# Core Workflow\n1. Build rapport first.\n2. Clarify the immediate concern.\n\n# Output Format\n- Output a short summary.",
                            "domain": "psychology",
                            "task_family": "intake",
                            "method_family": "structured_interview",
                            "stage": "intake",
                            "workflow_steps": ["Build rapport first.", "Clarify the immediate concern."],
                            "constraints": ["Keep the process safe."],
                            "cautions": ["Avoid premature interpretation."],
                            "output_contract": ["Output a short summary."],
                            "tags": ["psychology", "intake"],
                            "confidence": 0.9,
                            "risk_class": "medium",
                        }
                    ]
                },
                "document_version": {
                    "action": "create",
                    "target_skill_ids": [],
                    "reason": "create"
                }
            },
            ensure_ascii=False,
        )

    def _write_doc(self, *, root: str) -> str:
        path = os.path.join(root, "document.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(_DOC_TEXT)
        return path

    def _run_main_json(self, argv: list[str]) -> dict:
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(argv)
        text = buf.getvalue().strip()
        self.assertTrue(text)
        return json.loads(text)

    def _run_text(self, fn, argv: list[str]) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                fn(argv)
            except SystemExit as exc:
                if int(getattr(exc, "code", 0) or 0) not in {0}:
                    raise
        return buf.getvalue()

    def test_default_cli_invocation_routes_to_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = self._write_doc(root=tmpdir)
            payload = self._run_main_json(
                [
                    "--file",
                    doc_path,
                    "--dry-run",
                    "--quiet",
                    "--json",
                    "--llm-provider",
                    "mock",
                    "--llm-response",
                    self._mock_response(),
                    "--maintenance-strategy",
                    "llm",
                    "--store-path",
                    tmpdir,
                ]
            )

            self.assertEqual(payload["total_documents"], 1)
            self.assertGreater(payload["total_support_records"], 0)
            self.assertGreater(payload["total_skill_drafts"], 0)
            self.assertGreater(payload["total_skill_specs"], 0)

    def test_extract_command_returns_support_records_and_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = self._write_doc(root=tmpdir)
            payload = self._run_main_json(
                [
                    "extract",
                    "--file",
                    doc_path,
                    "--dry-run",
                    "--quiet",
                    "--json",
                    "--llm-provider",
                    "mock",
                    "--llm-response",
                    self._mock_response(),
                    "--maintenance-strategy",
                    "llm",
                    "--store-path",
                    tmpdir,
                ]
            )

            self.assertEqual(len(payload["documents"]), 1)
            self.assertGreater(len(payload["support_records"]), 0)
            self.assertGreater(len(payload["skill_drafts"]), 0)
            self.assertIn("relation_type", payload["support_records"][0])

    def test_compile_command_returns_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = self._write_doc(root=tmpdir)
            payload = self._run_main_json(
                [
                    "compile",
                    "--file",
                    doc_path,
                    "--dry-run",
                    "--quiet",
                    "--json",
                    "--llm-provider",
                    "mock",
                    "--llm-response",
                    self._mock_response(),
                    "--maintenance-strategy",
                    "llm",
                    "--store-path",
                    tmpdir,
                ]
            )

            self.assertEqual(len(payload["documents"]), 1)
            self.assertGreater(len(payload["support_records"]), 0)
            self.assertGreater(len(payload["skill_drafts"]), 0)
            self.assertGreater(len(payload["skills"]), 0)

    def test_top_level_cli_routes_to_document_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = self._write_doc(root=tmpdir)
            buf = io.StringIO()
            with redirect_stdout(buf):
                autoskill_main(
                    [
                        "offline",
                        "document",
                        "compile",
                        "--file",
                        doc_path,
                        "--dry-run",
                        "--quiet",
                        "--json",
                        "--llm-provider",
                        "mock",
                        "--llm-response",
                        self._mock_response(),
                        "--maintenance-strategy",
                        "llm",
                        "--store-path",
                        tmpdir,
                    ]
                )
            payload = json.loads(buf.getvalue().strip())

            self.assertEqual(len(payload["documents"]), 1)
            self.assertGreater(len(payload["support_records"]), 0)
            self.assertGreater(len(payload["skill_drafts"]), 0)
            self.assertGreater(len(payload["skills"]), 0)

    def test_top_level_document_help_shows_document_subcommands(self) -> None:
        output = self._run_text(autoskill_main, ["offline", "document", "-h"])

        self.assertIn("build", output)
        self.assertIn("ingest", output)
        self.assertIn("extract", output)
        self.assertIn("compile", output)

    def test_build_help_includes_examples_and_registry_help(self) -> None:
        output = self._run_text(main, ["build", "-h"])

        self.assertIn("Examples:", output)
        self.assertIn("--registry-root", output)
        self.assertIn("document registry root", output)

    def test_document_cli_defaults_store_path_to_docskill(self) -> None:
        args = build_parser().parse_args(["build", "--file", "/tmp/paper.md"])
        sdk = _build_sdk_from_args(args)

        self.assertEqual(sdk.config.store.get("path"), default_document_store_path())


if __name__ == "__main__":
    unittest.main()
