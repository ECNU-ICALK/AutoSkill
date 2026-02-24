---
id: "8437b378-27c1-4231-9008-d283fed690cf"
name: "dog-care-weekly-review-and-adjustment-protocol"
description: "A standardized weekly review and adaptive adjustment protocol for canine care plans, triggered after each 7-day cycle to assess adherence, detect early deviations (e.g., weight drift, appetite trends, behavior shifts), and apply evidence-based rule-based adjustments — applicable to both owner-managed and delegated (e.g., pet-sitting) contexts."
version: "0.1.0"
tags:
  - "pet-care"
  - "data-driven-adjustment"
  - "weekly-review"
  - "rule-based-escalation"
  - "care-plan-maintenance"
triggers:
  - "weekly dog care review"
  - "adjust dog care plan after 7 days"
  - "how to revise pet care schedule based on data"
  - "dog care plan adaptation protocol"
  - "canine care feedback loop"
---

# dog-care-weekly-review-and-adjustment-protocol

A standardized weekly review and adaptive adjustment protocol for canine care plans, triggered after each 7-day cycle to assess adherence, detect early deviations (e.g., weight drift, appetite trends, behavior shifts), and apply evidence-based rule-based adjustments — applicable to both owner-managed and delegated (e.g., pet-sitting) contexts.

## Prompt

# Goal
Generate a time-bound, objective-driven weekly review report for a dog's care plan, comparing observed metrics against baseline targets across five core modules (feeding, walking, grooming, deworming, weight), then apply pre-defined adjustment rules to update the next week’s plan — outputting only the revised action items and rationale.

# Constraints & Style
- Use only quantifiable, recorded data: daily food intake (g), walk duration (min), weight (kg, two decimals), deworming dates, grooming events.
- Baseline targets must be explicitly defined in input (e.g., 'target weight: 5.00 kg', 'target daily intake: 120 g').
- Adjustment rules are mandatory and non-negotiable:
  • Weight change > ±0.3 kg from baseline → trigger feeding volume recalibration: adjust daily intake by ±5 g per 0.1 kg deviation.
  • Two consecutive days with intake < 80% of target → add 'appetite observation' task to next week’s feeding module (include photo + 30-sec video requirement).
  • Missed deworming by >2 days → auto-schedule catch-up dose and flag for vet consult.
  • Walks missed ≥2x/week or <15 min average → reduce next week’s target to 80% and add 'leash retraining note' to walking module.
  • Grooming overdue by >10 days → insert urgent grooming slot (non-delegable if owner-only task).
- Output format: plain Markdown table with columns 'Module', 'Observed Deviation', 'Applied Adjustment', 'Rationale (1 sentence)'. No explanations, no markdown headers beyond # Goal and # Constraints & Style.
- Never invent data; if any metric is missing, state 'MISSING — requires manual input' in that row.
- Language: English only; all placeholders de-identified (e.g., <TARGET_DAILY_INTAKE>, <BASELINE_WEIGHT>).

# Workflow
1. Parse weekly log data (input as structured list or CSV-like text).
2. Compare each module’s observed values against defined baselines and tolerance thresholds.
3. For each deviation that meets an adjustment rule condition, apply the corresponding rule.
4. Compile results into the specified table format — no summary, no recommendations outside the table.

## Triggers

- weekly dog care review
- adjust dog care plan after 7 days
- how to revise pet care schedule based on data
- dog care plan adaptation protocol
- canine care feedback loop
