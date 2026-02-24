---
id: "03b8ddf5-1943-4a96-8854-029d3fe5e436"
name: "dog-care-escalation-rule-for-appetite-decline"
description: "Applies a time-bound, objective-based clinical escalation rule when a dog shows reduced appetite, triggering specific documentation and timely veterinary consultation."
version: "0.1.0"
tags:
  - "pet-health"
  - "clinical-escalation"
  - "care-policy"
  - "dog-care"
triggers:
  - "appetite drop in dog"
  - "when to call vet for loss of appetite"
  - "dog not eating for two days"
  - "appetite decline escalation protocol"
  - "red flags for canine anorexia"
---

# dog-care-escalation-rule-for-appetite-decline

Applies a time-bound, objective-based clinical escalation rule when a dog shows reduced appetite, triggering specific documentation and timely veterinary consultation.

## Prompt

# Goal
Generate a clear, actionable escalation protocol to be embedded in dog care plans or handover documents, specifying when and how to respond to appetite decline — including mandatory observation window, quantifiable thresholds, required documentation, and defined veterinary referral criteria.

# Constraints & Style
- Must define a strict 48-hour observation window: if appetite decline persists ≥48 hours, escalate immediately.
- Must require objective documentation: number of missed meals (≥2 consecutive), portion reduction percentage (≥30% for ≥2 meals), or complete anorexia (0 intake for ≥12 hours).
- Must mandate concurrent monitoring of at least two co-occurring red-flag symptoms: lethargy, vomiting, diarrhea, excessive panting, or abnormal gum color.
- Must prohibit subjective interpretations (e.g., 'seems less interested') — only observable, recordable behaviors qualify.
- Must specify that escalation includes: (1) contacting veterinarian *before* the 48-hour mark if red flags are present, and (2) sharing documented observations (not just impressions) during consultation.
- Must exclude generic advice (e.g., 'offer tasty food') — focus solely on decision logic and action triggers.
- Output must be self-contained, de-identified, and usable across any dog care context (home, boarding, pet-sitting).

# Workflow
None — this is a policy rule, not a multi-step procedure. Do not invent steps beyond the defined trigger-action-response structure.

## Triggers

- appetite drop in dog
- when to call vet for loss of appetite
- dog not eating for two days
- appetite decline escalation protocol
- red flags for canine anorexia
