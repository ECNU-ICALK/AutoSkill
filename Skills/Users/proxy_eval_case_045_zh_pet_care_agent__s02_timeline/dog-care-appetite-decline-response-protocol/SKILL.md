---
id: "5e625ce2-a398-4d14-9394-81f5ba951791"
name: "dog-care-appetite-decline-response-protocol"
description: "A reusable protocol for escalating veterinary care when a dog exhibits appetite decline, integrated into routine weekly care tracking."
version: "0.1.0"
tags:
  - "pet-care"
  - "health-monitoring"
  - "clinical-escalation"
  - "protocol"
triggers:
  - "appetite drop"
  - "dog not eating"
  - "refusing food"
  - "weight loss + low appetite"
  - "when to take dog to vet for not eating"
---

# dog-care-appetite-decline-response-protocol

A reusable protocol for escalating veterinary care when a dog exhibits appetite decline, integrated into routine weekly care tracking.

## Prompt

# Goal
Automatically trigger a tiered clinical escalation response when a dog's appetite decline is observed during routine weekly care (e.g., in feeding logs or behavioral notes), ensuring timely intervention before deterioration.

# Constraints & Style
• Must be triggered *only* by documented appetite decline — not subjective concern alone. Documentation must include at least two of: reduced food intake (<80% usual amount), skipped meals (≥1 full meal missed), or persistent refusal despite hand-feeding/food warming.
• Escalation is time-bound and severity-tiered:
  - Tier 1 (Same day): If appetite decline occurs *with* ≥1 red-flag symptom (lethargy, vomiting, diarrhea, pale gums, or >5% weight loss in 7 days) → contact vet immediately.
  - Tier 2 (Within 24h): If appetite decline persists for ≥2 consecutive days *without* red flags → schedule vet consult within 24 hours.
  - Tier 3 (Within 48h): If appetite decline occurs *after* recent vaccination, medication start, or environmental change (e.g., travel, new pet) → vet consult within 48 hours to rule out iatrogenic or stress-related causes.
• Never delay escalation for 'waiting to see' — all tiers require documented action (call log, appointment timestamp, or clinical note).
• Weight record must be cross-referenced: any ≥0.5kg drop from baseline in ≤7 days automatically activates Tier 1, regardless of other symptoms.
• Output must produce a clear, dated escalation decision (e.g., "Tier 2 activated: 2024-06-15 → Vet consult scheduled for 2024-06-16 at 10:00") — no open-ended advice.

# Workflow
1. Review latest feeding log and weight record.
2. Confirm documentation meets one of the appetite decline criteria above.
3. Screen for co-occurring red-flag symptoms or contextual triggers.
4. Apply tier logic based on duration, severity, and context.
5. Generate time-bound action with explicit deadline and required output format.

## Triggers

- appetite drop
- dog not eating
- refusing food
- weight loss + low appetite
- when to take dog to vet for not eating
