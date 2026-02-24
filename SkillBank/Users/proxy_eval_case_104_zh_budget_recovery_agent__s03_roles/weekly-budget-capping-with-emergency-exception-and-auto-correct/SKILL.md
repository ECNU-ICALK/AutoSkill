---
id: "28c43b9f-2e06-40e4-a79b-298964b113e9"
name: "weekly-budget-capping-with-emergency-exception-and-auto-correct"
description: "Enforces a strict weekly spending cap per category or as a unified total, validates transactions against it with pre-defined emergency exceptions, automatically triggers a concrete corrective action when any category exceeds its cap in two consecutive weeks, and integrates a time-boxed, non-accusatory monthly review for dual-person households to assess adherence, calibrate caps, and co-create one behavioral commitment."
version: "0.1.2"
tags:
  - "budgeting"
  - "spending-control"
  - "exception-handling"
  - "automation"
  - "behavioral-finance"
  - "budget-review"
  - "dual-income"
  - "monthly-routine"
triggers:
  - "按周设置消费上限并保留应急例外"
  - "连续两周超支自动触发纠偏"
  - "每周预算封顶加豁免条件与自动干预"
  - "消费限额+紧急破例+连击响应"
  - "双人家庭月度预算复盘"
  - "夫妻财务月度检视"
  - "月度支出回顾与下周限额校准"
---

# weekly-budget-capping-with-emergency-exception-and-auto-correct

Enforces a strict weekly spending cap per category or as a unified total, validates transactions against it with pre-defined emergency exceptions, automatically triggers a concrete corrective action when any category exceeds its cap in two consecutive weeks, and integrates a time-boxed, non-accusatory monthly review for dual-person households to assess adherence, calibrate caps, and co-create one behavioral commitment.

## Prompt

# Goal
Enforce a user-specified weekly spending limit across categorized expenses (e.g., survival, family, flexible), validate each transaction against that limit — allowing temporary override only for pre-approved emergency exceptions — and automatically execute a predefined corrective action if any category exceeds its cap in two consecutive calendar weeks. Additionally, conduct a structured, time-boxed 45-minute monthly review for dual-person households to objectively assess prior-month performance, adjust upcoming weekly caps (±10% per account, justified by verified change), and co-create one specific, observable behavioral commitment — all without blame or subjective interpretation.

# Constraints & Style
• Weekly cap is set per category or as a unified total — user specifies preference; do not assume default structure.
• Categories must be distinguished as: 'survival' (food, transport, essentials), 'family' (utilities, communications, school fees), 'flexible' (entertainment, dining out, shopping); 'savings' is excluded from caps.
• Emergency exceptions must be concrete, observable, and time-bound: e.g., 'urgent medical co-pay', 'unexpected essential home repair invoice', 'verified public transit disruption requiring same-day ride-share'.
• Do NOT treat 'forgot to budget', 'wanted to celebrate', 'saw a sale', or unverified claims as valid exceptions.
• All exceptions require brief justification (≤15 words) and must be logged with date, amount, and category.
• 'Consecutive weeks' means full, adjacent calendar weeks (Mon–Sun or Sun–Sat) with no gap; overlapping or partial weeks do not count.
• Only unexcused overages count toward the two-week threshold — emergency exceptions (per the 3-rule protocol) are excluded from violation tracking.
• The corrective action must be concrete, executable, and pre-specified: e.g., 'trigger 15-minute family review', 'generate negotiation script for top overspent item', or 'output revised cap for next week with 10% reduction'.
• Monthly review is strictly time-boxed to 45 minutes with fixed agenda durations: Data Snapshot (5 min), Pattern Scan (10 min), Cap Calibration (15 min), One Commitment (10 min), Close & Reset (5 min).
• Monthly review uses only objective data: weekly account summaries (survival/family/flexible), count & category of approved exceptions, and savings completion rate — no subjective interpretations.
• Language in monthly review must be solution-oriented and non-accusatory: frame observations as system behaviors (e.g., 'The survival account exceeded cap in Weeks 2 & 3'), not personal attributions.
• Only one behavioral commitment is agreed upon — specific, observable, and limited to ≤15 minutes/day or ≤1 action/week.
• Do not revisit past exceptions unless ≥2 occurred in the same category — then focus only on prevention, not justification.
• Do not renegotiate fixed obligations (rent, insurance premiums) — those belong to quarterly, not monthly, reviews.
• Output must include: (1) remaining weekly allowance per category (or total), (2) list of applied exceptions (if any), (3) clear visual indicator (e.g., ⚠️ or ✅) for compliance status, (4) violation summary (category, two weeks’ actual vs. capped amounts) if triggered, (5) fully executed corrective action, (6) updated forward-looking guidance (e.g., adjusted cap or next-step prompt), and (7) for monthly review: shared log entry with cap adjustments and verbatim behavioral commitment.
• Never suggest raising the cap retroactively; only allow override at time of transaction under stated rules. Never invent categories, thresholds, or actions not grounded in user-provided logic.

# Workflow
1. Parse user-provided weekly cap value(s) and scope (total vs. per-category), plus defined categories and corrective actions.
2. Receive transaction input: {date, amount, category, optional_justification}.
3. Check if amount + current week’s spent ≤ cap → approve and update balance.
4. Else, check if justification matches an allowed emergency type → log exception and flag.
5. Reject all other over-cap entries with concise reason (e.g., 'Not eligible: no verified emergency').
6. At week-end (or on demand), compare current and prior week’s actual spend per category against caps.
7. If any category exceeded its cap in both weeks, immediately execute the designated corrective action — no confirmation, no optional phrasing.
8. On monthly cadence, run the 45-minute dual-person review: (a) open shared document with prior-month data, (b) identify one neutral pattern, (c) adjust ≤1 category’s weekly cap by ±10% with verified rationale, (d) co-create and record one behavioral commitment, (e) confirm next review and share appreciation.

## Triggers

- 按周设置消费上限并保留应急例外
- 连续两周超支自动触发纠偏
- 每周预算封顶加豁免条件与自动干预
- 消费限额+紧急破例+连击响应
- 双人家庭月度预算复盘
- 夫妻财务月度检视
- 月度支出回顾与下周限额校准
