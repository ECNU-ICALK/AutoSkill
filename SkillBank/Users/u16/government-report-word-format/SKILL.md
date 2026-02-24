---
id: "f8a5a6f5-f823-4ff6-be43-5b620320aff4"
name: "government-report-word-format"
description: "将政策类报告内容严格转换为符合中文政务文书规范的纯Word兼容格式，禁用Markdown、HTML、特殊符号及任何非标准排版。"
version: "0.1.0"
tags:
  - "government"
  - "report"
  - "word"
  - "formatting"
  - "decoration-free"
  - "bureaucratic"
triggers:
  - "用word格式"
  - "不要花里胡哨"
  - "纯文本输出"
  - "去掉markdown"
  - "公文直排格式"
examples:
  - input: "✅ 推动“人工标注—专家校验—多源验证”三位一体的数据质量治理体系"
    output: "1. 推动人工标注、专家校验、多源验证三位一体的数据质量治理体系"
  - input: "**一、基本判断**  \n当前大语言模型的发展呈现……"
    output: "一、基本判断\n当前大语言模型的发展呈现……"
---

# government-report-word-format

将政策类报告内容严格转换为符合中文政务文书规范的纯Word兼容格式，禁用Markdown、HTML、特殊符号及任何非标准排版。

## Prompt

# Goal
Convert a policy-oriented report into plain, Word-compatible text format.

# Constraints & Style
- Use only ASCII and standard Chinese characters (no emoji, no Unicode icons like ✅, —, or em-dashes);
- Replace all rich formatting with plain equivalents: use "---" for section dividers, "**bold**" → "【标题】", "*italic*" → plain text;
- No markdown syntax (e.g., no `**`, `###`, `-`, `>`, or code blocks);
- No decorative elements: omit all asterisks, arrows, checkmarks, horizontal rules beyond simple "---", and visual emphasis;
- Paragraphs must be left-aligned, single-spaced, with blank lines between sections;
- Section numbering must use plain Arabic numerals + Chinese punctuation (e.g., "一、基本判断");
- All dates, names, institutions, and project-specific references must be de-identified as <DATE>, <ORGANIZATION>, <PROJECT> unless explicitly required by user;
- Tone must remain formal, factual, and bureaucratic—no rhetorical flourishes, metaphors, or speculative language.

# Workflow
1. Strip all non-textual and non-essential formatting;
2. Normalize section headers using standard government document hierarchy (一、二、三…；1. 2. 3.…；(1) (2) (3)…);
3. Replace bullet points with plain line breaks and numbered/lettered lists where semantically necessary;
4. Ensure zero hallucination: retain only claims, principles, and recommendations explicitly stated in source;
5. Output clean UTF-8 text, ready for paste-into-Word without reformatting.

## Triggers

- 用word格式
- 不要花里胡哨
- 纯文本输出
- 去掉markdown
- 公文直排格式

## Examples

### Example 1

Input:

  ✅ 推动“人工标注—专家校验—多源验证”三位一体的数据质量治理体系

Output:

  1. 推动人工标注、专家校验、多源验证三位一体的数据质量治理体系

### Example 2

Input:

  **一、基本判断**  
  当前大语言模型的发展呈现……

Output:

  一、基本判断
  当前大语言模型的发展呈现……
