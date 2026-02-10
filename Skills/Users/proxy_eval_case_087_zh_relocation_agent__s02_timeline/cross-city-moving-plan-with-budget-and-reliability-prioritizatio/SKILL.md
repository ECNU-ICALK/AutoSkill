---
id: "dc79ab92-e82f-4fed-927c-311efc53b364"
name: "cross-city-moving-plan-with-budget-and-reliability-prioritization"
description: "Generates a time-bound, phase-structured cross-city moving plan that enforces a hard budget ceiling and prioritizes vendor/service reliability over cost savings."
version: "0.1.0"
tags:
  - "moving-plan"
  - "budget-constraint"
  - "vendor-reliability"
  - "administrative-process"
  - "time-phased"
triggers:
  - "生成跨城搬家计划"
  - "制定6周搬家时间表"
  - "预算5万以内搬家方案"
  - "优先选稳定可靠的搬家公司"
  - "跨市搬家如何控制总成本"
---

# cross-city-moving-plan-with-budget-and-reliability-prioritization

Generates a time-bound, phase-structured cross-city moving plan that enforces a hard budget ceiling and prioritizes vendor/service reliability over cost savings.

## Prompt

# Goal
Generate a 6-week cross-city moving plan (domestic, no international logistics) that strictly respects a user-specified total budget上限 (e.g., ≤¥50,000), and explicitly prioritizes stability, track record, and service guarantees — not lowest price — when selecting vendors (e.g., movers), utilities providers, or administrative channels.

# Constraints & Style
- Must embed budget enforcement: all cost estimates (moving, packing, temporary housing, utility deposits, address update fees) must sum to ≤ the stated cap; flag any high-risk line items that could breach it.
- Must apply reliability filters: for each vendor-dependent task (e.g., hiring movers, booking utilities), recommend only platforms or providers with verifiable regulation (e.g., licensed搬家公司 with insurance), official integration (e.g., government-backed utility portals), or documented consumer trust (e.g., State Administration for Market Regulation registration).
- Never suggest unvetted individuals, cash-only services, or platforms without dispute resolution.
- Output must be structured by week, with clear 'What', 'When', and 'How to verify reliability' for each action.
- Use neutral, actionable language — no motivational phrasing ('you got this!'), no generic tips without policy grounding.
- Exclude all one-off personal details (names, cities, pet/baby specifics) unless provided as placeholders (<ORIGIN_CITY>, <DESTINATION_CITY>, <FAMILY_COMPOSITION>).

# Workflow
1. Parse user’s stated budget cap and reliability priority as non-negotiable constraints.
2. For each of the four core domains — housing search, moving service selection, utility migration (water/electricity/gas), and official address updates — identify:
   a) Earliest feasible start week,
   b) Minimum verification steps required to confirm provider reliability,
   c) Budget-impacted sub-tasks (e.g., 'gas safety inspection fee') with estimated cost range.
3. Assemble weekly phases, ensuring reliability checks precede commitment and budget headroom is preserved until final execution week.

## Triggers

- 生成跨城搬家计划
- 制定6周搬家时间表
- 预算5万以内搬家方案
- 优先选稳定可靠的搬家公司
- 跨市搬家如何控制总成本
