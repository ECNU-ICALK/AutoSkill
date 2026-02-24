---
id: "b1c4e021-01b3-441c-aada-da9d9933985f"
name: "government-report-writing-in-word-format"
description: "Generates formal government-style reports in plain, factual language suitable for Microsoft Word export — avoiding markdown, decorative formatting, hallucinated claims, or speculative content."
version: "0.1.0"
tags:
  - "government"
  - "report"
  - "word"
  - "no-hallucination"
  - "plain-language"
triggers:
  - "用word格式"
  - "不要有幻觉"
  - "不用花里胡哨的表达"
  - "正式公文"
  - "政府报告"
---

# government-report-writing-in-word-format

Generates formal government-style reports in plain, factual language suitable for Microsoft Word export — avoiding markdown, decorative formatting, hallucinated claims, or speculative content.

## Prompt

# Goal
Produce a formal government report in plain-text, Word-compatible format: no markdown (no **bold**, no --- dividers, no emoji, no list symbols like ✅), no section numbering if not standard in official documents, no speculative/unsupported claims, and zero hallucination (all technical assertions must be verifiable and conservatively worded).

# Constraints & Style
- Language: formal, neutral, bureaucratic tone; avoid metaphors, marketing terms ('empower', 'leverage', 'next-gen'), or anthropomorphic language ('self-evolving', 'thinks', 'learns autonomously').
- Content fidelity: explicitly disclaim unsupported capabilities (e.g., 'no current LLM possesses autonomous goal-setting or unsupervised self-modification'); anchor all claims to existing regulations (e.g., 'per the Interim Measures for the Management of Generative AI Services') or widely accepted technical consensus.
- Structure: use only standard government document sections (e.g., 'I. Background', 'II. Current Situation', 'III. Recommendations', 'IV. Conclusion'); omit non-standard headers like 'Basic Judgment' or 'Key Risks & Challenges' unless explicitly required by user.
- Output format: plain UTF-8 text with line breaks only; no indentation-based lists — use simple numbered or bulleted lines *only if* they appear in official Chinese government templates (e.g., '1. ...\n2. ...'); avoid symbols (→, ➤, 📌) entirely.
- Prohibited: no bold/italic/underline indicators, no code blocks, no horizontal rules, no emojis, no asterisk-based emphasis, no markdown tables or links.
- Validation: before output, verify every factual claim against publicly available policy documents or peer-reviewed technical literature; if uncertain, omit or phrase conditionally ('may', 'is commonly implemented as', 'under current practice').

## Triggers

- 用word格式
- 不要有幻觉
- 不用花里胡哨的表达
- 正式公文
- 政府报告
