---
id: "7bdb4f17-b28b-45ad-9ede-6d87e9511c03"
name: "family-property-claim-status-and-appeal-tracker"
description: "A dual-output skill that generates both a plain-language, visual claim status tracker for non-expert family members and a regulatory-aligned execution tracker for the policyholder — synchronized by phase logic, de-identified, and fully jargon-free."
version: "0.1.1"
tags:
  - "claim-tracking"
  - "claim-appeal"
  - "family-communication"
  - "plain-language"
  - "regulatory-compliance"
  - "de-identified-output"
triggers:
  - "给家人看得懂的状态追踪表"
  - "让爸妈也能看明白的理赔进度表"
  - "理赔申诉进度表要分两版"
  - "简明版+操作版进度表"
---

# family-property-claim-status-and-appeal-tracker

A dual-output skill that generates both a plain-language, visual claim status tracker for non-expert family members and a regulatory-aligned execution tracker for the policyholder — synchronized by phase logic, de-identified, and fully jargon-free.

## Prompt

# Goal
Generate two parallel, synchronized Markdown tables: (1) a **family-friendly claim status tracker**, using plain Chinese, intuitive status icons (✅/⏳/❌/🆘), and active-voice explanations — designed for quick scanning by family members with no insurance expertise; and (2) an **execution-ready claim appeal tracker**, containing precise deadlines (cited to regulation), named responsibilities ('You', 'Insurer', 'Third Party'), required actions, evidence formats, and de-identified placeholders (<POLICY_NUMBER>, <DENIAL_DATE>, <INSURER_NAME>, <YOUR_NAME>). Both tables must share identical phase structure, sequence, and dependency logic.

# Constraints & Style
- Language: Plain, conversational Chinese only — avoid all insurance terminology (e.g., say '保险公司重新看一遍' not '内部复核'; say '找行业调解组织帮忙' not '行业调解'); never use terms like '查勘', '定损', '核赔', '申诉', '复核', '仲裁'.
- Family version: Max 5 rows; columns must be exactly: 【阶段】| 【状态】| 【家人能看懂的说明】| 【下次提醒时间】; 【状态】 values only: ✅ 已完成 | ⏳ 进行中 | ❌ 暂停/卡住 | 🆘 需要帮忙; 【家人能看懂的说明】: 1 short sentence max, active voice, e.g., '我们已经寄出申诉信了' or '等保险公司3天内回复'; 【下次提醒时间】: fixed relative labels only — '今天' / '3天后' / '7天后' / '等通知'; include a 3-bullet 'What This Means For Us' footer in plain language.
- Execution version: Columns must be exactly: 【阶段】| 【截止时间】| 【负责人】| 【需完成事项】| 【提交方式与凭证】; cite regulatory anchors where applicable (e.g., '按《保险消费投诉处理管理办法》第十七条，5个工作日内答复'); use placeholder syntax consistently for all case-specific values; never invent steps or evidence types — reflect only user-confirmed statutory path (written objection → internal recheck → industry mediation → litigation/arbitration).
- No HTML, no images, no external dependencies, no dates requiring calculation, no calendar dates in table cells.
- Never include legal citations, internal insurer process names, or regulatory jargon in the family version.
- Output both tables consecutively, labeled clearly as '家庭版进度表' and '执行版进度表', with no intervening text or explanations.

# Workflow
1. Parse user’s confirmed claim or appeal framework: either standard claim phases (e.g., report → inspection → assessment → payout) or statutory appeal steps (written objection → internal recheck → industry mediation → litigation/arbitration).
2. Map each phase to parallel rows in both tables, preserving sequence and dependency.
3. For the family version: rewrite all actions into second-person active voice ('你寄出一封信说…'); suppress regulatory references but retain consequence-aware framing ('所以他们必须3天内回复').
4. For the execution version: insert mandatory compliance markers (deadline source, channel, evidence format); use only de-identified placeholders.
5. Output both tables as clean Markdown — no code blocks, no headers beyond labels, no extra commentary.

## Triggers

- 给家人看得懂的状态追踪表
- 让爸妈也能看明白的理赔进度表
- 理赔申诉进度表要分两版
- 简明版+操作版进度表
