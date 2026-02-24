---
id: "695871b5-655e-45d4-9d6d-699c91ce3743"
name: "weekly-leadership-checkpoint-execution"
description: "A concise, time-boxed weekly execution protocol for leadership teams to validate operational health across four pillars (hiring, runway, support, releases) and trigger predefined actions — especially cost-control tiers — based on objective, pre-defined thresholds."
version: "0.1.0"
tags:
  - "leadership"
  - "operational-rhythm"
  - "threshold-triggered"
  - "execution-checklist"
  - "four-pillar-tracking"
triggers:
  - "output leadership summary and execution checklist"
  - "generate weekly leadership checkpoint"
  - "make it concise actionable checkpoint-complete"
  - "final version must be concise actionable and checkpoint-complete"
---

# weekly-leadership-checkpoint-execution

A concise, time-boxed weekly execution protocol for leadership teams to validate operational health across four pillars (hiring, runway, support, releases) and trigger predefined actions — especially cost-control tiers — based on objective, pre-defined thresholds.

## Prompt

# Goal
Generate a concise, actionable, and checkpoint-complete leadership summary and execution checklist for a weekly leadership review. It must reflect the current state of four pillars (hiring, runway, support, releases), surface cross-pillar tensions, and enforce immediate, threshold-triggered actions — especially the Runway <5 Months Cost-Control Branch — with no ambiguity on ownership, timing, or completion criteria.

# Constraints & Style
- Output must be strictly limited to two sections: (1) a one-page Leadership Summary (table format: Dimension / Current State / Leadership Imperative / Signal of Success) and (2) an Execution Checklist (numbered, owner-assigned, with Done? column).
- All content must be de-identified: no names, roles, tools (e.g., Notion/Sheets), dates, or business-specific metrics beyond the invariant thresholds (e.g., "<5 months", ">24h", ">2 weeks", "≥3x").
- Use only objective, observable conditions as triggers — never subjective judgments (e.g., "spiking", "slipping") unless derived from defined thresholds.
- Every checklist item must be verifiably complete by EOD Friday; no open-ended or aspirational items.
- No explanations, rationale, or bonus offers — only the summary and checklist.
- Language must be imperative, third-person, and decision-oriented (e.g., "Confirm all pillar dashboards are updated", not "You should confirm...").
- Never include placeholders like <TOKEN> or markdown formatting instructions.

# Workflow
1. Extract the current status of each of the four pillars using only objectively measurable checkpoint conditions (e.g., runway ≤5.0 months, unresolved urgent tickets >24h, milestones marked 🟡/🔴, roles >2 weeks without qualified candidates).
2. Identify exactly one cross-pillar tension implied by simultaneous checkpoint failures (e.g., release delay → support load increase → hiring freeze triggered).
3. Apply the Runway <5 Months Cost-Control Branch logic: if true, include Tier 1 activation as a mandatory checklist item.
4. Populate the Leadership Summary table using only invariant dimensions and their universally applicable imperatives and success signals.
5. Populate the Execution Checklist with exactly five numbered, owner-assigned, binary (✅/❌) items — all scoped to completion by EOD Friday and grounded in checkpoint logic.

## Triggers

- output leadership summary and execution checklist
- generate weekly leadership checkpoint
- make it concise actionable checkpoint-complete
- final version must be concise actionable and checkpoint-complete
