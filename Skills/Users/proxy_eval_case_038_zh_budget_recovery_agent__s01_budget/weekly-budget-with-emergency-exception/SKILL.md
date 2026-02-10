---
id: "56de415a-18f3-47e8-80e5-7a9354459e3f"
name: "weekly-budget-with-emergency-exception-and-auto-correct"
description: "A reusable budgeting skill that enforces a strict weekly spending cap across all categories, allows pre-defined auditable emergency exceptions, and automatically triggers standardized corrective actions when overspending occurs in two consecutive weeks."
version: "0.1.1"
tags:
  - "budgeting"
  - "household-finance"
  - "rule-based-control"
  - "exception-handling"
  - "automation"
  - "financial-discipline"
triggers:
  - "按周设置消费上限"
  - "每周预算上限"
  - "保留应急例外规则"
  - "紧急支出豁免机制"
  - "周度消费封顶"
  - "连续两周超支"
  - "自动触发纠偏"
  - "预算超支自动响应"
---

# weekly-budget-with-emergency-exception-and-auto-correct

A reusable budgeting skill that enforces a strict weekly spending cap across all categories, allows pre-defined auditable emergency exceptions, and automatically triggers standardized corrective actions when overspending occurs in two consecutive weeks.

## Prompt

# Goal
Enforce a weekly spending limit for household expenses, segmented by category (fixed/survival, negotiable/autonomy, flexible/family co-benefit), apply an explicit, rule-based emergency exception mechanism, and auto-initiate corrective actions upon confirmed consecutive-week overspending.

# Constraints & Style
- Output only a clean, executable weekly budget plan in Markdown table format with columns: Category | Weekly Cap (¥) | Emergency Exception Rule | Tracking Method.
- Weekly cap must be derived from the user’s verified monthly net income and historical spending data (if provided); otherwise, use conservative defaults aligned with 55/25/20 survival/stability/flexibility allocation.
- Emergency Exception Rule must satisfy ALL of the following:
  • Defined as *only* unplanned, urgent, essential expenses (e.g., sudden medical co-pay, critical home repair, verified transport failure);
  • Requires pre-approval via a 2-question self-check: (1) 'Is this required to maintain health, safety, or core shelter within 48h?' (2) 'Is there zero viable lower-cost alternative available *now*?';
  • Triggers automatic logging: date, amount, justification (≤15 words), and post-hoc review prompt ('Did this meet both criteria? ✅/❌').
- Overspending correction activates **only** when actual outflow exceeds the weekly cap in *any one category layer* (survival, autonomy, or co-benefit) for two *consecutive natural weeks* (Monday–Sunday); corrections are concrete and non-punitive — e.g., reduce next week’s autonomy budget by 20%, require a 15-minute family review before any discretionary spend >¥100, or auto-disable one elastic payment method for 7 days.
- Corrections must reference and preserve the user’s existing emergency exception framework (e.g., documented, signed, ≤2/month); never invent new exceptions or thresholds.
- Never suggest rounding, estimates, or vague thresholds; all caps, rules, and corrections must be numeric and actionable.
- Do not include motivational language, explanations, or assistant commentary — output only the table and embedded logic.
- Use ¥ symbol; no commas in numbers; all text in Chinese.

# Workflow
1. Confirm or infer weekly net income (if not provided, state assumption clearly and ask for validation before proceeding).
2. Assign weekly caps per category using verified or default allocation ratios.
3. Embed the two-question emergency self-check and logging requirement directly into the 'Emergency Exception Rule' cell for each category.
4. After budget delivery, monitor actual outflow vs. caps weekly; if two consecutive weeks show overspending in any layer, generate a plain-text correction notice including: (a) confirmation of trigger condition met, (b) list of activated corrections, (c) clear reset condition (e.g., 'corrections lift after one compliant week').

## Triggers

- 按周设置消费上限
- 每周预算上限
- 保留应急例外规则
- 紧急支出豁免机制
- 周度消费封顶
- 连续两周超支
- 自动触发纠偏
- 预算超支自动响应
