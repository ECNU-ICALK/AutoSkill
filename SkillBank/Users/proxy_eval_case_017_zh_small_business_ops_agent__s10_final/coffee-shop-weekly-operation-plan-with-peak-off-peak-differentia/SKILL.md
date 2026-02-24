---
id: "91560931-872e-448f-864a-b95e43706793"
name: "coffee-shop-weekly-operation-plan-with-peak-off-peak-differentiation"
description: "A reusable weekly operational planning framework for small coffee shops that explicitly separates strategy, staffing, inventory, and promotion logic between weekdays and weekends based on significant客流差异."
version: "0.1.0"
tags:
  - "coffee-shop"
  - "operational-planning"
  - "staff-scheduling"
  - "inventory-management"
  - "promotions"
  - "waste-reduction"
triggers:
  - "工作日和周末客流差异大"
  - "要分开策略"
  - "区分平日和假日运营"
  - "客流波峰波谷不同"
  - "周末人多平时少怎么安排"
---

# coffee-shop-weekly-operation-plan-with-peak-off-peak-differentiation

A reusable weekly operational planning framework for small coffee shops that explicitly separates strategy, staffing, inventory, and promotion logic between weekdays and weekends based on significant客流差异.

## Prompt

# Goal
Generate a weekly operational plan for a small independent coffee shop (2–3 staff, mixed dine-in/takeout) that applies distinct, evidence-based tactics for weekdays versus weekends — specifically differentiating in staffing allocation, inventory pacing, promotional timing, and loss mitigation — grounded in observed high/low traffic patterns.

# Constraints & Style
- MUST separate all core modules (scheduling, procurement, promotions, waste control) into two parallel tracks: 'Weekdays (Mon–Fri)' and 'Weekends (Sat–Sun)'.
- MUST avoid generic or blended advice (e.g., no 'daily' or 'throughout the week' directives without weekday/weekend qualification).
- MUST tie each tactic to an observable operational driver: e.g., 'Saturday morning surge → assign both baristas to espresso station', 'Friday afternoon slump → shift prep focus to next-day batch brewing'.
- MUST include at least one concrete guardrail per module: e.g., a staffing cap ("no solo shifts on Saturday >10am"), a stock threshold trigger ("if weekend takeout cup usage >180% of weekday avg, activate自带杯 incentive Monday"), or a promotion expiry rule ("all weekend-only offers auto-deactivate Sunday 18:00").
- MUST exclude theoretical KPIs (e.g., 'aim for 20% uplift'), unverifiable claims ('customers love surprise'), or platform-specific features (e.g., 'use Instagram Stories') unless user has previously confirmed channel use.
- Output must be immediately actionable: use tables, bullet constraints, and time-bound actions — no paragraphs of rationale unless embedded as brief 'Why' notes (≤1 line).
- Language: clear, imperative, de-identified — replace all proper nouns, locations, product names, and personal identifiers with placeholders like <COFFEE_BEAN_TYPE>, <LOCATION_TYPE>, or <CORE_DRINK>.

# Workflow
1. Infer baseline traffic pattern from user input: confirm if 'workday vs weekend difference' is defined by volume, timing, or customer type (e.g., remote workers vs families). If ambiguous, default to volume + timing.
2. For each of the four required modules (staffing, procurement, promotions, waste control), generate two parallel sub-sections: 'Weekdays' and 'Weekends', each containing:
   - A time-anchored action (e.g., 'Mon–Fri 7:30–8:00: pre-batch cold brew for AM rush')
   - A capacity rule (e.g., 'Sat/Sun: minimum 2 staff on espresso station 9:00–12:00')
   - A trigger-based adjustment (e.g., 'If weekend pastry sell-through <60% by 14:00, convert remainder to next-day affogato specials').
3. End with a cross-module synchronization note: e.g., 'Friday’s surplus milk → Saturday’s affogato base; Sunday’s low-traffic hours → staff training window.'

## Triggers

- 工作日和周末客流差异大
- 要分开策略
- 区分平日和假日运营
- 客流波峰波谷不同
- 周末人多平时少怎么安排
