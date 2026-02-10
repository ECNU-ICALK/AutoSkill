---
id: "bd427b9d-5b26-4a75-b227-0c49e3c1b1f4"
name: "family-property-claim-status-tracker-with-weekly-review"
description: "A reusable, non-technical status tracking table for home property insurance claims, designed for non-expert family members, featuring plain-language milestones, auto-computed dates anchored to the report date, and a mandatory weekly review section to assess progress, flag blockers, and prescribe concrete next actions."
version: "0.1.1"
tags:
  - "claim-tracking"
  - "family-communication"
  - "plain-language"
  - "insurance-literacy"
  - "review"
  - "escalation"
triggers:
  - "给家人看得懂的状态追踪表"
  - "理赔进度表家人版"
  - "老人能看懂的保险进度表"
  - "简单明了的理赔状态表"
  - "增加每周复盘步骤和调整规则"
  - "理赔进度表加周回顾"
  - "家人版跟踪表要能每周检查"
  - "保险申诉表需要定期复盘"
---

# family-property-claim-status-tracker-with-weekly-review

A reusable, non-technical status tracking table for home property insurance claims, designed for non-expert family members, featuring plain-language milestones, auto-computed dates anchored to the report date, and a mandatory weekly review section to assess progress, flag blockers, and prescribe concrete next actions.

## Prompt

# Goal
Generate a simple, visual, time-based claim status tracker table that shows current claim progress in plain language — using only concrete milestones (e.g., 'Reported', 'Inspector visited', 'Offer received'), auto-computed dates anchored to <REPORT_DATE>, unambiguous status labels ('✅ Done', '⏳ Waiting', '⚠️ Stuck', '❌ Rejected'), and a fixed weekly review row. No insurance jargon, no clauses, no internal process terms.

# Constraints & Style
- Output only as a Markdown table with exactly 4 columns: **Step**, **Date/When**, **Status**, **What It Means (in 1 short sentence)**.
- Use only family-friendly, action-oriented language — e.g., 'We sent photos' instead of 'Evidence submitted'; 'They said “no” to part of it' instead of 'Partial denial issued'.
- All dates must be auto-computed from <REPORT_DATE> (e.g., D+3 = <REPORT_DATE> + 3 days); never use relative phrasing like '2 days ago' or 'next week' without anchor; never show absolute calendar dates unless computed from <REPORT_DATE>.
- Never include internal insurer roles (e.g., 'claims adjuster'), legal terms ('subrogation', 'reservation of rights'), or procedural labels ('Stage 2 review').
- If a step is pending, state *who* is waiting and *what they’re waiting for* — e.g., 'Waiting for repair quote from our contractor' — not 'Awaiting third-party assessment'.
- Append a fixed final row labeled '📆 Weekly Check-in (Every Sunday)' with exactly three sub-columns: 'What actually happened this week?' (max 15 words), 'Is anything RED? (e.g., no reply >3 days, missing document)' (yes/no + 1-word reason), and 'Next week’s top priority' (1 concrete action — if any RED is marked, this must be an escalation or external intervention, never 'wait longer' or 'follow up again').
- Omit all disclaimers, footnotes, instructions, headers, or explanations — the table must stand alone for a layperson.
- Do not generate templates, fillable fields, or tooling guidance — only the final rendered tracker.

# Workflow
1. Parse user-provided <REPORT_DATE> (required input).
2. Populate all timeline rows with computed dates and status logic.
3. Insert fixed '📆 Weekly Check-in (Every Sunday)' row at the bottom.
4. Pre-fill the 'Next week’s top priority' cell with a default escalation action *only if* the current phase is past its SLA (e.g., if D+15 has passed and no '复核决定书' is confirmed, default to 'Submit to 12378 today').
5. Output clean Markdown table ready for direct conversion to PDF/image/chat.

## Triggers

- 给家人看得懂的状态追踪表
- 理赔进度表家人版
- 老人能看懂的保险进度表
- 简单明了的理赔状态表
- 增加每周复盘步骤和调整规则
- 理赔进度表加周回顾
- 家人版跟踪表要能每周检查
- 保险申诉表需要定期复盘
