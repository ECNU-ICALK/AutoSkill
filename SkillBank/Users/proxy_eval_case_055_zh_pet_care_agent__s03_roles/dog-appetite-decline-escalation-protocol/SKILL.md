---
id: "f851bdee-4c7f-4f9c-a66f-26a9b6bb50d4"
name: "dog-appetite-decline-escalation-protocol"
description: "A reusable, evidence-based, tiered clinical decision protocol that triggers veterinary escalation for canine appetite decline — distinguishing normal fluctuation from pathological anorexia — using objective, observable criteria, life-stage adaptations, and executable actions for owners and caregivers."
version: "0.1.1"
tags:
  - "pet-health"
  - "clinical-protocol"
  - "decision-tree"
  - "caregiver-handoff"
  - "preventive-medicine"
triggers:
  - "appetite drop"
  - "dog not eating"
  - "refuses food"
  - "loss of appetite"
  - "when to call vet for appetite loss"
---

# dog-appetite-decline-escalation-protocol

A reusable, evidence-based, tiered clinical decision protocol that triggers veterinary escalation for canine appetite decline — distinguishing normal fluctuation from pathological anorexia — using objective, observable criteria, life-stage adaptations, and executable actions for owners and caregivers.

## Prompt

# Goal
Generate a clear, actionable, tiered veterinary escalation rule for canine appetite decline — to be embedded in pet care plans or handoff documents — that defines *when*, *why*, and *what to do* at each level of concern, based solely on quantifiable, observable criteria.

# Constraints & Style
• Must use only quantifiable, observable criteria: duration (hours/meals), severity (% intake reduction or meal skips), and corroborating signs (e.g., gum color, lip-licking, vomiting, abdominal guarding, respiratory rate, water intake change) — no subjective terms like "seems off" or "a bit quiet".
• Enforce three strict tiers: 🟢 1-level (24h observation with root-cause checklist), 🟡 2-level (48h vet evaluation with vitals check), 🔴 3-level (immediate ER activation).
• Automatically adapt tier thresholds by life stage: for puppies (<6mo) and seniors (>7yo), downgrade latency (e.g., full refusal >12h = 🔴; >24h = 🟡).
• Every tier mandates specific, executable actions — no generic advice (e.g., "measure rectal temp", "photograph gums", "stop all supplements", "withhold food/water", "wrap for transport").
• All instructions must be translatable to non-veterinarians — avoid jargon without immediate plain-language definition (e.g., "gum color" not "mucous membrane pallor").
• Output must be self-contained, de-identified, and generalizable: no assumptions about breed, weight, or preexisting conditions unless user provides them.
• Language: concise, imperative, clinically grounded — suitable for caregiver instructions or digital health tools.

# Workflow
1. At each scheduled feeding, observe and record: amount consumed (% of target), water intake change vs. baseline, and two behavioral anchors (tail movement, eye brightness).
2. If intake falls below 70% for one meal → trigger 🟢 1-level checklist (assess environment, food freshness, stressors).
3. If intake remains <50% for two consecutive meals OR one meal + any red-flag sign (e.g., lip-licking, reduced water, soft stool) → escalate to 🟡 2-level: initiate vitals check and vet contact.
4. If full refusal >24h (or >12h for puppies/seniors) OR refusal + vomiting/abdominal guarding/gum discoloration → activate 🔴 3-level: withhold food/water, wrap for transport, and contact ER.
5. Log all observations in a shared tracker visible to both owner and caregiver.

## Triggers

- appetite drop
- dog not eating
- refuses food
- loss of appetite
- when to call vet for appetite loss
