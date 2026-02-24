---
id: "33721843-4118-413e-843a-a8e280093df5"
name: "tiered-canine-appetite-decline-protocol"
description: "A time-bound, symptom-tiered escalation protocol for canine appetite decline, defining objective mild/moderate/severe thresholds, mandatory concrete actions per tier, strict time-based decision points, and unambiguous handoff criteria between owner and caregiver to veterinary care."
version: "0.1.2"
tags:
  - "pet-care"
  - "health-escalation"
  - "veterinary-triage"
  - "canine"
  - "caregiver-handoff"
  - "time-bound"
triggers:
  - "appetite dropped"
  - "dog not eating"
  - "refusing food"
  - "anorexia protocol"
  - "when to call vet for loss of appetite"
---

# tiered-canine-appetite-decline-protocol

A time-bound, symptom-tiered escalation protocol for canine appetite decline, defining objective mild/moderate/severe thresholds, mandatory concrete actions per tier, strict time-based decision points, and unambiguous handoff criteria between owner and caregiver to veterinary care.

## Prompt

# Goal
Generate two plain-text, copy-paste-ready response versions for canine appetite decline: (1) an 'Owner Daily Use' version for the pet owner’s self-management, and (2) a 'Caregiver Quick-Action' version for non-veterinarian third-party caregivers — both strictly time-triggered, clinically grounded, and free of tables, markdown, bullets, or structural overhead.

# Constraints & Style
• Must define appetite decline quantitatively using three tiers: 🔹 Light (single meal <70% intake but still investigating food), 🔸 Moderate (two consecutive meals refused or <2 bites), 🔺 Severe (complete refusal + ≥1 red-flag sign: vomiting, diarrhea with blood/mucus, pale/dry gums, abdominal pain, or lethargy).
• Must enforce strict, non-negotiable time thresholds: Light → escalate at 12 hours from first deviation; Moderate → escalate at 12 hours from onset; Severe → escalate at 6 hours from first red-flag sign.
• Must specify mandatory concurrent observations: vomiting, diarrhea, lethargy, gum color/moisture, abdominal pain signs, and temperature (via ear thermometer if available).
• Output only two labeled sections: "Owner Daily Use" and "Caregiver Quick-Action", each as a single unformatted paragraph (no line breaks between items, no symbols like •/→/✓, no bold/italics); use only short imperative sentences separated by semicolons.
• All time thresholds must be explicit (e.g., "at 6 hours", "by 12 hours", "if still not eating after 18 hours").
• Must distinguish between 'contact vet' (teleconsult) and 'visit vet' (in-person exam), with explicit triggers for each.
• All actions must be concrete, tool-agnostic, and imperative: e.g., "feed unsalted chicken broth (1:3 meat:water)", "measure ear temperature", "contact vet via video call", "transport to emergency clinic" — no vague language (e.g., "monitor closely", "try again later", "consider bland food") and no diagnostic speculation.
• Omit all explanations, rationale, examples, references, or tool mentions (e.g., no PDFs, QR codes, Excel, videos, or scripts).
• De-identify with placeholders <DOG_BREED>, <DOG_AGE>, <CURRENT_WEIGHT>, <CITY>, <DEPARTURE_DATE> only where required for portability; rules must remain universally applicable to healthy adult dogs.
• Keep total output under 300 words.
• Append a minimal 'Usage Notes' section clarifying: (a) clock starts at first observed deviation, (b) timestamps must be logged in owner's tracker (e.g., 'weight tracker → “Appetite” tab'), and (c) all versions expire after 24h of full refeeding.

## Triggers

- appetite dropped
- dog not eating
- refusing food
- anorexia protocol
- when to call vet for loss of appetite
