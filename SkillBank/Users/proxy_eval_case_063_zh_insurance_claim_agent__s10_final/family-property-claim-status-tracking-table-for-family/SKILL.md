---
id: "a0728762-6ae0-4c52-99c6-20c6b6daf9c9"
name: "family-property-claim-status-tracking-table-for-family"
description: "A reusable, plain-language status tracking table designed for family members with no insurance expertise — visual, time-based, and action-oriented, using unambiguous icons and concrete physical/digital actions."
version: "0.1.1"
tags:
  - "family-communication"
  - "status-tracking"
  - "plain-language"
  - "insurance-claim"
  - "non-expert"
  - "checklist"
triggers:
  - "给家人看得懂的状态追踪表"
  - "让爸妈也能看明白的理赔进度表"
  - "简单明了的家庭理赔跟踪表"
  - "适合老人看的保险进度表"
  - "最终版要求：简洁、可执行、检查点不遗漏"
---

# family-property-claim-status-tracking-table-for-family

A reusable, plain-language status tracking table designed for family members with no insurance expertise — visual, time-based, and action-oriented, using unambiguous icons and concrete physical/digital actions.

## Prompt

# Goal
Generate a printable, family-friendly status tracking table for a home property insurance claim (including appeals), showing current stage, next deadline, required actions, and simple status indicators — all without insurance jargon or legal terms.

# Constraints & Style
- Use only plain, conversational Chinese (e.g., '查勘员还没来' not '查勘尚未完成'; '等保险公司回复' not 'awaiting reconsideration')
- Replace all technical terms: 'subrogation' → '找楼上邻居要钱的事', 'indemnity' → '赔多少钱', 'adjuster' → '保险公司来的检查人员', 'mediation' → '第三方帮助会议', '12378' → '监管热线', 'reconsideration' → '等保险公司回复'
- Columns must be: 【当前在哪】｜【最晚哪天做】｜【我们该做什么】｜【状态】
- Status column uses only three emoji-led labels: ✅ 已完成｜⏳ 进行中｜⚠️ 要催了 (for standard claims) OR ✅ / ⏳ / ❌ (for appeal steps — use ❌ only when explicitly blocked or denied)
- For standard claims: auto-calculate next action date from <出险日期> as business-day offset (e.g., '等查勘员' → T+2 workday → show actual date); for appeals: use blank fill-in '____年__月__日' only
- No policy numbers, names, addresses, case IDs, or legal citations — use placeholders like <保单尾号>, <出险日期>, '__天', '¥______'
- Fit on one A4 page in landscape orientation; use bold headers and ample white space
- Under '我们该做什么', list only concrete, physical or digital actions a non-expert can do (e.g., '把手机里照片原图发给理赔员', '一起去邮局寄申诉材料', '拨打12378时全家一起听')
- Do not include escalation logic, internal insurer SLAs, explanations, footnotes, or assistant commentary — output is a single clean Markdown table only
- Rows must cover both standard claim and appeal flow: 报案完成、现场拍照存证、等查勘员、提交材料、等定损结果、确认赔付、结案、收到拒赔通知、提交申诉、等待保险公司回复、申请第三方帮助会议、拨打监管热线、案件解决

## Triggers

- 给家人看得懂的状态追踪表
- 让爸妈也能看明白的理赔进度表
- 简单明了的家庭理赔跟踪表
- 适合老人看的保险进度表
- 最终版要求：简洁、可执行、检查点不遗漏
