---
id: "87b995d9-5b2e-48e3-8860-1f4f9434877b"
name: "weekly-budget-overspend-auto-correct"
description: "Automatically triggers a predefined corrective action when weekly spending exceeds the cap for two consecutive weeks, enforcing accountability without manual intervention."
version: "0.1.0"
tags:
  - "budget"
  - "automation"
  - "enforcement"
  - "family-finance"
triggers:
  - "连续两周超支要自动触发纠偏动作"
  - "两周超支自动纠正"
  - "预算连超自动干预"
  - "周预算双周超标响应"
---

# weekly-budget-overspend-auto-correct

Automatically triggers a predefined corrective action when weekly spending exceeds the cap for two consecutive weeks, enforcing accountability without manual intervention.

## Prompt

# Goal
Enforce automatic, rule-based financial course correction when a household's weekly budget is exceeded for two consecutive weeks — without requiring user-initiated review or decision.

# Constraints & Style
- Must trigger *only* after two full, calendar-aligned weeks (e.g., Mon–Sun) both exceed the pre-set weekly spending cap.
- The corrective action must be concrete, immediate, and operational — not advisory (e.g., not 'suggest a review', but 'initiate a 15% reduction in next week’s elastic budget').
- Do not reference specific amounts, categories, or tools unless provided as inputs; use placeholders like <WEEKLY_CAP>, <ELASTIC_BUDGET>, <FAMILY_MEMBERS>.
- Output must be unambiguous: state the trigger condition, the exact action taken, and the effective timeframe.
- Exclude emotional language, encouragement, or rationale — only state the policy-mandated response.

# Workflow
1. Confirm two consecutive weeks have each exceeded <WEEKLY_CAP> (based on verified transaction data or user-confirmed entries).
2. Apply the pre-defined corrective action: reduce the upcoming week’s <ELASTIC_BUDGET> by 15% and freeze all <NEGOTIABLE_EXPENSES> renewals until manually re-enabled.
3. Generate a plain-text notification summarizing: (a) the trigger period, (b) the applied action, and (c) the reset condition (e.g., 'Two compliant weeks required to restore original allocation').

## Triggers

- 连续两周超支要自动触发纠偏动作
- 两周超支自动纠正
- 预算连超自动干预
- 周预算双周超标响应
