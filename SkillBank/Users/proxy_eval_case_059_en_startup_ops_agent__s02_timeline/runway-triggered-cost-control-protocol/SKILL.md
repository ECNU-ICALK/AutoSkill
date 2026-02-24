---
id: "25c9309b-b7cf-4144-ad23-f54a0598c420"
name: "runway-triggered-cost-control-protocol"
description: "Automatically initiates and executes a time-compressed, role-anchored cost-control protocol when a startup's cash runway falls to ≤5.0 months — producing a decision-ready leadership summary and a concise, deadline-bound execution checklist with non-removable steps, integrated into existing operational cadence without new meetings or committees."
version: "0.1.2"
tags:
  - "financial governance"
  - "startup operations"
  - "risk response"
  - "runway management"
  - "cost control"
  - "cadence-integration"
triggers:
  - "runway drops below 5 months"
  - "trigger cost control"
  - "runway < 5 months"
  - "activate cost-control branch"
  - "cash runway critical"
---

# runway-triggered-cost-control-protocol

Automatically initiates and executes a time-compressed, role-anchored cost-control protocol when a startup's cash runway falls to ≤5.0 months — producing a decision-ready leadership summary and a concise, deadline-bound execution checklist with non-removable steps, integrated into existing operational cadence without new meetings or committees.

## Prompt

# Goal
Trigger and execute a standardized cost-control protocol when cash runway drops to ≤5.0 months — producing a leadership summary (concise, decision-ready) and an execution checklist (role-specific, time-bound, with non-removable steps marked).

# Constraints & Style
- Must trigger *only* when runway ≤ 5.0 months (calculated as current cash balance ÷ monthly net burn); validation requires timestamped source link.
- Output must include exactly two sections: "Leadership Summary" (≤5 sentences, plain English, no jargon) and "Execution Checklist" (Markdown table with columns: #, Action, Owner(s), Deadline, Verification).
- Leadership Summary must state: (1) confirmation of trigger condition met, (2) immediate status change (e.g., 'Cost-Control Branch activated'), (3) top 3 priority levers, (4) hiring policy update, and (5) exit criteria (e.g., runway ≥5.5 months).
- Execution Checklist must contain exactly five non-removable actions, each prefixed with "🔒": (1) verify runway ≤5.0 months using latest finance report, (2) issue public spend freeze notice, (3) publish top 3 cost levers with savings estimates and owners, (4) update hiring pipeline with `⏸️ CC-BRANCH` and `✅ REVENUE-CRITICAL` tags, (5) reset Weekly Pulse agenda to lead with "Cost-Control Progress".
- All deadlines must be absolute and compressed: every action completed within 48 hours of trigger confirmation; use precise phrasing (e.g., 'Same day', 'Within 48 hrs') — no multi-day allowances.
- Do not invent new cost measures, thresholds, roles, revenue targets, adoption metrics, tool names, or organizational entities; use placeholders like <REVENUE_THRESHOLD>, <ADOPTION_METRIC>, or <BUDGET_CAP> if referenced.
- Never delay, soften, or qualify the trigger — treat ≤5.0 months as binary, urgent, and non-negotiable.
- Use plain, directive language — no explanations, caveats, scenario analysis, or optional items in output.
- No markdown beyond required table syntax; no emojis except those explicitly required (🔒, ⏸️, ✅).
- All content must be actionable by leadership without external context.

# Workflow
1. Verify runway value from latest validated, timestamped data source (e.g., finance report or Notion dashboard).
2. Compare against threshold (5.0 months).
3. If threshold breached: generate Leadership Summary and Execution Checklist as defined.
4. If not breached: output null (no action).

## Triggers

- runway drops below 5 months
- trigger cost control
- runway < 5 months
- activate cost-control branch
- cash runway critical
