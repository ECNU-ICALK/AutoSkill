---
id: "26b90ef6-6b8b-496d-8b6c-b775dc9acf02"
name: "family-property-claim-status-tracker-for-family"
description: "Generates a simplified, non-technical status tracking table for home property insurance claims, designed for family members with no insurance expertise to understand progress at a glance."
version: "0.1.0"
tags:
  - "insurance"
  - "claim-tracking"
  - "accessibility"
  - "family-communication"
  - "plain-language"
triggers:
  - "给家人看得懂的状态追踪表"
  - "家人版理赔进度表"
  - "通俗版理赔状态表"
  - "老人能看懂的理赔跟踪表"
---

# family-property-claim-status-tracker-for-family

Generates a simplified, non-technical status tracking table for home property insurance claims, designed for family members with no insurance expertise to understand progress at a glance.

## Prompt

# Goal
Generate a plain-language, visually clear claim status tracker table intended for family members (e.g., elderly parents, spouses, adult children) who need to follow along without insurance jargon, legal terms, or procedural complexity.

# Constraints & Style
- Use only everyday vocabulary: replace 'subrogation' → 'recovery from responsible party', 'indemnity' → 'reimbursement', 'adjuster' → 'claims agent', 'policyholder' → 'you' or 'the insured'.
- Never include legal citations, regulatory references, clause numbers, or insurer internal process names.
- Present status as simple phases: 'Reported', 'Waiting for Visit', 'Evidence Submitted', 'Being Reviewed', 'Approved / Partially Approved / Denied', 'Payment Sent'.
- For each phase, show: ✅ if done, ⏳ if in progress, ❌ if overdue (more than 3 business days past expected start), and a 1-line plain-English explanation (e.g., '⏳ Waiting for Visit → The insurance company is scheduling someone to look at the damage').
- Highlight next step and owner (e.g., 'Next: You upload photo receipts by Friday → [ ] Done') using checkable boxes.
- Output format: clean Markdown table (no nested tables, no colors); use only ASCII characters and emoji for universal readability.
- Exclude all case-specific identifiers: no policy numbers, names, addresses, dates, insurer names, or monetary amounts — use placeholders like <INSURER>, <CLAIM_ID>, <AMOUNT>.
- Do not generate templates for legal documents, scripts, or escalation paths — this is strictly a *status visibility* tool for non-experts.

# Workflow
None — this is a single-output generation task. No multi-step AI operations are specified or implied.

## Triggers

- 给家人看得懂的状态追踪表
- 家人版理赔进度表
- 通俗版理赔状态表
- 老人能看懂的理赔跟踪表
