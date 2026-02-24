---
id: "09c6ee3c-5660-4039-931c-39e4b87a632b"
name: "family-travel-weather-contingency-planning"
description: "Generates dual-format weather-resilient travel plans for multi-generational families: a detailed execution version for planners and a simplified, actionable version for family group chat — both embedding indoor activity alternatives and real-time rail ticket modification protocols aligned with mobility needs and weather triggers."
version: "0.1.2"
tags:
  - "family-travel"
  - "contingency"
  - "accessibility"
  - "rail-travel"
  - "weather-resilience"
  - "multi-format-output"
triggers:
  - "if rain forecast exceeds 80%"
  - "if thunderstorm warning issued"
  - "if itinerary disrupted by weather"
  - "need indoor backup plan"
  - "how to change高铁 tickets last minute"
---

# family-travel-weather-contingency-planning

Generates dual-format weather-resilient travel plans for multi-generational families: a detailed execution version for planners and a simplified, actionable version for family group chat — both embedding indoor activity alternatives and real-time rail ticket modification protocols aligned with mobility needs and weather triggers.

## Prompt

# Goal
Produce two parallel outputs for a 6-day multi-generational family trip (2 adults + 1 senior with mobility limits + 1 child): (1) an **Execution Version**, containing full operational detail (timings, accessibility specs, rail modification pathways, hotel weather-clause terms, budget line items); and (2) a **Family Group Chat Version**, distilled into 6–8 scannable bullet points using plain language, emoji, and concrete micro-actions — suitable for direct sharing in WeChat/WhatsApp.

# Constraints & Style
- Both versions must embed *identical* weather-resilience logic: for each outdoor activity, pre-identify ≥2 indoor alternatives meeting all of: wheelchair/stroller accessibility, climate control, no stairs, <50m indoor walking, available seating/rest zones, seated engagement for elders, child-friendly duration/stimulation, and ≤20-min transit from accommodation.
- Indoor alternatives must require zero pre-booking or ID beyond standard rail pass/ticket, and fit within the originally scheduled 3.5-hour morning or afternoon block (excluding fixed 2h lunch/nap).
- Execution Version must include: step-by-step rail rebooking guidance (target G/D/C trains, minimum advance notice, fee-free change windows, station-based assistance contacts), official policy references (e.g., '12306 Late Flex Policy'), hotel weather-clause terms (e.g., free room extension), and pre-allocated contingency budget line items totaling ≤¥15,000.
- Family Group Chat Version must omit all technical terms (e.g., '12306', 'proration'), use only concrete actions ('Tap this link to reschedule train → [short URL]', 'Ask front desk for free quiet room at 1pm'), highlight *who does what*, avoid uncertainty markers ('might', 'could', 'possibly'), be card-style and phonetically readable (short lines, no nested clauses), front-load key info (dates, total cost, accommodation names + 3 accessibility features), and include explicit weather response cues (e.g., '群内发「下雨」→ 我秒发定位+预约码').
- Both versions must share identical core mobility constraints: max 600m/day flat-surface walking, zero unavoidable stairs/steep slopes, mandatory 2h midday rest block, all transport pre-arranged or pre-vetted for wheelchair/child stroller access, and indoor alternatives located ≤1km from each outdoor site with verified accessibility (ramps, AC, seating, nursing/child zones).
- Neither version may reference specific cities, dates, budgets, vendors, or personal identifiers — use placeholders: <DEPARTURE_CITY>, <TRAVEL_PERIOD>, <ELDER_MOBILITY_NEED>, <CHILD_AGE_RANGE>, <DESTINATION>, <DATES>, <BUDGET>, <HOTEL_NAME>.
- Output only the two components — no intros, summaries, or markdown headers.
- Language: Execution Version = professional, precise, audit-ready; Family Version = warm, directive, reassuring, imperative, action-oriented; avoid adjectives and fluff.

# Workflow
1. Identify the day’s original outdoor activity category (e.g., cultural site, nature park, historic town).
2. Select indoor alternatives that preserve thematic continuity and satisfy all five accessibility + comfort criteria.
3. Map rail modification options to three weather scenarios: (a) pre-departure disruption, (b) in-destination daily disruption, (c) mid-trip truncation — citing confirmed policy names.
4. Generate Execution Version as Day-by-Day table + Appendix (Hotel Terms, Rail Policy Cheat Sheet, Budget Breakdown).
5. Generate Family Group Chat Version using ✅/⚠️/📍 emojis, active voice, and embedded micro-actions (e.g., '📲 Save this number: +86-XXX for same-day train help').

## Triggers

- if rain forecast exceeds 80%
- if thunderstorm warning issued
- if itinerary disrupted by weather
- need indoor backup plan
- how to change高铁 tickets last minute
