---
id: "9b12f295-6e42-484f-98ed-ba2b292e9eb3"
name: "runway-triggered-cost-control-protocol"
description: "A time-boxed, three-phase operational protocol that activates automatically when a startup's cash runway falls below a predefined threshold, initiating reversible cost-containment actions, leadership reviews, and exit criteria — all while preserving team stability, operational reversibility, and cadence integration."
version: "0.1.2"
tags:
  - "finance"
  - "operational-cadence"
  - "startup"
  - "risk-mitigation"
  - "threshold-trigger"
  - "cost-control"
  - "startup-governance"
  - "crisis-protocol"
triggers:
  - "runway drops below threshold"
  - "cash runway under threshold"
  - "activate cost-control protocol"
  - "trigger financial containment protocol"
---

# runway-triggered-cost-control-protocol

A time-boxed, three-phase operational protocol that activates automatically when a startup's cash runway falls below a predefined threshold, initiating reversible cost-containment actions, leadership reviews, and exit criteria — all while preserving team stability, operational reversibility, and cadence integration.

## Prompt

# Goal
Automatically trigger a cost-control operational protocol when cash runway drops below <RUNWAY_THRESHOLD> months — shifting focus from growth execution to financial sustainability, with pre-defined actions, ownership, timelines, and escalation paths.

# Constraints & Style
- Must activate *only* when runway < <RUNWAY_THRESHOLD> months (calculated as <CASH_BALANCE> ÷ <MONTHLY_BURN>, using conservative assumptions).
- Must not require manual interpretation: the threshold is binary and objective — no 'soft' triggers like 'runway trending down' or 'budget variance'.
- Output must include exactly two components: (1) a concise **Stakeholder Summary** (≤150 words) explaining the binary trigger, three phases (🔍 Diagnose, 🛠️ Act, 📈 Assess & Reset), core tenets (time-boxing, reversibility within <REVERSIBILITY_HOURS>h, no layoffs or equity changes, transparency, cadence integration), and role-specific responsibilities; and (2) an executable **Executor View** in tabular Markdown format with columns: # | Action | Owner | Deadline | Status (☐/✅) | Notes — containing exactly three rows, one per phase, with parameterized durations (<DIAGNOSE_DAYS>, <ACT_DAYS>, <ASSESS_DAYS>) and concrete, observable actions (e.g., 'publish Expense Heatmap', 'freeze contractor onboarding', 'sign Cost-Control Pact').
- Avoid generic advice (e.g., 'review expenses'); specify *which* expense categories are in scope (e.g., contractors, SaaS tools, travel) and *who owns* each action.
- Strictly exclude: layoffs, equity compensation changes, fundraising tactics, or product roadmap changes.
- All actions must be reversible within <REVERSIBILITY_HOURS> hours; explicitly reflect that constraint in both views.
- Include mandatory cross-cutting requirements: Founder must send transparent internal update within 24h of trigger; document key assumptions; integrate outputs into existing cadence (e.g., Weekly Sync, MBR).
- Do not embed company-specific data (e.g., actual cash amounts, vendor names, team structure); use placeholders like <CURRENT_RUNWAY>, <CASH_BALANCE>, <MONTHLY_BURN>, <RUNWAY_THRESHOLD>, <DIAGNOSE_DAYS>, <ACT_DAYS>, <ASSESS_DAYS>, <REVERSIBILITY_HOURS>.
- Language must be directive, plain English, and executable — suitable for inclusion in an operating playbook or Notion automation.

# Workflow
1. Detect: Compare latest calculated runway against <RUNWAY_THRESHOLD>-month threshold.
2. Confirm: Validate input data sources (cash balance from accounting tool; burn from reconciled P&L).
3. Activate: Surface the cost-control protocol — first the Stakeholder Summary, then the Executor View.
4. Escalate: Notify Founder, Finance Lead, and Cadence Owner via pre-configured channel (e.g., Slack alert).

## Triggers

- runway drops below threshold
- cash runway under threshold
- activate cost-control protocol
- trigger financial containment protocol
