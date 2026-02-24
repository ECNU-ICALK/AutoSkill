---
id: "60c4d95e-25ad-44e1-ba9b-7512d70bdf0d"
name: "family-claim-risk-prioritization"
description: "A reusable framework for identifying and documenting the top three context-specific risks in a household property insurance claim, paired with actionable, non-technical countermeasures — designed for shared family understanding and coordinated response."
version: "0.1.0"
tags:
  - "risk-management"
  - "family-collaboration"
  - "insurance-claim"
  - "preventive-action"
  - "plain-language"
triggers:
  - "补充前三大风险和对应预案"
  - "列出理赔中最可能出问题的三个环节"
  - "家庭理赔要重点防哪三件事"
  - "最该盯住的三个风险点是什么"
  - "理赔失败常见原因+我们怎么挡"
---

# family-claim-risk-prioritization

A reusable framework for identifying and documenting the top three context-specific risks in a household property insurance claim, paired with actionable, non-technical countermeasures — designed for shared family understanding and coordinated response.

## Prompt

# Goal
Generate a concise, family-friendly risk-prioritization table for a household property insurance claim, listing exactly the top 3 most likely or impactful risks (e.g., delay, evidence loss, miscommunication), each with a plain-language description and a concrete, executable prevention/mitigation step.

# Constraints & Style
- Output only a Markdown table with columns: **Risk**, **Why It Matters (1 sentence)**, **What We Do (actionable, who + when + how)**.
- Use zero insurance/legal jargon — terms like 'subrogation', 'indemnity', or 'exclusion clause' are forbidden.
- Prioritize risks by real-world impact on outcome (not by frequency alone): e.g., 'missing time-stamped photos' > 'late email reply'.
- Each 'What We Do' must be assignable to a family member, doable within 24h, and require no external approval (e.g., 'Mom texts plumber for quote by 5pm today' ✅; 'Wait for insurer’s approval' ❌).
- Never invent risks not grounded in common claim failure modes (e.g., no 'cyber breach' or 'regulatory audit').
- Do not include generic advice ('keep records') — only specific, behavior-triggered actions.
- If user provides a拒赔 notice or factual context (e.g., 'water leak', 'theft'), anchor risks to that scenario.

# Workflow
None — this is a single-step output. No staging, no follow-up logic.

## Triggers

- 补充前三大风险和对应预案
- 列出理赔中最可能出问题的三个环节
- 家庭理赔要重点防哪三件事
- 最该盯住的三个风险点是什么
- 理赔失败常见原因+我们怎么挡
