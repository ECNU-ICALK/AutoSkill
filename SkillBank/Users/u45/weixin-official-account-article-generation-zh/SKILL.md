---
id: "0ab1ab16-471b-4769-a89c-a301ccb39c67"
name: "weixin-official-account-article-generation-zh"
description: "生成符合微信公众号平台调性与排版规范的中文原创文章，面向大众读者，强调可读性、结构清晰与去技术化表达。"
version: "0.1.0"
tags:
  - "weixin"
  - "content-writing"
  - "zh"
  - "humanized"
  - "plain-text"
triggers:
  - "写一篇微信公众号文章"
  - "生成公众号推文"
  - "用Word格式写公众号文"
  - "不要markdown，要word标准格式"
  - "公众号文案输出"
---

# weixin-official-account-article-generation-zh

生成符合微信公众号平台调性与排版规范的中文原创文章，面向大众读者，强调可读性、结构清晰与去技术化表达。

## Prompt

# Goal
Generate a WeChat Official Account article in standard Word document format (plain text with semantic paragraph breaks, no Markdown syntax), written in fluent, natural Chinese. The article must be self-contained, ready for direct copy-paste into Word, and follow WeChat's typical voice: approachable, lightly narrative, lightly metaphorical, and audience-aware (non-technical readers).

# Constraints & Style
- Output must contain **no Markdown** (e.g., no `###`, `**`, `-`, `>`, or code blocks); use only plain text with line breaks for section separation.
- Use full-width Chinese punctuation; avoid English punctuation except where linguistically required (e.g., product names).
- Paragraphs must be short (≤3 sentences), with clear topic sentences and logical flow.
- Avoid AI-typical patterns: no exaggerated metaphors (e.g., 'symphony of intelligence'), no -ing abstractions ('leveraging', 'optimizing'), no vague attribution ('studies suggest'), no triple-list rhetoric ('not only... but also... and more importantly...'), no overuse of em dashes (—) or colons.
- Replace promotional or speculative language with grounded, evidence-anchored statements (e.g., 'some systems can detect implicit feedback' instead of 'it magically learns').
- Include a concise, human-toned closing line — not a call-to-action, but a resonant takeaway.
- Do not include image suggestions, footnotes, or editorial notes (e.g., '(文末可配图建议...)') — those are not part of the Word-ready article.

# Workflow
1. Parse the core topic and target audience from user input.
2. Draft content using plain Chinese paragraphs only, organized into intuitive sections (e.g., title → hook → explanation → examples → significance → perspective → closing).
3. Apply humanization pass: remove all AI stylistic markers per the 'humanizer-zh' reference, prioritizing sentence rhythm, concrete verbs, and reader-centered phrasing.
4. Output final text as clean, Word-compatible plain text.

## Triggers

- 写一篇微信公众号文章
- 生成公众号推文
- 用Word格式写公众号文
- 不要markdown，要word标准格式
- 公众号文案输出
