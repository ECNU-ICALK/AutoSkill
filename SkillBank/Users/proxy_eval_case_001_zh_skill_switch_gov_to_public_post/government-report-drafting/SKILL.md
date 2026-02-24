---
id: "c6d49cfe-cc8c-49ed-acf6-367aceeec9a3"
name: "government-report-drafting"
description: "Generates formal government policy report drafts in standard bureaucratic style: restrained diction, no rhetorical flourishes or speculative claims, no markdown tables or decorative formatting, structured with plain numbered sections and unadorned prose."
version: "0.1.1"
tags:
  - "government"
  - "policy"
  - "formal-writing"
  - "bureaucratic-style"
  - "anti-hallucination"
triggers:
  - "写一份政府报告"
  - "起草政策报告初稿"
  - "正式公文风格"
  - "用词克制，不要花哨"
  - "内容要具体，问题要犀利，避免幻觉"
---

# government-report-drafting

Generates formal government policy report drafts in standard bureaucratic style: restrained diction, no rhetorical flourishes or speculative claims, no markdown tables or decorative formatting, structured with plain numbered sections and unadorned prose.

## Prompt

# Goal
Produce a formal government report draft on a specified policy topic, adhering strictly to official administrative writing conventions.

# Constraints & Style
- Use formal, neutral, and restrained language; avoid metaphors, superlatives, rhetorical questions, promotional phrasing (e.g., no 'leap forward', 'game-changing', 'paradigm shift', 'new starting point', 'unlock potential/dividends'), or speculative/hypothetical claims ('self-reflection', 'environment-triggered adaptation', 'lightweight online learning') unless explicitly attested in authoritative public sources.
- Present all content in continuous prose; do not use tables, bullet points, bold/italic emphasis, markdown syntax, or decorative separators ('---').
- Structure the report using standard bureaucratic sectioning: Roman numerals (I., II., III., etc.) for main sections; Arabic numerals (1., 2., 3., etc.) for subsections — or plain hierarchical headings (e.g., '一、', '（一）', '1．') if aligned with local convention; no sub-subsections deeper than two levels.
- Define problems with precision and critical edge: name concrete failure modes (e.g., 'fact consistency degradation', 'bias index spike', 'adversarial robustness decay'), not vague risks.
- Anchor all proposals to enforceable mechanisms: specify *who* acts, *what* is required, *how* compliance is verified (e.g., 'must submit an EIA report containing X, Y, Z before deployment'; 'shall log A, B, C in standardized format defined by GB/T XXXX-2025').
- Omit all placeholder tokens (e.g., <TOKEN>, <NUM>); replace with generic terms like 'relevant authorities', 'designated agencies', 'specified timeframe', or omit where syntactically invalid; never fabricate dates, names, legal article numbers, or unverified technical assertions.
- Do not include appendices, footnotes, editorial notes (e.g., 'this is a draft', 'for discussion only'), branding, institutional bylines, or signature blocks unless explicitly requested; if appendices are included, label generically (e.g., '附：术语简释') without inventing contents.
- Maintain third-person, passive-voice–preferred administrative tone throughout.

## Triggers

- 写一份政府报告
- 起草政策报告初稿
- 正式公文风格
- 用词克制，不要花哨
- 内容要具体，问题要犀利，避免幻觉
