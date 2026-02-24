---
id: "b99843b3-74d8-4840-938a-528f4cfd5981"
name: "family-travel-contingency-planner"
description: "Generates a dual-version family travel plan (execution + family-group summary) with built-in branching logic for weather, health, and operational disruptions — including cancellation, delay, and budget overrun triggers."
version: "0.1.0"
tags:
  - "family-travel"
  - "contingency-planning"
  - "accessibility"
  - "budget-control"
  - "multi-version-output"
triggers:
  - "突发取消"
  - "行程延迟"
  - "超预算"
  - "天气变化"
  - "老人膝痛加重"
---

# family-travel-contingency-planner

Generates a dual-version family travel plan (execution + family-group summary) with built-in branching logic for weather, health, and operational disruptions — including cancellation, delay, and budget overrun triggers.

## Prompt

# Goal
Generate a concise, dual-version (Execution Version + Family Group Summary) 6-day高铁-based family travel plan for 2 adults + 1 elderly person with knee limitations + 1 child, embedding explicit, actionable contingency branches for three disruption types: (1) full trip cancellation, (2) single-day delay (e.g., due to weather or health), and (3) budget overrun (>5% of total cap). All branches must be pre-defined, no ad-hoc reasoning.

# Constraints & Style
- Must output exactly two clearly labeled sections: '【执行版】' (detailed, operational, with time anchors, vendor confirmations, and risk-mitigation specs) and '【家庭群简版】' (≤150 words, plain language, emoji-light, scannable by non-planners).
- Every contingency branch must specify: (a) trigger condition (e.g., "knee pain score ≥7/10 confirmed by on-site clinic"), (b) immediate action (e.g., "activate B-plan + notify hotel via pre-saved template"), and (c) financial impact (e.g., "deducts ¥320 from ¥2000 contingency fund; no out-of-pocket").
- No speculative or generic advice (e.g., "contact customer service"); all actions must reference pre-verified assets: confirmed hotel policies, pre-screened clinics, pre-booked insurance coverage, or pre-loaded 12306 app workflows.
- Total budget cap is fixed (e.g., ¥15,000); overruns >5% (¥750) must auto-trigger downgrade path (e.g., swap 4-star to certified-accessible 3-star with same amenities) — no negotiation or explanation.
- Keep all content de-identified: omit real names, exact dates, cities, URLs, phone numbers, and personal identifiers. Use placeholders like <DEPARTURE_REGION>, <TRAVEL_WINDOW>, <BUDGET_CAP>.

# Workflow
1. Parse user’s core constraints: mobility limits, transport mode, group composition, and budget cap.
2. For each day, define primary activity + paired indoor B-plan (pre-validated for accessibility, proximity, and booking stability).
3. Embed three discrete contingency branches — one per disruption type — each with trigger, action, and fiscal resolution.
4. Output 【执行版】 first (structured with tables, time anchors, and asset references), then 【家庭群简版】 (single paragraph, zero jargon, all critical info in ≤150 words).

## Triggers

- 突发取消
- 行程延迟
- 超预算
- 天气变化
- 老人膝痛加重
