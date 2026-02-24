---
id: "f28e1c8f-cd41-4b7f-9ca8-81e20f7e442b"
name: "generate-family-claim-status-tracker-for-non-experts"
description: "A reusable procedure to generate a clear, non-technical insurance claim status tracker designed for family members with no insurance expertise — using plain language, visual cues, and zero jargon, while minimizing implementation cost by 10% via strategic simplification without compromising usability."
version: "0.1.1"
tags:
  - "claim-tracking"
  - "accessibility"
  - "family-communication"
  - "plain-language"
  - "cost-optimization"
triggers:
  - "给家人看得懂的状态追踪表"
  - "做个老人能看明白的理赔进度表"
  - "让家里人不用问就能知道理赔到哪了"
  - "简单明了的理赔步骤跟踪表"
  - "做个更轻量但同样清晰的理赔进度表"
---

# generate-family-claim-status-tracker-for-non-experts

A reusable procedure to generate a clear, non-technical insurance claim status tracker designed for family members with no insurance expertise — using plain language, visual cues, and zero jargon, while minimizing implementation cost by 10% via strategic simplification without compromising usability.

## Prompt

# Goal
Generate a printable or mobile-friendly claim status tracking table that any family member (e.g., elderly parent, teen, non-insurance professional) can understand at a glance — showing current phase, next step, owner, deadline, and what 'done' looks like — without requiring domain knowledge. Output must be a single self-contained Markdown table plus one ready-to-share empathetic status message template.

# Constraints & Style
- Use only plain, conversational language: replace terms like 'subrogation', 'indemnity', or 'loss adjuster' with equivalents like 'insurance company's damage checker' or 'money they owe you'.
- Never assume familiarity with insurance processes: explain each stage in one short phrase (e.g., 'They’re checking photos and reports' instead of 'Loss assessment in progress').
- Visual clarity is mandatory: use ✅/⏳/⚠️/❌ icons consistently; include color-ready placeholders (e.g., '[GREEN] Done', '[YELLOW] Waiting') but do not hardcode actual colors (for accessibility and print compatibility).
- Omit all case-specific identifiers: no policy numbers, names, dates, addresses, or insurer names — use placeholders like <POLICY_REF>, <REPORT_DATE>, <INSURER>.
- Structure must be strictly tabular (Markdown table), with exactly these 5 columns: **Stage**, **What’s Happening**, **Who’s Doing It**, **By When**, **How We’ll Know It’s Done**.
- Each row must represent a discrete, observable milestone — no abstract or internal process steps (e.g., 'Underwriter review' → ❌; 'They send us a paper saying how much they’ll pay' → ✅).
- Replace high-effort delivery formats (custom PDF, branded Excel, multi-channel broadcasts) with a single responsive Markdown table + optional plain CSV export + one copy-paste WhatsApp/WeChat message template.
- Pre-calculate all deadlines from a single user-provided date (e.g., <REPORT_DATE>): apply fixed calendar arithmetic (5 working days = Mon–Fri, exclude weekends unless specified); show deadlines as fixed formatted dates (e.g., 'Sync due: May 23'), not formulas or placeholders like <DUE_DATE>.
- Do not include instructions, footnotes, explanations, or external assets — the table and message template must be self-explanatory and fully contained.

# Workflow
1. Extract the user’s reported claim start date (e.g., <REPORT_DATE>).
2. Pre-calculate all critical dates: Day 3 / Day 6 / Day 9 sync deadlines, standard processing windows (e.g., '5 working days after inspection'), and material submission deadlines — using fixed calendar arithmetic (assume standard workweek unless holidays are explicitly provided).
3. Populate the table with plain-language stage names, status icons, fixed dates, and unambiguous action prompts.
4. Generate one concise, empathetic, shareable family-group message template that mirrors the table’s current status row.

## Triggers

- 给家人看得懂的状态追踪表
- 做个老人能看明白的理赔进度表
- 让家里人不用问就能知道理赔到哪了
- 简单明了的理赔步骤跟踪表
- 做个更轻量但同样清晰的理赔进度表
