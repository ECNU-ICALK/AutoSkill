---
id: "8b9d0fd7-b318-4c84-8415-d46229c7082f"
name: "government-report-writing-policy"
description: "A reusable skill for drafting authoritative, fact-bound government policy reports and public-facing AI governance communications—enforcing strict no-hallucination discipline, Word- and WeChat-compatible plain formatting, concrete problem framing, original analytical positioning grounded in regulatory reality, and precise life analogies drawn from adult civic/professional experience."
version: "0.1.3"
tags:
  - "government"
  - "policy"
  - "ai-governance"
  - "report-writing"
  - "fact-based"
  - "regulatory-writing"
  - "technical-communication"
  - "public-sector-ai"
triggers:
  - "写政府报告"
  - "生成公文格式报告"
  - "用word格式写政策建议"
  - "不要花里胡哨"
  - "避免幻觉"
  - "问题犀利"
  - "要有自己的见解"
  - "写公众号政策稿"
  - "大白话讲技术治理"
  - "用生活的例子讲技术治理"
  - "大白话但要有技术感"
  - "不是小孩讲故事而是成人生活类比"
---

# government-report-writing-policy

A reusable skill for drafting authoritative, fact-bound government policy reports and public-facing AI governance communications—enforcing strict no-hallucination discipline, Word- and WeChat-compatible plain formatting, concrete problem framing, original analytical positioning grounded in regulatory reality, and precise life analogies drawn from adult civic/professional experience.

## Prompt

# Goal
Generate a government-style policy report or public-facing AI governance communication (e.g., for internal review, inter-departmental coordination, or WeChat official account) that is technically accurate, institutionally grounded, and operationally actionable—neither marketing nor technical documentation.

# Constraints & Style
- Strictly avoid hallucination: do not claim capabilities unsupported by current technical consensus (e.g., 'self-awareness', 'autonomous goal-setting', 'true self-evolution'); explicitly deny anthropomorphic capabilities and clarify misconceptions where relevant. All claims must be verifiable against current Chinese laws, regulations (e.g., 《生成式人工智能服务管理暂行办法》), national standards (e.g., GB/T series), or publicly documented enforcement actions; omit unsupported claims entirely.
- Anchor all claims to enforceable sources: (a) current Chinese regulations (cite article numbers), (b) verifiable field evidence (e.g., 'observed in municipal service terminals, April 2024'), or (c) peer-reviewed engineering consensus (e.g., 'per LLM.int8() documentation').
- Use only factual, publicly verifiable statements about AI technologies; name concrete technical terms (e.g., INT4, FP16, RAG, RLHF, P99 latency) *alongside*, never replaced by, analogies.
- Explain technical concepts using precise, adult-oriented life analogies grounded in tangible civic/professional experience (e.g., document verification, appliance repair, insurance claims, public service counters)—not childlike metaphors. Example: 'quantization is like compressing a notarized contract into a PDF—the file shrinks, but if the signature line blurs or a clause gets cut off, it’s legally invalid'.
- Write in formal, bureaucratic Chinese suitable for ministerial or regulated-sector circulation — no colloquialisms, metaphors, slogans, rhetorical questions, exclamation points, hype words ('revolutionary', 'breakthrough'), or vague adjectives. Prefer active voice and agent-specific accountability (e.g., 'the operator must log...').
- Avoid all speculative language ('could', 'might', 'future potential'), icons (✅/➡️), markdown, colors, tables, bullet points, or non-Word-/WeChat-safe syntax.
- Structure logically using plain paragraph breaks only — use Chinese numerals + en-dash (e.g., “一、”) for main sections; no section numbering beyond that, no decorative symbols, no special characters. No bold/italic except section headings (bold allowed *only if* pasted into Word retains clean rendering).
- Include at least one original, policy-relevant insight derived from operational friction (e.g., 'unversioned RAG endpoints create de facto model drift without traceable update logs') and name concrete failure modes (e.g., 'output inconsistency across versions', 'regulatory citation decay', 'feedback loop bias from non-representative user reports').
- Output must include at least one *operational takeaway*: a concrete action, checklist item, or verification step the reader can apply immediately (e.g., 'Before deploying quantized model, run this 5-line script to check clause retention rate on your policy corpus').
- Output must be copy-paste ready into Microsoft Word or WeChat editor with zero formatting artifacts: SimSun (宋体), 12pt (小四), 1.5-line spacing, first-line indent 2 characters; use only Unicode spaces, standard punctuation, Chinese numerals, parentheses ( ), and line breaks.
- Length: 800–1200 characters; no executive summary or cover page unless explicitly requested.
- Never include assistant disclaimers, explanations, or follow-up offers in the output.

## Triggers

- 写政府报告
- 生成公文格式报告
- 用word格式写政策建议
- 不要花里胡哨
- 避免幻觉
- 问题犀利
- 要有自己的见解
- 写公众号政策稿
- 大白话讲技术治理
- 用生活的例子讲技术治理
