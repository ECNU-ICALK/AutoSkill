---
id: "1c05d149-fff7-4475-b8f5-d5038848f210"
name: "daily-claim-action-checklist"
description: "Generates a plain-language, executable daily checklist for insurance claim申诉 (appeal) actions — optimized for non-expert family members to follow without interpretation or decision overhead."
version: "0.1.0"
tags:
  - "checklist"
  - "insurance-claim"
  - "family-use"
  - "action-oriented"
  - "no-jargon"
triggers:
  - "再给一个可以直接执行的每日清单版本"
  - "每日可执行理赔清单"
  - "纯动作版申诉日程表"
  - "不带说明的每日任务表"
---

# daily-claim-action-checklist

Generates a plain-language, executable daily checklist for insurance claim申诉 (appeal) actions — optimized for non-expert family members to follow without interpretation or decision overhead.

## Prompt

# Goal
Generate a single-column, date-anchored, action-only daily checklist for insurance claim appeal execution, where each row is a concrete, time-bound, no-ambiguity task (e.g., 'Mail异议函 via EMS', 'Call投诉专线 and obtain case number'), with zero explanatory text, zero jargon, and zero optional items.

# Constraints & Style
- Output only a Markdown table with exactly two columns: | Date Anchor | Action |
- Date anchors must be absolute relative to D0 (e.g., 'D0', 'D1', 'D3', 'D5') — never 'today' or 'tomorrow'
- Every action must be verb-led, imperative, and physically executable by a layperson (e.g., 'Take photo of拒赔通知书 front/back', not 'Review the notice')
- No explanations, tips, warnings, or rationale — remove all 🟡/🟢/❗/🔹/text notes
- No placeholders like <TOKEN> — use generic terms: 'insurance company', 'complaint hotline', 'EMS', 'email', 'printed copy'
- All terminology de-identified: no insurer names, no law/article numbers, no URLs, no phone number patterns
- Table must cover D0 through D15, with *exactly one action per day* that is the highest-leverage, non-deferrable step for that day
- If no high-leverage action exists on a given day, omit that row — do not insert filler
- Use only ASCII characters; no emojis, no special symbols

# Workflow
None — this is a static, deterministic output format. No AI reasoning, no conditional branching, no personalization.

## Triggers

- 再给一个可以直接执行的每日清单版本
- 每日可执行理赔清单
- 纯动作版申诉日程表
- 不带说明的每日任务表
