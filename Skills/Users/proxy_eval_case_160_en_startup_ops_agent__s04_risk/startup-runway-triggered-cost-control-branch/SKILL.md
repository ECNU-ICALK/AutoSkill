---
id: "cf310d95-f578-4972-a986-8aced684ba42"
name: "startup-runway-cost-control-branch"
description: "A time-bound, tiered operational protocol that activates automatically when a startup's calculated cash runway falls below 5 months, prescribing one of three proportional response paths based on severity and revenue context."
version: "0.1.2"
tags:
  - "cash-runway"
  - "cost-control"
  - "startup-ops"
  - "decision-protocol"
  - "leadership-communication"
  - "risk-mitigation"
triggers:
  - "if runway drops below 5 months"
  - "runway under 5 months trigger"
  - "runway alert response"
  - "activate cost control when cash is low"
  - "startup cost freeze protocol"
---

# startup-runway-cost-control-branch

A time-bound, tiered operational protocol that activates automatically when a startup's calculated cash runway falls below 5 months, prescribing one of three proportional response paths based on severity and revenue context.

## Prompt

# Goal
Generate a leadership summary and execution checklist for the activated cost-control branch when cash runway drops below 5 months — strictly following the defined three-path protocol (Path A: Optimize, Path B: Conserve, Path C: Reset), including confirmation step, path selection criteria, immediate actions, owners, durations, and exit conditions.

# Constraints & Style
- Must trigger *only* when runway < 5.0 months (calculated as: current cash balance ÷ average 3-month net burn).
- Output exactly two sections: "Leadership Summary" (concise, stakeholder-facing, ≤120 words) and "Execution Checklist" (bulleted, action-oriented, owner-assigned, time-bound).
- Leadership Summary must include: current runway value, triggered path name, *one-sentence rationale*, and *first visible action* — no jargon, no ambiguity.
- Execution Checklist must list only concrete, atomic actions — no explanations, no conditionals. Each item must specify: verb + object + owner + deadline (e.g., "Pause all non-revenue-critical hiring — Ops Lead, by EOD tomorrow").
- Include exactly three tiers of actions: (1) Immediate freeze (effective within 24h), (2) 30-day reduction levers (with owner & deadline), (3) 60-day strategic options (to be reviewed by CEO + Finance by EOD next business day).
- Prohibit vague language: every action must name a specific lever (e.g., 'pause all non-contractual agency spend'), owner, and deadline.
- Never invent paths, thresholds, owners, or durations beyond those explicitly defined in the protocol.
- Do not include vendor names, tool names, team size details, budget projections, scenario modeling, or fundraising advice unless explicitly requested in the same turn.
- Use plain English; avoid jargon like 'OPEX optimization' or 'runway extension levers'.
- If runway ≥5 months, output only: "No action required: runway threshold not met."
- Add a third section: "Top-3 Risks & Mitigations" — one sentence per risk/mitigation pair, using only these three validated patterns: (1) freeze non-essential spend, (2) renegotiate high-spend contracts, (3) launch targeted revenue-accelerating tests.
- All placeholders use angle-bracket syntax: <CASH_BALANCE>, <NET_BURN>, <PRIMARY_PRESSURE_DRIVER>, <REVENUE_TREND>, <BURN_TREND>, <PATH_CHOSEN>.
- Never invent root causes, trends, or drivers — leave them as placeholders unless explicitly provided by user.
- Exclude role titles, dates, or team-specific facts — keep fully de-identified and reusable.

## Triggers

- if runway drops below 5 months
- runway under 5 months trigger
- runway alert response
- activate cost control when cash is low
- startup cost freeze protocol
