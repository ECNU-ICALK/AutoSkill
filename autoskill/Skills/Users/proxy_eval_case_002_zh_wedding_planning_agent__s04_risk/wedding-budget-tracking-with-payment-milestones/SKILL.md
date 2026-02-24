---
id: "e42b43ee-56ff-4e01-8613-bf97fc4c7e6a"
name: "wedding-budget-tracking-with-payment-milestones"
description: "A reusable skill for managing wedding budgets up to a user-specified cap (e.g., ¥300,000), with enforced tracking of vendor payment milestones (deposit, progress, final) against timeline-critical deadlines."
version: "0.1.0"
tags:
  - "wedding"
  - "budget"
  - "finance"
  - "vendor-management"
  - "milestone-tracking"
triggers:
  - "track wedding payments"
  - "wedding budget with deadlines"
  - "vendor payment schedule"
  - "30万婚礼预算表"
  - "payment milestone tracker"
---

# wedding-budget-tracking-with-payment-milestones

A reusable skill for managing wedding budgets up to a user-specified cap (e.g., ¥300,000), with enforced tracking of vendor payment milestones (deposit, progress, final) against timeline-critical deadlines.

## Prompt

# Goal
Generate a vendor-level wedding budget tracker that enforces: (1) total cap (e.g., ¥300,000), (2) per-vendor payment schedule aligned to contractual milestones (e.g., deposit by D-90, final by D-30), and (3) real-time remaining headroom.

# Constraints & Style
- Output as a clean, printable Markdown table with columns: Vendor | Category | Total Budget | Deposit Due (Date) | Deposit Paid (Y/N) | Progress Due (Date) | Progress Paid (Y/N) | Final Due (Date) | Final Paid (Y/N) | Remaining Headroom
- All dates must be relative to wedding date (e.g., 'D-90', 'D-30') — never absolute calendar dates.
- Total row must show sum of 'Total Budget', sum of paid amounts, and strict calculation of remaining headroom = cap − sum(paid).
- Highlight any overdue payment due date in bold and red (e.g., **<span style='color:red'>D-90</span>**).
- Do not include vendor contact info, notes, or narrative — only structured, auditable financial tracking.
- Cap is fixed and non-negotiable; no row may exceed its allocated amount without explicit user override.

# Workflow
None — this is a static, deterministic output format. No AI reasoning or interpretation beyond parsing the provided cap and vendor milestones.

## Triggers

- track wedding payments
- wedding budget with deadlines
- vendor payment schedule
- 30万婚礼预算表
- payment milestone tracker
