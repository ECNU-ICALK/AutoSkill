---
id: "50ed3950-899e-4d8a-a5b6-75c7d57d910e"
name: "family-budget-weekly-cap-with-emergency-exception-overspend-correction-and-monthly-couple-review"
description: "A reusable skill for enforcing weekly spending limits across household expense categories with pre-defined emergency exceptions, triggering automatic corrective actions after two consecutive weeks of elastic overspending, initiating a lightweight 20-minute weekly reconciliation with rule-governed limit adjustment and assigned action, and closing the loop with a structured, low-burden monthly review for dual-adult households."
version: "0.1.3"
tags:
  - "budgeting"
  - "spending-control"
  - "emergency-rule"
  - "weekly-cycle"
  - "accountability"
  - "behavioral-nudge"
  - "review"
  - "couple"
  - "ritual"
  - "weekly-review"
  - "limit-adjustment"
  - "behavioral-accountability"
triggers:
  - "按周设置消费上限并支持应急例外"
  - "家庭预算周限额与连超自动纠偏"
  - "紧急支出豁免与两周超支响应机制"
  - "双人家庭月度复盘"
  - "家庭预算月度回顾"
  - "伴侣财务复盘流程"
  - "weekly budget review"
  - "adjust weekly spending limit"
  - "household weekly money check-in"
  - "elastic budget recalibration"
---

# family-budget-weekly-cap-with-emergency-exception-overspend-correction-and-monthly-couple-review

A reusable skill for enforcing weekly spending limits across household expense categories with pre-defined emergency exceptions, triggering automatic corrective actions after two consecutive weeks of elastic overspending, initiating a lightweight 20-minute weekly reconciliation with rule-governed limit adjustment and assigned action, and closing the loop with a structured, low-burden monthly review for dual-adult households.

## Prompt

# Goal
Enforce a strict weekly spending cap across categorized household expenses (fixed, negotiable, flexible), permit deviations *only* for documented emergencies, automatically initiate pre-defined corrective actions if elastic spending exceeds its weekly upper limit for two full, sequential calendar weeks, conduct a standardized 20-minute weekly budget reconciliation resulting in verified elastic spend, one rule-based limit adjustment (if triggered), and one concrete assigned action, and conduct a time-boxed, outcome-oriented monthly financial review between two adults — all without manual override or ad-hoc decisions.

# Constraints & Style
• Output must be a clear, executable budget rule — not advice or explanation.
• Weekly cap applies separately to each of the three categories: fixed, negotiable, flexible — no cross-category borrowing.
• Emergency exceptions are permitted *only* for: (1) urgent medical out-of-pocket costs (e.g., ER co-pay, prescription refill after stockout), (2) critical home/vehicle repairs preventing safety or basic function (e.g., broken heater in winter, flat tire blocking commute), or (3) verified income disruption (e.g., pay delay >5 business days, layoff notice).
• Every emergency exception must be logged with: date, category, amount, reason (mapped to one of the three criteria), and supporting evidence type (e.g., 'ER receipt', 'mechanic quote', 'HR termination email').
• No exceptions allowed for: travel, gifts, dining out, subscriptions, aesthetics, convenience, or 'future savings' justifications.
• Cap resets every Monday 00:00; unused amounts do NOT roll over.
• Overspend is defined strictly as: elastic spending > weekly elastic upper limit, *net of approved emergency exceptions*.
• Corrective actions trigger *only* after two full, sequential calendar weeks of confirmed elastic overspend — not partial, non-consecutive, or single-week events.
• Corrective actions must be concrete, pre-defined, and executable without external input: (a) pause all non-essential subscriptions (streaming, apps, gyms) by account holder within 24h of Week 2 close; (b) reduce next week’s elastic upper limit by 15% (rounded to nearest ¥10); (c) schedule mandatory 15-minute family financial review before start of next week using pre-filled template highlighting overspend pattern and one root-cause hypothesis.
• Weekly reconciliation is strictly time-boxed to 20 minutes — enforced via pre-set timer; no extensions.
• Weekly inputs are limited to: (a) last week’s payment app summary (screenshot or text), (b) current week’s elastic spending limit, (c) any active emergency exceptions used.
• Elastic limit may be adjusted *only* under these conditions:
  • Increase allowed only if: (i) prior week’s elastic spending was ≤90% of limit *and* (ii) at least one pre-approved 'small experiment' (e.g., 'no外卖 Wed') succeeded; max +10% increase, rounded down to nearest ¥10.
  • Decrease required if: (i) prior week’s elastic spending exceeded limit by ≥20%, *or* (ii) two emergency exceptions were used; min −10% decrease, rounded up to nearest ¥10.
• Weekly output must be plain-text markdown with exactly four fields: `🔹 Verified elastic spend`, `🔹 Adjusted limit (if changed)`, `🔹 Agreed action`, `🔹 Owner & deadline`.
• All monetary values use ¥ symbol and no commas; durations use "D+X" notation (e.g., "D+2" = two days from now).
• No discussion of past intent, blame, or hypotheticals — only observable behavior and forward-looking actions.
• Monthly review is strictly for two adults (e.g., partners, cohabiting peers); excludes children or third parties.
• Use neutral, non-judgmental language: replace 'overspend', 'failure', 'loss of control' with 'deviation', 'displacement', 'recalibration'.
• All monthly review data comes exclusively from already-recorded weekly operational boards — no re-reconciliation or per-transaction tracing.
• Monthly review is time-boxed to 60 minutes with fixed phases: Review (15min), Attribution (20min), Decision (15min), Snapshot generation (10min).
• Monthly output must be archive-ready: printable/screenshotable, with all personally identifiable information and exact monetary values removed (use ranges like ¥500–¥600).
• Monthly review does not introduce new rules, categories, or tools — it only validates and closes the loop on the existing weekly cap, emergency exception, double-week correction, and weekly reconciliation system.
• Language must be directive and operational — suitable for embedding in a shared family dashboard or spreadsheet validator.

## Triggers

- 按周设置消费上限并支持应急例外
- 家庭预算周限额与连超自动纠偏
- 紧急支出豁免与两周超支响应机制
- 双人家庭月度复盘
- 家庭预算月度回顾
- 伴侣财务复盘流程
- weekly budget review
- adjust weekly spending limit
- household weekly money check-in
- elastic budget recalibration
