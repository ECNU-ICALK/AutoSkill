---
id: "599762a9-b2ba-431a-bc8e-18a7c34a2de3"
name: "canine-care-plan-dual-version-generator"
description: "A reusable skill that generates two parallel, policy-aligned care plans — one for daily self-care and one for temporary third-party care — with synchronized constraints across feeding, exercise, grooming, parasite control, weight monitoring, and clinical escalation rules."
version: "0.1.1"
tags:
  - "pet-care"
  - "care-plan"
  - "delegation"
  - "health-protocol"
  - "risk-mitigation"
  - "clinical-escalation"
  - "role-specific-planning"
triggers:
  - "generate daily and caregiver dog care plans"
  - "dual-version pet care protocol"
  - "self-care vs sitter care checklist"
  - "parallel dog care plans"
  - "pet care plan for owner and substitute"
---

# canine-care-plan-dual-version-generator

A reusable skill that generates two parallel, policy-aligned care plans — one for daily self-care and one for temporary third-party care — with synchronized constraints across feeding, exercise, grooming, parasite control, weight monitoring, and clinical escalation rules.

## Prompt

# Goal
Generate two de-identified, executable care plan versions — **Daily Self-Care Plan** and **Temporary Caregiver (e.g., pet-sitter/family) Plan** — for a healthy adult dog. Both must share identical core health policies (e.g., feeding schedule precision,驱虫 frequency, weight change thresholds, appetite decline escalation logic), but differ in execution ownership, verification methods, and risk-mitigation steps appropriate to the caregiver’s training level.

# Constraints & Style
• Output only two cleanly separated Markdown sections: '## 🏠 Daily Self-Care Plan' and '## 🧑‍🤝‍🧑 Temporary Caregiver Plan'.
• All medical/behavioral policies (e.g., "appetite drop → vet if ≥3 meals missed") must be *verbatim identical* between versions — no rewording or softening for caregivers.
• For caregiver version: replace self-verification actions (e.g., "I check footpads") with *observable, documentable, low-skill proxies* (e.g., "Take photo of footpads after each walk; upload to shared folder").
• Prohibit vague terms: ban 'as needed', 'if possible', 'try to', 'usually'; require concrete frequency (e.g., "2×/day"), duration (e.g., "≥30 min"), quantity (e.g., "120 g ±5 g"), or objective pass/fail criteria (e.g., "CRT <2 sec").
• Never include unverified medical claims (e.g., 'chicken broth aids digestion') — only evidence-informed, user-validated protocols.
• De-identify all payload: omit breed, age, name, location, product brands, exact dates, weights, and contact details; use placeholders like <DOG_WEIGHT>, <FEEDING_TIME>, <VET_CONTACT>.

# Workflow
1. Extract the user’s validated health policies from conversation history (e.g., feeding timing tolerance, drive frequency, weight fluctuation threshold, appetite decline escalation timeline).
2. For each of the five core domains (Feeding, Walking, Grooming, Parasite Control, Weight Tracking), define identical policy statements.
3. For the Daily Self-Care Plan: specify direct human actions with built-in quality checks (e.g., "Weigh food on digital scale; log value in tracker").
4. For the Temporary Caregiver Plan: convert each action into a verifiable, low-cognition task with mandatory documentation (e.g., "Photograph food bowl before/after meal with timestamp; upload to <SHARED_FOLDER>").
5. Embed the validated clinical escalation protocol (e.g., appetite decline response) *unchanged* in both plans — with explicit 'must-do' language and zero ambiguity.

## Triggers

- generate daily and caregiver dog care plans
- dual-version pet care protocol
- self-care vs sitter care checklist
- parallel dog care plans
- pet care plan for owner and substitute
