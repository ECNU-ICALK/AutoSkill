---
id: "5af5c584-cd96-4141-90fe-1bd8a7c93d0a"
name: "runway-triggered-cost-control-protocol"
description: "Automatically initiates and enforces a time-bound, action-oriented cost-control protocol when startup cash runway falls below 5 months, producing a leadership summary, an executable owner-assigned checklist with deadlines and binary success criteria, and a strict day-by-day (T+0 to T+24 hrs) activation plan."
version: "0.1.2"
tags:
  - "runway"
  - "cost-control"
  - "financial-governance"
  - "startup-ops"
  - "leadership-reporting"
  - "operational-checklist"
  - "crisis-response"
triggers:
  - "runway drops below 5 months"
  - "cash runway under 5 months"
  - "trigger cost control"
  - "activate fiscal guardrail"
  - "runway alert"
  - "activate cost control"
  - "day-by-day cost control checklist"
  - "24-hour cost control activation plan"
---

# runway-triggered-cost-control-protocol

Automatically initiates and enforces a time-bound, action-oriented cost-control protocol when startup cash runway falls below 5 months, producing a leadership summary, an executable owner-assigned checklist with deadlines and binary success criteria, and a strict day-by-day (T+0 to T+24 hrs) activation plan.

## Prompt

# Goal
Trigger and execute a standardized cost-control protocol upon confirmed runway <5.0 months — producing a concise, decision-ready Leadership Summary, an executable owner-assigned Execution Checklist with deadlines and binary success criteria, and a strict day-by-day (T+0 to T+24 hrs) Activation Plan in table format.

# Constraints & Style
- Must trigger *automatically* upon confirmed runway <5.0 months (calculated from latest cash balance and net burn).
- Output must be strictly three sections: "Leadership Summary" (≤5 bullet points, no jargon; covers risk, immediate actions, and next reassessment deadline), "Execution Checklist" (table: Action | Owner | Deadline | ✅ Done When…), and "Activation Plan" (table: Day/Time | Action | Owner | Done? (☐), using absolute offsets: T+0 hrs, T+2 hrs, ..., T+24 hrs).
- All actions must be concrete, binary (done/not done), and time-bound — use verbs like "freeze", "cancel", "deliver", "flag", "recalculate"; avoid vague terms like "review" or "assess".
- Requires immediate documentation: update the Runway Risk Register with the trigger event, root cause, and first action taken.
- Prohibits new hiring, non-essential tool subscriptions, or travel spend until runway ≥5.5 months *and* a recovery plan is approved by founders.
- All cost-control actions must be time-bound (e.g., "hiring freeze: 30 days, renewable only after revenue review").
- Never invent thresholds, timelines, or roles — only use user-confirmed ones: 5-month trigger, 24-hour immediate actions, 7-day review sprint, twice-weekly runway recalculation until >5 months, and mandatory "Runway Impact Statement" for all new initiatives.
- De-identify all specifics: omit names, dates, dollar amounts, tool names (e.g., say "helpdesk" not "Zendesk"), and product features.
- Tone: calm, authoritative, operational — no motivational language or explanations.
- Output must include: (1) confirmation of trigger, (2) active cost-control measures, (3) owner and deadline for next runway reassessment, (4) T+0 to T+24 hrs activation sequence with role-based owners.
- Activation Plan must be ≤10 rows, exclude any step beyond T+24 hrs, and contain no explanations, summaries, or planning tasks.

# Workflow
1. Monitor weekly runway calculation (from 'Runway' metric tracking).
2. If runway < 5.0 months → immediately flag as 🔴 Red in dashboard and notify founders + finance owner.
3. Generate Leadership Summary covering: (a) Immediate Actions (within 24h), (b) 7-Day Review Sprint deliverables, (c) Ongoing Discipline rules.
4. Generate Execution Checklist by decomposing each phase into discrete, owned, time-bound actions — including "Runway Impact Statement" requirement for all new initiatives, assigned to initiative owner, due before approval.
5. Generate Activation Plan: a fixed, time-anchored table of mandatory actions from T+0 hrs to T+24 hrs, with role-based owners and binary completion criteria.
6. Log trigger and response in Runway Risk Register with timestamp and justification.
7. Schedule mandatory 7-day follow-up: reassess runway projection and measure impact of controls.

## Triggers

- runway drops below 5 months
- cash runway under 5 months
- trigger cost control
- activate fiscal guardrail
- runway alert
- activate cost control
- day-by-day cost control checklist
- 24-hour cost control activation plan
