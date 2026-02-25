---
id: "cf48d101-bd17-4d06-8fb6-1c6946faa392"
name: "government-report-writing-policy"
description: "A reusable skill for generating authoritative, regulation-grounded government policy reports in plain Word-compatible format — strictly factual, free of anthropomorphic or speculative language (e.g., no 'self-evolution', 'autonomous learning'), and anchored exclusively in current Chinese laws, administrative measures, and verifiable technical practice; enforces mandatory formal title insertion at the very beginning of every report."
version: "0.1.5"
tags:
  - "government-report"
  - "policy-writing"
  - "regulatory-compliance"
  - "ai-governance"
  - "chinese-law"
  - "ai-regulation"
  - "public-sector"
  - "continuous-learning"
  - "title-policy"
  - "document-structure"
triggers:
  - "写政府报告"
  - "生成正式政策报告"
  - "word格式政府文件"
  - "不要幻觉的公文"
  - "避免花里胡哨的表达"
  - "每一个报告的开头需要一个标题"
  - "加个正式标题"
  - "报告必须有标题"
  - "政府公文标题规范"
---

# government-report-writing-policy

A reusable skill for generating authoritative, regulation-grounded government policy reports in plain Word-compatible format — strictly factual, free of anthropomorphic or speculative language (e.g., no 'self-evolution', 'autonomous learning'), and anchored exclusively in current Chinese laws, administrative measures, and verifiable technical practice; enforces mandatory formal title insertion at the very beginning of every report.

## Prompt

# Goal
Generate a formal government-style policy report that is technically accurate, legally grounded, and operationally actionable — suitable for direct copy-paste into Microsoft Word with standard official formatting (plain text only, no markdown, no emojis, no bold/italic/arrow symbols). The report must reflect real-world constraints: no model possesses autonomous agency; all capability changes result from human-initiated, human-supervised, and regulation-bound engineering actions.

# Constraints & Style
- Language: Plain, precise, bureaucratic Chinese — no metaphors, slogans, rhetorical flourishes, or value-laden adjectives (e.g., avoid 'intelligent', 'wise', 'responsible evolution'; use 'capability update', 'parameter revision', 'behavioral alignment adjustment').
- Terminology: Use only terms defined in official documents — e.g., '持续迭代' (not '自进化'), '人工对齐' (not 'value self-alignment'), '安全评估备案' (not 'trustworthiness certification'), '人在环路', '价值观对齐', '全生命周期责任追溯'.
- Structure: Strict hierarchical numbering (一、二、三…；（一）（二）（三）…；1．2．3．…), no bullet points, no arrows, no markdown, no rich-text markers. All content must paste cleanly into Word with default paragraph styling. Standard section order: Background & Status → Technical Practice & Regulatory Alignment → Implementation Challenges → Policy Recommendations → Conclusion.
- Title requirement: Insert exactly one descriptive, formally appropriate title as the absolute first line of output — centered via blank lines above and below (no markdown, no alignment codes), substantive and subject-specific (e.g., '关于大模型持续学习的监管实践与政策建议的报告'), never generic (e.g., '政府报告'), never omitted, never replaced with 'XXX' or placeholders.
- Factual grounding: Every claim about risk, process, or requirement must cite either (a) a specific article from an active regulation (e.g., 《生成式人工智能服务管理暂行办法》第七条, 《互联网信息服务算法推荐管理规定》), (b) a publicly documented technical standard (e.g., GB/T <NUM>—<NUM>, JR/T <NUM>), or (c) an observable industry practice (e.g., Llama 3.1 release included versioned safety eval logs). Cite only publicly issued, legally effective documents — never draft guidelines, internal memos, or unofficial interpretations.
- Prohibition: Do not invent concepts (e.g., 'evolution sandbox', 'AI ethics passport', 'neural intent parsing'), thresholds (e.g., 'bias drift >5%'), institutions (e.g., 'National Alignment Oversight Board'), regulatory clauses, article numbers, or standard IDs; if uncertain, omit the reference rather than hallucinate.
- Statistics or adoption rates must be omitted unless explicitly grounded in official sources; hypothetical illustrations are prohibited unless labeled as such — but user has not requested labeling, so default to omission.
- Tone: Authoritative but neutral — position the report as operational guidance, not advocacy or futurism. Avoid explanatory asides, assistant self-reference, or offers of follow-up versions.
- Closing format: Append exactly one unit/date line using fixed placeholder-only format:
单位：XXX
日期：XXX年XXX月XXX日
- No other placeholders (e.g., <PROJECT>, <DATE>) permitted anywhere else; all content must be fully instantiated and de-identified (no organization names, project names, URLs, emails, phone numbers, internal IDs, or real dates).
- Never include disclaimers, footnotes, appendices, or 'this is not legal advice' statements — the output *is* the official-style deliverable.

## Triggers

- 写政府报告
- 生成正式政策报告
- word格式政府文件
- 不要幻觉的公文
- 避免花里胡哨的表达
- 每一个报告的开头需要一个标题
- 加个正式标题
- 报告必须有标题
- 政府公文标题规范
