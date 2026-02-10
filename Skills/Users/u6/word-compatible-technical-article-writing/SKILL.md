---
id: "cff9e1af-f993-40ee-8619-a43c27abaf1f"
name: "word-compatible-technical-article-writing"
description: "Generates or converts technically accurate, audience-appropriate long-form articles optimized for Microsoft Word compatibility — including clean heading hierarchy using Chinese numbering (e.g., '一、', '（二）', '1．'), plain-text formatting (no emojis/special symbols/Markdown), paragraph-based flow, fully fleshed-out sections with concrete examples, data points, and implementation details, strict de-identification of proprietary entities, and replacement of internal engineering jargon with plain-language functional equivalents."
version: "0.1.3"
tags:
  - "technical-writing"
  - "word-export"
  - "content-structuring"
  - "ai-engineering"
  - "documentation"
  - "de-identification"
  - "format-standardization"
  - "格式转换"
  - "公众号"
  - "去Markdown"
  - "技术传播"
  - "plain-language"
  - "user-facing"
triggers:
  - "用Word格式写"
  - "导出到Word"
  - "适配办公软件排版"
  - "生成可直接粘贴的公众号文稿"
  - "去掉符号，内容充实"
  - "使用word格式撰写"
  - "导出为正式文档"
  - "适配office排版"
  - "去掉符号直接可用"
  - "公众号文转word"
  - "转成word格式"
  - "去掉markdown符号"
  - "适配公众号word排版"
  - "纯文本导出"
  - "清除特殊符号"
  - "format this for Word"
  - "make it Word-compatible"
  - "remove tables and tech terms"
  - "export to docx-ready text"
  - "clean up for official documentation"
---

# word-compatible-technical-article-writing

Generates or converts technically accurate, audience-appropriate long-form articles optimized for Microsoft Word compatibility — including clean heading hierarchy using Chinese numbering (e.g., '一、', '（二）', '1．'), plain-text formatting (no emojis/special symbols/Markdown), paragraph-based flow, fully fleshed-out sections with concrete examples, data points, and implementation details, strict de-identification of proprietary entities, and replacement of internal engineering jargon with plain-language functional equivalents.

## Prompt

# Goal
Generate a polished, production-ready technical article suitable for direct copy-paste into Microsoft Word (.docx), with no formatting loss, symbol incompatibility, or hidden characters.

# Constraints & Style
- Use only standard ASCII and common UTF-8 Chinese characters: no emojis (e.g., 🌱, ❌), no special Unicode symbols (e.g., →, ⇒, ●, ▶, •), no Markdown syntax (e.g., `###`, `---`, `**bold**`, `> quote`, `🔹`, `✅`), no non-standard brackets (e.g., 『』【】); retain only full-width Chinese punctuation (，。！？；：）（）；
- Apply strict hierarchical heading structure using Chinese numbering: '一、Section Title' for H2, '（二）Subsection Title' for H3, '1．Point Title' for H4 — no Markdown syntax (## / ###) allowed;
- Every section must be substantively complete: include definition, real-world motivation, concrete example(s) with measurable outcomes (e.g., '37% accuracy gain', '72-hour detection-to-deployment'), deployment context (e.g., 'edge device', 'cloud API'), and explicit tooling/methodology references (e.g., 'EWC', 'LoRA', 'RAG', 'Avalanche', 'LangChain+Llama-3');
- Avoid bullet/numbered lists that rely on rich formatting; use plain dash-led or colon-separated phrasing where needed, ensuring linear readability in Word's default style;
- All citations and entities must be de-identified: replace specific company names, product names, platforms, locations, report IDs, and timestamps with neutral placeholders (e.g., '某金融风控系统', '某政务服务平台', '2024年实测数据'); retain technical metrics and methodological terms verbatim;
- Enforce term consistency: use canonical Chinese terminology throughout (e.g., '自进化智能体', not 'Self-Evolving Agent' or 'SEA'); first occurrence only may include English in parentheses if user explicitly provided it;
- Maintain formal, third-person prose: avoid contractions, colloquialisms ('咱们', '你猜怎么着'), and meta-commentary (e.g., '注：', '下期预告', '留言你最希望...' — integrate such content as natural concluding sentences);
- Paragraphs must be dense and self-contained: each ≥3 sentences, combining definition + mechanism + evidence/data/example;
- Use single blank lines between paragraphs; no first-line indentation, no extra blank lines, no tabs or zero-width characters; output must be UTF-8 clean and Word-paste-safe;
- Replace all internal engineering terminology (e.g., 'cross-task constraint merging', 'feedback gating', 'patch versioning') with plain-language functional equivalents — e.g., 'combine repeated rules from different tasks', 'only create skills when users consistently correct the AI', 'update existing skills instead of making new ones';
- Omit implementation details (e.g., file paths like `Users/u1/`, CLI flags like `--min-score 0.4`, or module names like `maintenance.merge()`);
- Preserve all user-specified structural elements (e.g., '是什么 / 为什么需要 / 怎么用 / 误区 / 实践步骤', '① 真实痛点', '② 方法本质', '三层能力基座') and slogans/taglines (e.g., 'Skill很火却不会用？...越用越聪明，越用越懂你！') verbatim — map them directly to Chinese-numbered headings without renaming or collapsing.

# Workflow
- Step 1: Scan input for non-standard symbols and replace them with spaces or standard Chinese punctuation;
- Step 2: Map any Markdown-style headings (## / ###) to Chinese-numbered hierarchy (一、／（二）／1．);
- Step 3: De-identify all named entities (organizations, tools, locations, reports, dates) while preserving technical metrics and methodology names;
- Step 4: Expand fragmented statements into cohesive, information-dense paragraphs with logical flow;
- Step 5: Rewrite technical explanations using only observable user-facing behavior — what the user sees, says, and experiences — not internal system mechanics;
- Step 6: Convert any tabular or structured comparison into sequential, sentence-based description;
- Step 7: Output pure text — no markdown, no HTML, no invisible characters — ready for immediate paste into Word.

## Triggers

- 用Word格式写
- 导出到Word
- 适配办公软件排版
- 生成可直接粘贴的公众号文稿
- 去掉符号，内容充实
- 使用word格式撰写
- 导出为正式文档
- 适配office排版
- 去掉符号直接可用
- 公众号文转word
