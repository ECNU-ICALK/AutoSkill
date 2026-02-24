---
id: "df6a80f0-76e2-45a3-a5a6-f3127a9b0b1c"
name: "dog-care-plan-dual-version-generator"
description: "Generates two parallel, synchronized care checklists — one for daily owner use and one for temporary caregiver handover — both aligned to the same core health modules (feeding, walking, grooming, deworming, weight tracking) and shared escalation rules; optionally compresses the plan to a 7-day critical-path timeline while preserving non-removable steps based on physiological safety, data continuity, and escalation integrity."
version: "0.1.1"
tags:
  - "pet-care"
  - "checklist-generation"
  - "handover-protocol"
  - "health-monitoring"
  - "escalation-rules"
  - "checklist-compression"
  - "risk-prioritization"
triggers:
  - "generate daily and handover checklists"
  - "dual-version dog care plan"
  - "owner vs caregiver routine"
  - "split care protocol for travel"
  - "parallel pet care checklists"
  - "compress dog care plan to 7 days"
  - "what can't be cut from pet handover checklist"
  - "non-removable steps in shortened care timeline"
---

# dog-care-plan-dual-version-generator

Generates two parallel, synchronized care checklists — one for daily owner use and one for temporary caregiver handover — both aligned to the same core health modules (feeding, walking, grooming, deworming, weight tracking) and shared escalation rules; optionally compresses the plan to a 7-day critical-path timeline while preserving non-removable steps based on physiological safety, data continuity, and escalation integrity.

## Prompt

# Goal
Generate two de-identified, operationally identical checklists — a **Daily Owner Version** and a **Caregiver Handover Version** — derived from a unified dog care protocol. Both must cover the same five core modules: feeding, walking, grooming, deworming, and weight tracking; and embed the same conditional escalation logic (e.g., appetite decline response). Optionally, when requested, compress the full protocol into a 7-day critical-path version that explicitly identifies non-removable vs. compressible steps.

# Constraints & Style
• Output only two cleanly separated Markdown tables: 'Daily Owner Version' and 'Caregiver Handover Version' — unless compression is explicitly requested, in which case output only two sections: '✅ Non-removable steps' (bulleted, minimal justification referencing objective thresholds: physiological limits, data integrity needs, or escalation dependencies) and '⚠️ Compressible steps' (bulleted, brief rationale).
• Use placeholder syntax for all case-specific values: <BREED>, <AGE>, <CURRENT_WEIGHT_kg>, <NEUTER_STATUS>, <FEEDING_AMOUNT_g>, <WALK_DURATION_min>, <DEWORMING_SCHEDULE>.
• Caregiver version must include: explicit time-bound actions, photo/video verification prompts (e.g., '📸 send morning weight photo'), remote-check triggers (e.g., '▶️ you confirm via text within 1h'), and zero-assumption language (no 'as usual', 'like before').
• Owner version may use concise shorthand (e.g., '✓ 7:30/18:00', '▲ if >0.2kg/week') but retain all decision gates (e.g., 'if 24h intake <70% → check gums → if pale → call vet').
• All medical escalation criteria must be verbatim-aligned between versions (same wording, same conditions, same outcomes).
• No brand names, drug dosages, dates, locations, personal contact details, or institution names.
• Never invent new modules, thresholds, or clinical logic — strictly reflect only those user-confirmed in conversation (e.g., 70% intake threshold, 24h trigger, gum color check, weight delta limits).
• For compression mode: justifications must be imperative, third-person, and reference only objective constraints — not preferences or convenience.

# Workflow
1. Extract the canonical set of modules, timing frequencies, measurement units, and escalation conditions from user-confirmed requirements.
2. For each module, write parallel rows: one optimized for habitual owner execution, one for first-time caregiver execution with verification hooks.
3. Ensure cross-version consistency: if owner version says 'weigh daily pre-breakfast', caregiver version must say 'weigh at 7:15am → photo + value to group chat'.
4. If compression is requested: identify non-removable steps using only user-confirmed physiological, data-integrity, or escalation-critical constraints; classify all others as compressible with brief, objective rationale.
5. Output only the requested format — no intro, no explanation, no examples.

## Triggers

- generate daily and handover checklists
- dual-version dog care plan
- owner vs caregiver routine
- split care protocol for travel
- parallel pet care checklists
- compress dog care plan to 7 days
- what can't be cut from pet handover checklist
- non-removable steps in shortened care timeline
