---
id: "a994479c-7368-412b-9b21-eae92e6074f4"
name: "dog-care-appetite-decline-response-rule"
description: "A reusable clinical escalation protocol that triggers veterinary consultation when a dog exhibits sustained appetite decline, with clear duration, severity, and contextual thresholds."
version: "0.1.0"
tags:
  - "pet-care"
  - "clinical-escalation"
  - "decision-rule"
  - "canine-health"
triggers:
  - "appetite dropped"
  - "not eating well"
  - "refusing food"
  - "dog skipped meals"
  - "low appetite rule"
---

# dog-care-appetite-decline-response-rule

A reusable clinical escalation protocol that triggers veterinary consultation when a dog exhibits sustained appetite decline, with clear duration, severity, and contextual thresholds.

## Prompt

# Goal
Automatically determine whether observed appetite decline in a dog meets pre-defined criteria for urgent veterinary evaluation — producing a binary 'Escalate' or 'Monitor' decision with justification.

# Constraints & Style
• Must apply ONLY to healthy adult dogs (exclude puppies, seniors, or dogs with known chronic conditions unless explicitly stated in input).
• Appetite decline is defined as: reduced food intake (<80% of usual amount) OR complete refusal of meals.
• Escalation is mandatory if ANY ONE of the following holds:
  - Refusal of ≥2 consecutive meals; OR
  - Intake reduced >30% for ≥48 consecutive hours; OR
  - Appetite decline co-occurs with ≥1 red-flag symptom: vomiting, diarrhea (≥2 episodes), lethargy (reduced responsiveness/mobility), or abnormal feces (blood, mucus, black/tarry).
• Do NOT escalate for isolated, transient pickiness (e.g., skipping 1 meal, mild sniffing without eating) without red-flag symptoms.
• Output must be strictly one of two labeled verdicts: "ESCALATE: [brief reason]" or "MONITOR: [brief reason]" — no explanations, suggestions, or extra text.
• Never infer unstated symptoms; rely only on explicitly reported observations.

# Workflow
1. Parse input for: meal count refusal, % intake reduction, duration (in hours), and presence/absence of red-flag symptoms.
2. Evaluate against the three escalation conditions above (OR logic).
3. Return verdict with minimal, factual justification using only confirmed inputs.

## Triggers

- appetite dropped
- not eating well
- refusing food
- dog skipped meals
- low appetite rule
