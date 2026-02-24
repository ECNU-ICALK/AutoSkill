---
id: "f86265ff-aaeb-4f75-8439-1a6c672f7dd3"
name: "wedding-budget-tracking-schedule-300k"
description: "A reusable budget tracking schedule for weddings with a hard cap of 300,000 RMB, mapping vendor payments to precise timeline milestones (T-4 to T-1 month) and enforcing payment-node verification before task progression."
version: "0.1.0"
tags:
  - "wedding"
  - "budget"
  - "payment-tracking"
  - "milestone"
  - "vendor-management"
triggers:
  - "track wedding payments under 300k"
  - "wedding budget payment schedule"
  - "300k wedding payment nodes"
  - "verify wedding vendor payments"
  - "wedding milestone-based budget release"
---

# wedding-budget-tracking-schedule-300k

A reusable budget tracking schedule for weddings with a hard cap of 300,000 RMB, mapping vendor payments to precise timeline milestones (T-4 to T-1 month) and enforcing payment-node verification before task progression.

## Prompt

# Goal
Generate a wedding budget tracking schedule for a 120-person wedding with total budget ≤300,000 RMB, explicitly linking each major vendor payment to a verified milestone in the 4-month timeline (T-4 to T-1). Output must include: (1) vendor category, (2) max allowable amount, (3) exact payment trigger (e.g., 'after signed contract', 'upon delivery of 3D layout'), (4) required verification step (e.g., 'contract scan uploaded', 'layout approved in writing'), and (5) consequence of non-verification (e.g., 'hold next payment').

# Constraints & Style
- Enforce strict 300,000 RMB ceiling: no rounding up, no 'buffer' line items outside the cap.
- All payment triggers must be objective, observable, and time-bound — no vague terms like 'when ready' or 'as needed'.
- Verification steps must require concrete evidence (e.g., document upload, signed checklist, timestamped confirmation), not verbal assurance.
- If a vendor’s quoted price exceeds its allocated budget bucket, flag it as 'over-cap' and show shortfall amount — do not auto-reallocate.
- Output as a clean Markdown table with columns: Vendor | Budget Cap (¥) | Payment Trigger | Verification Required | Block If Unverified.
- Do not include general advice, tips, or tool recommendations — only the enforceable payment schedule.

# Workflow
1. Parse the 4-month wedding timeline into discrete, vendor-agnostic milestone phases (T-4, T-3, T-2, T-1).
2. For each core vendor category (venue, catering, photography, stationery, decor, attire, transport, contingency), assign a fixed budget cap summing to ≤300,000 ¥.
3. For each category, define exactly one primary payment trigger tied to a milestone phase and one mandatory verification action.
4. Validate that all triggers are sequential and non-overlapping — no two payments may share the same trigger condition.
5. Output only the final table; omit explanations, summaries, or offers for additional assets.

## Triggers

- track wedding payments under 300k
- wedding budget payment schedule
- 300k wedding payment nodes
- verify wedding vendor payments
- wedding milestone-based budget release
