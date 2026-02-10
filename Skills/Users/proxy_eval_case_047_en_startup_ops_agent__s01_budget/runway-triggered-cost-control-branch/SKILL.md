---
id: "1eab2513-8210-48c4-be6a-a42f70ca1af2"
name: "runway-triggered-cost-control-branch"
description: "A time-boxed, role-allocated cost-control protocol that activates automatically when verified runway falls below a predefined threshold (e.g., 5 months), with explicit triage, reversible control-mode levers, and objective exit criteria — integrated into weekly financial review rituals."
version: "0.1.1"
tags:
  - "finance"
  - "runway"
  - "cost-control"
  - "startup-ops"
  - "threshold-trigger"
  - "startup-governance"
triggers:
  - "runway drops below 5 months"
  - "trigger cost control"
  - "activate cost-control protocol"
  - "runway alert"
  - "financial safety trigger"
---

# runway-triggered-cost-control-branch

A time-boxed, role-allocated cost-control protocol that activates automatically when verified runway falls below a predefined threshold (e.g., 5 months), with explicit triage, reversible control-mode levers, and objective exit criteria — integrated into weekly financial review rituals.

## Prompt

# Goal
Automatically trigger and execute a standardized cost-control operational branch when the startup's verified weekly runway drops below 5.0 months — ensuring rapid, transparent, reversible, and pre-approved financial mitigation without founder deliberation delay or custom tooling.

# Constraints & Style
- Runway must be recalculated weekly using verified cash balance and net monthly burn (including payroll, tools, contracts, and founder compensation).
- Trigger is strictly event-based: activation occurs *only* upon confirmed, owner-posted runway value < 5.0 months in the weekly dashboard update (e.g., `❗ Alert: Runway = [4.9] months`).
- Threshold is strict and non-negotiable: "below 5 months" means ≤4.9 months; no rounding or subjective interpretation.
- The cost-control branch must contain *only* pre-vetted, reversible actions — no hiring freezes, layoffs, or vendor terminations unless separately approved in a dedicated decision forum.
- Must include three distinct, time-bound phases: (1) same-day 15-min Triage Huddle (Founder + Finance + People + Product), (2) up-to-4-week Control Mode with four defined levers (hiring freeze, tooling audit, contractor review, marketing pause), each assigned to a single named owner with hard deadline (24h–72h) and one explicit guardrail, and (3) mandatory weekly 10-min Runway Check-In surfacing only three prescribed questions.
- Exit requires *all three* conditions: (a) runway ≥ 5.5 months, (b) at least one lever action fully closed (e.g., tool canceled, contract terminated), and (c) team sync includes a 2-min 'Win & Learn' reflection.
- Output must be binary and unambiguous: either "✅ Cost-control branch inactive" or "🚨 Cost-control branch ACTIVATED — executing [Action List]."
- All activation logic, assignments, deadlines, guardrails, and exit validation must be documented live in the public Decisions Log.
- Output language must be directive, unambiguous, and action-oriented — avoid explanatory framing or motivational phrasing.
- Never invent thresholds, durations, roles, or levers beyond those user-specified (e.g., 5-month trigger, 5.5-month exit, Founder-led triage, People/Finance/Product/GTM owners).

# Workflow
1. During weekly runway check (owned by Founder or Finance Lead), compare updated runway value against 5-month threshold using verified data.
2. If runway < 5.0 months:
   a. Post immediate alert in team channel: "🚨 Cost-control branch ACTIVATED — executing [Action List]."
   b. Initiate Phase 1: Schedule 15-min Triage Huddle (Founder + Finance + People + Product) same day; constrain agenda to cash-in/out facts and top 2 levers.
   c. Launch Phase 2: Assign lever actions with owners, deadlines, and guardrails — enforce strict start timing (next business day). Levers are: • Pause all non-essential SaaS subscriptions (> $50/mo) effective next billing cycle. • Freeze all non-critical marketing spend (e.g., paid ads, sponsorships) for 30 days. • Require dual approval (Founder + Finance Lead) for any new expense > $250. • Conduct tooling audit (Finance) and contractor review (People) within 72h, each with one explicit guardrail.
   d. Log activation timestamp, runway value, and executed actions in Decisions Log.
3. Run Phase 3: Every Monday, surface only the three prescribed questions in #runway channel; require dollar/FTE-week quantification and updated runway number.
4. Re-evaluate status weekly until all three exit criteria are met — then post "✅ Cost-control branch deactivated."

## Triggers

- runway drops below 5 months
- trigger cost control
- activate cost-control protocol
- runway alert
- financial safety trigger
