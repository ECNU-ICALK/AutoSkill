---
id: "ff43b81c-c44f-43e9-b994-f3e2994003a7"
name: "transform-formal-report-to-public-facing-article"
description: "Converts formal, policy-oriented government reports into clear, accessible, and actionable public communications for general family audiences—without inventing facts, exaggerating outcomes, or omitting constraints."
version: "0.1.0"
tags:
  - "public-communication"
  - "policy-translation"
  - "local-government"
  - "elderly-care"
  - "accessibility"
triggers:
  - "改写成公众号文章"
  - "转为面向普通家庭的宣传稿"
  - "用老百姓能听懂的话重写"
  - "生成居民版服务告知"
---

# transform-formal-report-to-public-facing-article

Converts formal, policy-oriented government reports into clear, accessible, and actionable public communications for general family audiences—without inventing facts, exaggerating outcomes, or omitting constraints.

## Prompt

# Goal
Rewrite a formal municipal service optimization report into a friendly, scannable, and trustworthy WeChat official account article for residents and family caregivers. Preserve all factual claims, timelines, responsibilities, eligibility conditions, and quantitative targets from the source—no fabrication, no softening of limits (e.g., 'up to 80% subsidy', '12月31日前完成', '租房老人同样可申请'), and no introduction of new services or benefits not present in the original.

# Constraints & Style
- Language: Plain Mandarin—short sentences, active voice, conversational but respectful tone (e.g., '您只需…', '不用预约，随到随测'); avoid bureaucratic terms ('协同机制', '字段级对接', '权责对等') and translate them functionally ('有人盯着更安心', '手机上随时看').
- Structure: Lead with relatable pain points; use ✅ emoji headers for each change; include concrete 'who/what/when/how' in every point; anchor all claims to verifiable deliverables (e.g., '2小时内医生线上响应', '审批时限压缩至7个工作日').
- Fidelity: Never imply universality unless stated (e.g., '全街道8个日间照料中心' ✅; 'all seniors get free home visits' ❌). Retain all qualifiers: '试点社区', '首批名单', '符合条件的家庭', '最高可享', '支持刷社保卡支付'.
- Formatting: No markdown tables or bullet nesting; use line breaks, emojis, and bold sparingly for emphasis only; keep paragraphs ≤3 lines; end with clear, real-world next steps (hotline, QR code prompt, in-person window info).
- Prohibited: Invented testimonials, speculative impact ('this will reduce loneliness by 30%'), unattributed policy sources, or visual suggestions (e.g., 'add photo of smiling elder').

# Workflow
1. Extract all time-bound actions, responsible parties, eligibility rules, and numeric targets from the formal report.
2. Map each policy element to a resident-facing benefit using direct cause-effect language ('X happens → Y changes for you').
3. Group related items under intuitive, non-technical headers (e.g., '社区里就能看医生' not '提升服务响应能力').
4. Rewrite all passive or institutional phrasing into second-person guidance ('you/your family' focus), preserving scope limits (e.g., '3个试点社区' remains explicit).
5. Verify every claim against the source: if a metric or deadline appears only in assistant output and lacks user confirmation, omit it.

## Triggers

- 改写成公众号文章
- 转为面向普通家庭的宣传稿
- 用老百姓能听懂的话重写
- 生成居民版服务告知
