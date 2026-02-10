---
id: "0fb6740c-ba2a-476d-af97-4d0f874c3248"
name: "runway-triggered-cost-control-protocol"
description: "Automatically initiates a standardized, multi-action cost-control response when a startup's cash runway falls below a configured threshold (e.g., 5 months), producing a leadership summary and an owner-specific execution checklist — not analysis or recommendations."
version: "0.1.2"
tags:
  - "finance"
  - "startup"
  - "runway"
  - "cost-control"
  - "leadership"
  - "execution"
  - "adjustment-rule"
  - "owner-accountability"
triggers:
  - "runway drops below 5 months"
  - "trigger cost control protocol"
  - "runway alert activated"
  - "financial safety trigger"
  - "activate cost-control branch"
  - "runway trigger adjustment"
---

# runway-triggered-cost-control-protocol

Automatically initiates a standardized, multi-action cost-control response when a startup's cash runway falls below a configured threshold (e.g., 5 months), producing a leadership summary and an owner-specific execution checklist — not analysis or recommendations.

## Prompt

# Goal
Trigger the predefined 'Runway < 5 Months' Cost-Control Protocol when weekly runway calculation drops below 5.0 months — outputting exactly two sections: a concise Leadership Summary and an owner-specific Execution Checklist. Output must be executable, not advisory.

# Constraints & Style
- Output exactly two sections: 'Leadership Summary' (3–4 bullet points, executive tone, plain English) and 'Execution Checklist' (tabular, 3 columns: Action | Owner | Deadline).
- Leadership Summary must include: (1) confirmation of trigger, (2) core protective guardrails (no layoffs, no critical release delays, continued customer learning), (3) key activation actions, and (4) objective exit criteria (reach 5.5 months runway OR meet any of: 12% MoM revenue growth, verified expense reduction, secured milestone).
- Execution Checklist must list only three immediate, mandatory, owner-assigned actions to be completed within 24 hours: (1) freeze non-essential hiring, (2) audit and pause ≤2 discretionary SaaS subscriptions, (3) schedule a 60-min Cost Control Review with CEO, Finance Lead, and People Lead.
- Threshold is fixed per cycle (e.g., '5.0 months'); trigger only on objective, updated runway data — never forecasts, estimates, or sentiment.
- No justification, modeling, scenario planning, long-term strategy, comms, templates, formulas, or tooling references.
- Language must be imperative and time-bound (e.g., 'Pause X by EOD tomorrow', 'Schedule Y before Thursday 10 AM').
- Adjustment branches activate automatically on threshold breach (e.g., runway ≤ 4.9 months); no manual approval required.
- Exit criteria require *two consecutive weeks* of达标 plus at least one milestone achievement.
- All outputs must be de-identified: no company names, tool names, role titles beyond functional descriptors (e.g., 'People Lead'), or project-specific goals.

# Workflow
1. Confirm runway value is from the latest weekly update and is < 5.0 months.
2. Generate Leadership Summary using the four invariant elements above.
3. Generate Execution Checklist containing only the three immediate actions with their assigned owners and 'Within 24 hrs' deadline.
4. Output both sections sequentially, with no preamble or follow-up.

## Triggers

- runway drops below 5 months
- trigger cost control protocol
- runway alert activated
- financial safety trigger
- activate cost-control branch
- runway trigger adjustment
