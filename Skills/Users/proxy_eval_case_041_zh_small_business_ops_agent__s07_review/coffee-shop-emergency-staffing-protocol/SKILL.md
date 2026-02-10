---
id: "b3df51a8-595e-460a-86cd-d6b912ab47bf"
name: "coffee-shop-emergency-staffing-protocol"
description: "A reusable, rule-based, tiered emergency staffing protocol for small coffee shops (2–3 scheduled staff) that activates when scheduled staff are unexpectedly absent, ensuring minimum viable operations while preserving food safety, core service SLAs, and customer trust."
version: "0.1.1"
tags:
  - "staffing"
  - "contingency"
  - "sop"
  - "small-business"
  - "food-service"
triggers:
  - "突发缺人"
  - "应急排班"
  - "staff absent last minute"
  - "紧急替班方案"
  - "咖啡店临时少人"
---

# coffee-shop-emergency-staffing-protocol

A reusable, rule-based, tiered emergency staffing protocol for small coffee shops (2–3 scheduled staff) that activates when scheduled staff are unexpectedly absent, ensuring minimum viable operations while preserving food safety, core service SLAs, and customer trust.

## Prompt

# Goal
Generate a clear, actionable, de-identified emergency staffing response plan for a small coffee shop facing sudden staff shortage — structured in three escalation tiers (yellow/orange/red), each with explicit trigger conditions, time-bound actions, role reallocations, service reductions, and physical/digital safeguards.

# Constraints & Style
- Must be activated only when ≥1 scheduled staff member is confirmed absent <4 hours before shift start; all decisions must be made within ≤5 minutes of confirmation.
- Must be fully executable by existing staff with no external hires or tools; rely only on pre-established skills, labeled roles, and on-site resources.
- Preserve non-negotiables: no solo operation of espresso machine during peak hours; all food safety logs (temperature, cleaning) must still be completed; cash reconciliation remains dual-controlled.
- Prioritize tasks into three tiers:
  • Tier 1 (MUST do): order fulfillment for in-progress tickets, handwashing/station sanitation, temperature logging, cash drop.
  • Tier 2 (DO if capacity allows): prepping next-day ingredients, restocking consumables, responding to non-urgent messages.
  • Tier 3 (PAUSE): non-essential promotions, new menu testing, deep cleaning, staff training.
- All tiers must specify: (1) precise trigger condition, (2) action sequence with ≤5-minute decision window, (3) hard limits on active menu items/services, (4) mandatory visual/physical controls (e.g., printed signage, dedicated storage zones, pre-set POS shortcuts).
- Define clear escalation triggers: if >2 consecutive orders exceed 120s prep time OR >3 customers wait >5 mins, immediately pause new orders and display "Brief Pause — Improving Your Order" sign.
- Prohibit vague terms like 'as needed', 'if possible', or 'try to'. Replace with concrete verbs: 'shut down', 'switch to', 'activate', 'display', 'scan', 'press'.
- Output format: clean Markdown table per tier + bulleted 'preventive prep' list (max 3 items), using only ☕⚡🛡️ icons for visual scannability.
- Use only generic placeholders: <SHIFT_DAY>, <PEAK_HOURS>, <STAFF_COUNT>, <EMERGENCY_MENU_ITEMS>, <SKILL_LEVELS>.
- Tone: directive, calm, operational — no motivational language or explanations of 'why'.
- No brand names, locations, app names, URLs, personal identifiers, dates, or financial figures.

## Triggers

- 突发缺人
- 应急排班
- staff absent last minute
- 紧急替班方案
- 咖啡店临时少人
