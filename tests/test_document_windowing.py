from __future__ import annotations

import json
import unittest

from autoskill.llm.base import LLM
from AutoSkill4Doc.document.windowing import build_windows_for_record
from AutoSkill4Doc.ingest import HeuristicDocumentIngestor, ingest_document, parse_sections_from_text
from AutoSkill4Doc.models import DocumentRecord, DocumentSection, TextSpan


class _OutlineMockLLM(LLM):
    def complete(self, *, system: str | None, user: str, temperature: float = 0.0) -> str:
        _ = system, temperature
        payload = json.loads(user)
        if "candidates" in payload:
            return json.dumps(
                {
                    "headings": [
                        {"candidate_index": 0, "level": 1},
                        {"candidate_index": 1, "level": 2},
                        {"candidate_index": 2, "level": 2},
                    ]
                },
                ensure_ascii=False,
            )
        return json.dumps({"skills": []}, ensure_ascii=False)


class DocumentWindowingTest(unittest.TestCase):
    def test_recommended_ingest_filters_noise_sections_and_builds_strict_windows(self) -> None:
        result = ingest_document(
            data="""
# 摘要
这是一段摘要说明，不应进入主窗口。

# 第2阶段目标
阶段目标是识别自动思维并建立本次会谈目标。

认知重构用于检验自动思维中的证据。

使用思维记录表整理支持证据和替代解释。

安排家庭作业，在会谈后继续练习。
""".strip(),
            title="CBT Stage Window",
            domain="psychology",
            dry_run=True,
        )

        self.assertEqual(len(result.text_units), 1)
        self.assertEqual(len(result.documents), 1)
        self.assertEqual(len(result.windows), 1)
        window = result.windows[0]
        self.assertEqual(window.strategy, "strict")
        self.assertNotEqual(window.section_heading, "摘要")
        self.assertIn("认知重构", window.text)
        self.assertIn("家庭作业", window.text)

    def test_dialogue_heavy_excerpt_is_dropped_from_main_windows(self) -> None:
        result = ingest_document(
            data="""
# 对话摘录
咨询师：你现在最担心什么？
来访者：我一直睡不好。
咨询师：最近有没有伤害自己的想法？

# 风险评估
先评估当前自伤风险和他伤风险。

再确认安全计划与紧急联系人。

记录转介与后续跟进要求。
""".strip(),
            title="Risk Intake",
            domain="psychology",
            dry_run=True,
        )

        self.assertEqual(len(result.windows), 1)
        window = result.windows[0]
        self.assertEqual(window.section_heading, "风险评估")
        self.assertNotIn("咨询师：", window.text)
        self.assertIn("安全计划", window.text)

    def test_process_like_section_without_explicit_anchor_falls_back_to_local_window(self) -> None:
        result = ingest_document(
            data="""
# 干预流程
1. 先明确当前目标。
2. 再做现实检验。
3. 记录替代想法。
4. 布置练习与回顾方式。
""".strip(),
            title="Process Fallback",
            domain="psychology",
            dry_run=True,
        )

        self.assertEqual(len(result.windows), 1)
        window = result.windows[0]
        self.assertEqual(window.paragraph_start, 0)
        self.assertEqual(window.paragraph_end, 0)
        self.assertIn("现实检验", window.text)
        self.assertIn("布置练习", window.text)

    def test_chunk_strategy_marks_windows_as_chunk(self) -> None:
        result = ingest_document(
            data="""
# 干预流程
第一步先明确当前目标并建立任务边界。

第二步进行现实检验，梳理支持与反证。

第三步记录替代解释与后续练习。
""".strip(),
            title="Chunk Window",
            domain="psychology",
            dry_run=True,
            extract_strategy="chunk",
        )

        self.assertEqual(len(result.windows), 1)
        self.assertEqual(result.windows[0].strategy, "chunk")

    def test_invalid_extract_strategy_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported extract strategy"):
            ingest_document(
                data="""
# 干预流程
1. 先明确当前目标。
2. 再做现实检验。
""".strip(),
                title="Bad Strategy",
                domain="psychology",
                dry_run=True,
                extract_strategy="chunks",
            )

    def test_numbered_subsections_preserve_hierarchy_context(self) -> None:
        sections = parse_sections_from_text(
            """
3 认知重构

3.1 自动思维识别
先识别自动思维和触发事件。

3.2 证据检验
再评估支持证据、反证和替代解释。
""".strip(),
            default_title="CBT",
        )

        self.assertEqual(["3 认知重构", "3.1 自动思维识别"], sections[0].metadata["heading_path"])
        self.assertEqual("3 认知重构", sections[1].metadata["parent_heading"])

        result = ingest_document(
            data="""
3 认知重构

3.1 自动思维识别
先识别自动思维和触发事件。

3.2 证据检验
再评估支持证据、反证和替代解释。
""".strip(),
            title="CBT Hierarchy",
            domain="psychology",
            dry_run=True,
        )

        self.assertEqual(1, len(result.windows))
        first = result.windows[0]
        self.assertEqual("3 认知重构", first.section_heading)
        self.assertEqual(["3 认知重构"], first.metadata["heading_path"])
        self.assertIn("3.1 自动思维识别", list(first.metadata.get("subsection_headings") or []))
        self.assertIn("3.2 证据检验", list(first.metadata.get("subsection_headings") or []))

    def test_reference_like_body_is_skipped_even_without_reference_heading(self) -> None:
        result = ingest_document(
            data="""
# 研究摘要
这是正文说明。

文献列表
[1] Beck, A. T. (1979). Cognitive Therapy and the Emotional Disorders.
[2] Ellis, A. (1962). Reason and Emotion in Psychotherapy.
[3] https://doi.org/10.1000/example
[4] Dobson, K. S. (2010). Handbook of Cognitive-Behavioral Therapies.
""".strip(),
            title="Reference Filter",
            domain="psychology",
            dry_run=True,
        )

        self.assertEqual([], result.windows)

    def test_outline_llm_fallback_recovers_parent_and_subsections(self) -> None:
        result = ingest_document(
            data="""
Intervention Framework

Focus Reset
先帮助来访者收束当前焦点并明确本次目标。

Evidence Review
再检查支持证据、反证和替代解释。
""".strip(),
            title="Outline Fallback",
            domain="psychology",
            dry_run=True,
            ingestor=HeuristicDocumentIngestor(llm=_OutlineMockLLM()),
        )

        self.assertEqual(1, len(result.windows))
        self.assertEqual("Intervention Framework", result.windows[0].section_heading)
        self.assertEqual(["Intervention Framework"], result.windows[0].metadata["heading_path"])
        self.assertEqual("", result.windows[0].metadata["parent_heading"])
        self.assertIn("Focus Reset", list(result.windows[0].metadata.get("subsection_headings") or []))
        self.assertIn("Evidence Review", list(result.windows[0].metadata.get("subsection_headings") or []))

    def test_outline_llm_fallback_can_refine_low_confidence_partial_structure(self) -> None:
        result = ingest_document(
            data="""
3 认知重构

自动思维识别
先识别自动思维和触发事件。

证据检验
再评估支持证据、反证和替代解释。
""".strip(),
            title="Partial Outline",
            domain="psychology",
            dry_run=True,
            ingestor=HeuristicDocumentIngestor(llm=_OutlineMockLLM()),
        )

        self.assertEqual(1, len(result.windows))
        self.assertEqual("3 认知重构", result.windows[0].section_heading)
        self.assertEqual(["3 认知重构"], result.windows[0].metadata["heading_path"])
        self.assertIn("自动思维识别", list(result.windows[0].metadata.get("subsection_headings") or []))
        self.assertIn("证据检验", list(result.windows[0].metadata.get("subsection_headings") or []))

    def test_long_section_is_pre_split_before_window_building(self) -> None:
        para1 = "阶段目标 " + ("A" * 4200)
        para2 = "认知重构 " + ("B" * 4200)
        para3 = "家庭作业 " + ("C" * 4200)
        record = DocumentRecord(
            doc_id="doc-long",
            source_type="markdown_document",
            title="Long Section",
            domain="psychology",
            raw_text=f"# 长章节\n\n{para1}\n\n{para2}\n\n{para3}",
            sections=[
                DocumentSection(
                    heading="长章节",
                    text=f"{para1}\n\n{para2}\n\n{para3}",
                    level=1,
                    span=TextSpan(start=0, end=len(f"{para1}\n\n{para2}\n\n{para3}")),
                    metadata={"heading_path": ["长章节"]},
                )
            ],
            content_hash="hash-long",
        )

        windows = build_windows_for_record(
            record=record,
            strategy="chunk",
            max_chars=20000,
            max_section_chars=10000,
        )

        self.assertEqual(2, len(windows))
        self.assertEqual(1, windows[0].metadata["section_chunk_index"])
        self.assertEqual(2, windows[0].metadata["section_chunk_count"])
        self.assertEqual(2, windows[1].metadata["section_chunk_count"])
        self.assertLessEqual(len(windows[0].text), 10000)
        self.assertLessEqual(len(windows[1].text), 10000)


if __name__ == "__main__":
    unittest.main()
