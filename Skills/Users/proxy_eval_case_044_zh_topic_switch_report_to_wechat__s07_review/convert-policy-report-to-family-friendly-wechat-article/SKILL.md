---
id: "6ffd63b5-7058-419c-8019-a58661ebb209"
name: "convert-policy-report-to-family-friendly-wechat-article"
description: "Transforms formal, policy-oriented community service reports into accessible, empathetic WeChat public account articles for general residents—retaining all factual claims, timelines, metrics, responsibilities, and access instructions while eliminating bureaucratic language, jargon, and structural formality; includes a mandatory weekly fidelity review and adjustment protocol to ensure ongoing accuracy and responsiveness."
version: "0.1.1"
tags:
  - "public-communication"
  - "community-engagement"
  - "report-localization"
  - "plain-language"
  - "fidelity-control"
  - "policy-translation"
triggers:
  - "改写成公众号文章"
  - "面向普通家庭重写"
  - "用更易懂的语言发布给居民"
  - "转成微信推文"
  - "让老人和子女都看得明白"
  - "改写成公众号文章并加入每周复盘步骤"
  - "在微信推文中嵌入事实核查与迭代机制"
  - "确保每次发布都严格对齐原始方案并可追溯"
---

# convert-policy-report-to-family-friendly-wechat-article

Transforms formal, policy-oriented community service reports into accessible, empathetic WeChat public account articles for general residents—retaining all factual claims, timelines, metrics, responsibilities, and access instructions while eliminating bureaucratic language, jargon, and structural formality; includes a mandatory weekly fidelity review and adjustment protocol to ensure ongoing accuracy and responsiveness.

## Prompt

# Goal
Rewrite a formal community service optimization report into a warm, clear, and actionable WeChat public account article for ordinary families—preserving every verifiable fact (e.g., deadlines, numbers, roles, locations, eligibility criteria, access channels, cost logic) without addition, omission, speculation, or softening.

# Constraints & Style
- Language: Plain, conversational Mandarin—short sentences, active voice, rhetorical questions (e.g., '您是否也经历过…?'), relatable scenarios, concrete verbs ('加装', '停靠', '教', '签个名'), inclusive pronouns ('咱们', '您', '家人'), and zero bureaucratic terms ('协同机制' → '一起配合', '结构性不足' → '不够用').
- Tone: Trustworthy, compassionate, and grounded—no hype, no vague promises ('soon', 'soon to be launched'), no invented benefits or emotional manipulation ('life-changing', 'don’t wait until it’s too late').
- Fidelity: All quantitative targets (e.g., '95% coverage by end-2024', '500 hand units', '3 pilot neighborhoods'), responsible entities ('community health center', 'street office'), timelines ('starting August', 'by June 2025'), service conditions ('free for 80+ solo/disabled elders'), access methods (phone, address, QR keyword), and disclaimers ('data as of June 2024', 'subject to latest notice') must appear *unchanged in meaning and scope* and be *explicitly traceable* to the source report—no paraphrasing that alters precision (e.g., '2024年底前' ≠ '今年底前' unless original says both).
- Structure: Use scannable, user-need-themed sections (e.g., 'Eating is easier', 'Help is closer', 'Tech support at home') with emoji-led headers (✅/📌/❤️/🍚/🏥/⌚/🏡), concrete callouts (phone number, location, deadline), and zero markdown tables, footnotes, appendices, or fictionalized stories.
- Prohibited: Invented names, speculative outcomes, emotional exaggeration, markdown formatting beyond headers/bullets, or any detail absent from the original report text.

# Workflow
1. Extract all factual anchors: dates, numbers, locations, roles, eligibility rules, service scope, cost logic, access channels (phone, address, keyword), verification mechanisms (e.g., 'quarterly public scorecards'), and attribution (e.g., 'XX Community Service Center').
2. Map each formal section to a family-relevant theme—not by report structure but by resident need (eating, health, tech, environment).
3. Rewrite using only confirmed facts—replace passive constructions ('will be implemented') with active, present/future commitments ('starts in July', 'you can book now').
4. Preserve all disclaimers and attribution.
5. End with clear, real-world CTAs (phone, address, keyword replies) matching those in the source.
6. At the end of each week (every Sunday), run an automated fidelity check: compare every sentence in the published article against the source report for factual alignment; flag any deviation (addition, omission, date shift, scope broadening).
7. If ≥1 fidelity issue is found: (a) log the discrepancy with timestamp and source line reference; (b) revert the article to last verified version within 24 hours; (c) notify the editorial lead and policy owner via email with evidence.
8. If ≥2 consecutive weeks show ≥1 unresolved fidelity issue: pause further publishing and trigger a full cross-departmental review before resuming.

## Triggers

- 改写成公众号文章
- 面向普通家庭重写
- 用更易懂的语言发布给居民
- 转成微信推文
- 让老人和子女都看得明白
- 改写成公众号文章并加入每周复盘步骤
- 在微信推文中嵌入事实核查与迭代机制
- 确保每次发布都严格对齐原始方案并可追溯
