---
id: "e57e1cfa-e543-4c03-bae0-732e395e4ce9"
name: "public-service-report-to-wechat-article"
description: "Converts formal, policy-grounded public service reports into concise, executable WeChat public account articles for general families — preserving all verified facts (timelines, metrics, responsibilities, contact points, eligibility, and accountability mechanisms) while removing jargon, abstraction, and non-actionable content."
version: "0.1.1"
tags:
  - "wechat"
  - "public-communication"
  - "community-service"
  - "fidelity-preserving"
  - "executable-output"
triggers:
  - "改写成公众号文章"
  - "面向普通家庭重写"
  - "语言更易懂但不编造"
  - "转为微信推文"
  - "让老人和子女都看得明白"
---

# public-service-report-to-wechat-article

Converts formal, policy-grounded public service reports into concise, executable WeChat public account articles for general families — preserving all verified facts (timelines, metrics, responsibilities, contact points, eligibility, and accountability mechanisms) while removing jargon, abstraction, and non-actionable content.

## Prompt

# Goal
Transform a formal public service report (e.g., community aging support plan) into a WeChat public account article targeting ordinary families — delivering only what is actionable, verifiable, and immediately relevant. Output must be self-contained, scannable, fully traceable to the source, and strictly faithful to every factual claim: no invention, exaggeration, omission, or misrepresentation of dates, numbers, roles, locations, channels, thresholds, or verification mechanisms.

# Constraints & Style
- Language: warm, conversational Mandarin; use short sentences, active voice, and everyday vocabulary (e.g., '打个电话' not '通过电话渠道申请'; '多开半小时' not '延长服务时长30分钟'); avoid bureaucratic terms ('optimize', 'leverage'), jargon ('multi-stakeholder coordination'), passive constructions, and hedging modals ('将', '拟', '力争', '争取').
- Truth fidelity: Preserve *all* original facts exactly — names, numbers, deadlines (e.g., 'by July 15'), quantified targets (e.g., '120 meals/month'), responsible units (e.g., 'community居委会', 'certified nursing staff'), service boundaries (e.g., 'within 1 km', 'for those aged 65+'), contact points, eligibility criteria, and accountability features (e.g., 'monthly progress reports published online', 'response within 2 working days'). No rounding, paraphrasing, or invented options.
- Structure: Use only ✅ numbered items (max 5), each containing exactly four labeled sub-lines: '→ 能做什么', '→ 谁来负责', '→ 怎么联系', '→ 啥时候能用上'. Omit rhetorical questions, metaphors, slogans, emotional appeals, disclaimers, summary paragraphs, and warm closings.
- Accountability: Every item must include at least one concrete, observable checkpoint (e.g., date, phone number, location, count, time window, SLA).
- Length: Strictly ≤ 450 Chinese characters total (excluding title and byline 'XX社区综合服务中心').
- Voice: Maintain third-person institutional voice — no first-person plural ('we') unless explicitly used and endorsed in source context.

## Triggers

- 改写成公众号文章
- 面向普通家庭重写
- 语言更易懂但不编造
- 转为微信推文
- 让老人和子女都看得明白
