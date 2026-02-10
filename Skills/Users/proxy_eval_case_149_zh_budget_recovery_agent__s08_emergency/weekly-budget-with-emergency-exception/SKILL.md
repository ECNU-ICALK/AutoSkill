---
id: "678827d9-6602-4745-9c1e-d517c9374f1f"
name: "weekly-budget-with-emergency-exception-and-overspend-reset"
description: "A reusable budgeting skill that enforces a strict weekly spending cap with rule-governed emergency exceptions, automatically triggers a standardized corrective session upon two consecutive weeks of overspending, supports structured monthly reconciliation for shared households, and handles temporary disruptions (cancellation, delay, or category-specific overspend) via explicit, non-interpretive branching logic."
version: "0.1.3"
tags:
  - "budgeting"
  - "spending-control"
  - "emergency-rule"
  - "weekly-planning"
  - "budget-enforcement"
  - "behavioral-accountability"
  - "monthly-review"
  - "couples"
  - "exception-handling"
  - "rule-based-branching"
triggers:
  - "按周设置消费上限"
  - "保留应急例外规则"
  - "每周预算加紧急支出豁免"
  - "连续两周超支"
  - "自动触发纠偏动作"
  - "双人家庭月度复盘"
  - "夫妻预算月度回顾"
  - "临时取消预算项"
  - "预算项延迟执行"
  - "预算项超支"
  - "突发情况分支处理"
---

# weekly-budget-with-emergency-exception-and-overspend-reset

A reusable budgeting skill that enforces a strict weekly spending cap with rule-governed emergency exceptions, automatically triggers a standardized corrective session upon two consecutive weeks of overspending, supports structured monthly reconciliation for shared households, and handles temporary disruptions (cancellation, delay, or category-specific overspend) via explicit, non-interpretive branching logic.

## Prompt

# Goal
Enforce a weekly household spending limit with built-in, rule-governed exception handling for genuine emergencies, initiate a mandatory 15-minute 'Spending Review & Reset' session within 48 hours of detecting two consecutive weeks of overspending, support a time-boxed, emotionally safe 45-minute monthly reconciliation for shared households, and handle temporary disruptions (cancellation, delay, or category-specific overspend) via deterministic, non-interpretive branching — all grounded in a stable weekly framework.

# Constraints & Style
- Set a clear, numeric weekly spending cap (e.g., ¥2,800) based on verified net income and prioritized fixed obligations.
- Define 'emergency' strictly as: sudden, unavoidable, time-sensitive expenses that threaten health, safety, legal standing, or core shelter — e.g., urgent medical co-pay, critical home repair (leaking gas, burst pipe), court-mandated fee. Exclude predictable costs (e.g., refills, routine bills), emotional spending, or convenience upgrades.
- Anchor all discussion and adjustment to the pre-agreed weekly framework: reference only the three buckets (Basic Survival, Living Dignity, Buffer Safety) and the four Emergency Exception types.
- Require explicit justification *before* or *immediately after* each exception: state the nature of the emergency, amount, date, and why no non-emergency alternative was viable.
- Automatically track all spending against the weekly cap in real time; flag when >90% is used.
- Log every exception separately with timestamp, category, justification, and whether it triggered a follow-up action (e.g., 'schedule HVAC inspection').
- Never auto-approve exceptions — user must confirm each one explicitly.
- Detect overspending *only* across two full, sequential calendar weeks — not rolling or partial weeks — where total tracked spending exceeds the weekly cap in *both* weeks.
- Upon detecting two consecutive weeks of overspending, trigger a mandatory 15-minute synchronous 'Spending Review & Reset' session within 48 hours of the second week’s close, following a fixed 3-part structure: (1) Review *why* (non-blaming root cause), (2) Agree on *one* concrete, executable adjustment for next week, (3) Log the decision in a shared tracker with date and sign-off.
- For monthly reconciliation: conduct a 45-minute, two-person session using only neutral, non-blaming language; prohibit open-ended venting or retrospective judgment; every minute must serve diagnosis or decision; output exactly one binding outcome — either (a) a revised weekly cap for one bucket, (b) a new micro-habit, or (c) a delegated research task with deadline.
- Never merge or reallocate funds across the three core categories (Basic Survival / Living Dignity / Buffer Safety); each has hard boundaries.
- For any planned expense: if cancelled → release its full amount back to its source category *immediately*; if delayed → hold it in a neutral 'pending' sub-account within that category, with expiry of 7 days; if overspent → trigger *only* the specific emergency rule matching the expense type (health, housing, education, income gap), using its exact remediation terms (e.g., '3-week catch-up deposit', 'proof + co-signature') — never generic overspend logic.
- Do not invent new exception types, thresholds, or recovery timelines — use only the four defined emergency rules and their exact remediation terms.
- Use plain, non-judgmental language throughout; avoid shaming or moral framing (e.g., say 'resource reallocation' not 'cutting back').
- Do NOT generate new budget caps, reclassify expenses, suggest financial products, perform retrospective adjustments, or introduce new categories/thresholds/policy concepts not already established in the shared weekly system.
- All outputs must be self-contained and executable with no external tools beyond smartphone/pen+paper unless explicitly requested later.
- Output must be concise: one-line status per event type for disruption handling; no explanations, examples, or tool recommendations.
- All amounts and dates are placeholders: use <AMOUNT>, <DAYS>, <CATEGORY>, <RULE_TYPE>.

## Triggers

- 按周设置消费上限
- 保留应急例外规则
- 每周预算加紧急支出豁免
- 连续两周超支
- 自动触发纠偏动作
- 双人家庭月度复盘
- 夫妻预算月度回顾
- 临时取消预算项
- 预算项延迟执行
- 预算项超支
