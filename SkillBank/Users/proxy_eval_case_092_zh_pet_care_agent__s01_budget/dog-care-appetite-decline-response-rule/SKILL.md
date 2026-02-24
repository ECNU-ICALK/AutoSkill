---
id: "98c4024c-0b9c-4655-8114-ea3df2985403"
name: "dog-care-appetite-decline-response-rule"
description: "A reusable, evidence-informed clinical escalation protocol for canine appetite decline that converts objective observations into time-bound, actionable veterinary referral criteria — preserving diagnostic sensitivity and urgency while supporting cost-efficient implementation."
version: "0.1.1"
tags:
  - "pet-health"
  - "clinical-escalation"
  - "canine-care"
  - "veterinary"
  - "clinical-protocol"
triggers:
  - "appetite dropped"
  - "not eating well"
  - "skipped meals"
  - "eating less than usual"
  - "refusing food"
---

# dog-care-appetite-decline-response-rule

A reusable, evidence-informed clinical escalation protocol for canine appetite decline that converts objective observations into time-bound, actionable veterinary referral criteria — preserving diagnostic sensitivity and urgency while supporting cost-efficient implementation.

## Prompt

# Goal
Automatically apply a standardized, evidence-informed clinical escalation rule when a dog shows reduced appetite, converting subjective observation into time-bound, actionable veterinary referral criteria.

# Constraints & Style
• MUST trigger only when appetite decline is observed for **≥2 consecutive meals** (e.g., skips breakfast AND dinner, or eats <50% of usual portion at two meals). 
• MUST NOT rely on owner judgment alone: require objective corroboration — either (a) documented food intake (grams/portion consumed), OR (b) concurrent symptom from this list: lethargy, vomiting, diarrhea (>1 episode), oral lesions, or new lip-licking/salivation. 
• MUST escalate to "contact veterinarian today" if both conditions are met: (i) ≥2 missed/substantially reduced meals, AND (ii) ≥1 corroborating sign. 
• MUST downgrade to "monitor closely" (no vet contact yet) if only 1 reduced meal occurs, even with mild signs — unless the dog is geriatric (≥7 years), diabetic, or has known chronic disease (then treat as urgent). 
• NEVER suggest home remedies (e.g., warming food, adding broth) as alternatives to assessment — those may be added *only after* veterinary clearance. 
• Output must state the rule unambiguously in active voice, using plain terms (e.g., "Contact your veterinarian today" not "Consider consulting...").
• Cost reduction is permitted *only* via substitution of non-diagnostic, non-essential tools (e.g., generic thermometer for branded; laminated digital gum-color reference for printed card); thresholds, time windows, symptoms, and action logic MUST remain unchanged.
• All placeholders (e.g., <DAILY_FOOD_GRAM>, <VET_PHONE>) remain intact — do not fill or infer.

## Triggers

- appetite dropped
- not eating well
- skipped meals
- eating less than usual
- refusing food
