---
id: "be1e0557-8982-4751-88e0-a856de643e1e"
name: "family-property-claim-status-tracking-table-for-family"
description: "Generates a simplified, non-technical claim status tracking table designed for family members with no insurance expertise — using plain language, visual cues, and minimal jargon to convey progress, next steps, urgency, and common disruptions (temporary cancellation, delay, budget overrun)."
version: "0.1.1"
tags:
  - "claim-tracking"
  - "family-communication"
  - "plain-language"
  - "status-table"
  - "contingency-handling"
triggers:
  - "给家人看得懂的状态追踪表"
  - "让爸妈能看明白的理赔进度表"
  - "简单版理赔跟踪表"
  - "家属版理赔状态表"
  - "加入突发情况分支：临时取消、延迟或超预算"
  - "家属版理赔表要包含取消/延迟/超支提醒"
  - "简洁版理赔跟踪表带意外情况处理"
---

# family-property-claim-status-tracking-table-for-family

Generates a simplified, non-technical claim status tracking table designed for family members with no insurance expertise — using plain language, visual cues, and minimal jargon to convey progress, next steps, urgency, and common disruptions (temporary cancellation, delay, budget overrun).

## Prompt

# Goal
Generate a printable or mobile-friendly claim status tracking table that a non-insurance-proficient family member (e.g., elderly parent, spouse, adult child) can understand at a glance — showing current stage, who’s responsible, what’s done/missing, when action is needed, and how to respond to three common disruptions: temporary cancellation, delay beyond expected timeline, or cost exceeding initial estimate.

# Constraints & Style
• Use only everyday vocabulary: replace 'subrogation' → 'insurance company handles neighbor claim'; 'loss adjuster' → 'claims inspector'; 'indemnity' → 'payout'; 'loss assessment' → 'damage check'; 'indemnity offer' → 'payment promise'.
• Avoid all insurance terms without immediate plain-language translation in parentheses.
• No dates, names, case IDs, insurer names, contact details, or exact numbers — use relative phrasing ('next workday', 'within 2 days') and placeholders like <NEXT-FOLLOWUP-DATE>, <REPORT-NUMBER>, <INSURER-NAME>.
• Include four visual priority markers: ✅ (done), ⚠️ (waiting on us), ❓ (waiting on insurer), 🟢 (on track), 🟡 (waiting normally), 🔴 (urgent action needed) — no color reliance (i.e., do not say 'red = urgent').
• Disruption rows (⚠️) must be dedicated, labeled rows — not notes or sidebars — each containing: (1) trigger condition in plain terms, (2) one-sentence explanation, (3) exactly one concrete action the family should take: 'Call to reschedule' (cancellation), 'Call to confirm new date' (delay), 'Ask for written cost breakdown' (over-budget).
• Table must fit on one A4 page or smartphone screen without horizontal scroll; max 8 rows total.
• Header must state: 'This is NOT official paperwork — it’s just for our family to stay in sync.'
• Never include legal disclaimers, regulatory references, procedural fine print, nested sections, or footnotes.

# Workflow
1. Extract only the *current known status* from user-provided context (e.g., 'after first inspection', 'awaiting repair quote', 'partially denied').
2. Map that status to one of five universal stages: (a) Just reported, (b) Inspector visited, (c) Estimate received, (d) Decision made, (e) Payout pending.
3. For each stage, auto-populate: (i) What this means in 1 short sentence, (ii) Who is doing what (us / insurer / third party), (iii) What we need to do next (if anything), (iv) When it’s due or expected.
4. Insert exactly one ⚠️ disruption row immediately after the stage where that disruption most plausibly occurs — for 'temporary cancellation', 'delay beyond expected timeline', and 'cost exceeds initial estimate'.
5. Output only the completed table — no intro, no explanation, no offer to customize further.

## Triggers

- 给家人看得懂的状态追踪表
- 让爸妈能看明白的理赔进度表
- 简单版理赔跟踪表
- 家属版理赔状态表
- 加入突发情况分支：临时取消、延迟或超预算
- 家属版理赔表要包含取消/延迟/超支提醒
- 简洁版理赔跟踪表带意外情况处理
