---
id: "d9946a86-fbf3-4f49-a029-cac984f07314"
name: "startup-runway-triggered-cost-control-protocol"
description: "A policy-driven operational rule that automatically initiates a predefined cost-control protocol when a startup's cash runway falls below 5 months, ensuring timely, consistent, and pre-vetted financial discipline without ad-hoc deliberation or leadership override."
version: "0.1.2"
tags:
  - "runway"
  - "cost-control"
  - "startup-finance"
  - "operational-policy"
  - "threshold-trigger"
  - "financial-governance"
triggers:
  - "runway drops below 5 months"
  - "trigger cost control"
  - "activate cost-control branch"
  - "runway under 5 months"
  - "financial trigger threshold"
---

# startup-runway-triggered-cost-control-protocol

A policy-driven operational rule that automatically initiates a predefined cost-control protocol when a startup's cash runway falls below 5 months, ensuring timely, consistent, and pre-vetted financial discipline without ad-hoc deliberation or leadership override.

## Prompt

# Goal
Automatically trigger a cost-control protocol (i.e., a set of pre-defined, executable actions and decision gates) when the startup's calculated cash runway drops below 5 months — without requiring ad-hoc deliberation or leadership override.

# Constraints & Style
- Must trigger *immediately* upon confirmation of runway < 5 months (e.g., during Weekly Leadership Pulse or via automated alert).
- The protocol must be pre-defined, lightweight, and executable by the CEO/Finance Lead with no new approvals needed.
- Must include at minimum: (1) pause on all non-critical hiring, (2) freeze on discretionary spend (> $250), (3) 48-hour review window to assess runway recovery options (e.g., accelerate revenue, extend fundraising timeline, renegotiate contracts).
- Output must be unambiguous: either "RUNWAY OK" or "COST-CONTROL PROTOCOL ACTIVATED" + list of 3 immediate actions.
- Output exactly two sections: "Leadership Summary" (concise, narrative, ≤150 words, CEO-facing tone, plain text only — no tables, markdown, emojis, or bullet symbols; use "-" for lists) and "Execution Checklist" (≤6 items, each as a single-line sentence, time-bound, owner-assigned).
- All actions must map to roles already defined: CEO, Hiring Manager, Finance/CEO, Ops Lead, Product/Eng Lead — no new roles.
- Use only the confirmed activation condition: *runway < 5 months* — no other metrics or thresholds.
- Use placeholders like [current runway], [date], [list exempt roles], <CRITICAL_ROLE>, <REVENUE_CATALYST>, or <CORE_FEATURE> — never invent values.
- Avoid speculative, emotional, or promotional language (e.g., no phrases like "you've got this", "not emergency mode", or "operational precision").
- Exclude tooling specifics (Notion/Sheets), templates, scripts, calculators, optional paths, or unconfirmed guardrails (e.g., layoff rules not reaffirmed by user); retain only confirmed guardrails: no layoffs without ≥2 weeks of revenue shortfall data; no cuts to support/core eng/security; all actions logged in Decision Log.
- Keep language action-oriented, de-identified, and reusable.

## Triggers

- runway drops below 5 months
- trigger cost control
- activate cost-control branch
- runway under 5 months
- financial trigger threshold
