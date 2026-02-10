---
id: "534cce45-75a6-49d9-8159-e8349cf8a650"
name: "weekly-budget-with-emergency-exception"
description: "Enforces a strict weekly spending cap across all categories, while embedding explicit, pre-defined conditions under which the cap may be temporarily exceeded for genuine emergencies."
version: "0.1.0"
tags:
  - "budgeting"
  - "spending-control"
  - "exception-handling"
  - "household-finance"
triggers:
  - "按周设置消费上限"
  - "保留应急例外规则"
  - "每周预算加例外"
  - "紧急情况破例规则"
  - "带豁免条款的周预算"
---

# weekly-budget-with-emergency-exception

Enforces a strict weekly spending cap across all categories, while embedding explicit, pre-defined conditions under which the cap may be temporarily exceeded for genuine emergencies.

## Prompt

# Goal
Enforce a weekly spending limit for household expenses, with built-in, rule-based exceptions for verified emergency scenarios — ensuring discipline without rigidity.

# Constraints & Style
• Output must be a single, self-contained Markdown table with exactly three columns: 'Category', 'Weekly Cap (¥)', and 'Emergency Exception Rule'.
• Categories must be derived from the user's tripartite budget structure: 'Fixed Expenses', 'Negotiable Expenses', 'Flexible Expenses'.
• Weekly caps must be expressed as absolute amounts (¥), not percentages or ranges.
• Emergency exception rules must be concrete, observable, and verifiable — e.g., 'Receipt for urgent medical co-pay ≥ ¥300', 'Official layoff notice dated within last 7 days', 'Utility shutoff warning letter'. Avoid vague terms like 'urgent' or 'serious' without objective anchors.
• No justification, explanation, or narrative text outside the table. No totals, footnotes, or examples.
• Do not invent categories, thresholds, or documentation requirements not grounded in user instruction.

# Workflow
None — this is a declarative configuration task, not a multi-step process.

## Triggers

- 按周设置消费上限
- 保留应急例外规则
- 每周预算加例外
- 紧急情况破例规则
- 带豁免条款的周预算
