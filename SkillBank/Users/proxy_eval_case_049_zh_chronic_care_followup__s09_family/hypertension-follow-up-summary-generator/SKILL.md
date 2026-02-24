---
id: "69d8d065-2ed1-4cf1-acd6-ad02ce8cd9fd"
name: "hypertension-follow-up-summary-generator"
description: "Generates a concise, ready-to-share clinical summary for physician consultation and a parallel family-facing risk summary when home blood pressure readings meet ≥140/90 mmHg for three consecutive days in the same measurement window."
version: "0.1.1"
tags:
  - "healthcare"
  - "chronic-care"
  - "family-caregiving"
  - "clinical-communication"
  - "hypertension"
  - "clinical-triage"
triggers:
  - "generate doctor summary for high BP"
  - "create 3-day BP summary"
  - "make clinical handoff note"
  - "prepare hypertension visit summary"
  - "BP escalation summary"
  - "generate family risk report"
  - "make caregiver action plan"
  - "hypertension follow-up summary"
---

# hypertension-follow-up-summary-generator

Generates a concise, ready-to-share clinical summary for physician consultation and a parallel family-facing risk summary when home blood pressure readings meet ≥140/90 mmHg for three consecutive days in the same measurement window.

## Prompt

# Goal
Generate two aligned, self-contained outputs from home BP data: (1) a one-page clinical summary for physician review, and (2) a plain-language risk summary for family members — triggered *only* when systolic/diastolic BP ≥140/90 mmHg occurs on **three consecutive calendar days**, in either morning (pre-medication) or evening (pre-sleep) measurements.

# Constraints & Style
- ✅ Clinical summary must include: date range of the 3-day elevation, all recorded BP values (with time context), medication adherence status, and observed symptoms (if any); formatted as a scannable markdown table + bullet list; max 150 words; no interpretation, advice, urgency labels, or external data.
- ✅ Family summary must use plain language, avoid medical jargon, omit raw numbers unless critical, emphasize stability/context, and end with a calm, forward-looking statement (e.g., 'We’ll check in with the doctor next week').
- ✅ Both outputs must be generated in parallel, fully independent — no cross-references or shared state assumptions.
- ❌ Do not suggest dose changes, differential diagnoses, lifestyle adjustments, or daily reminders.
- ❌ Do not include caregiver opinions, emotional framing, reassurances, subjective interpretations, or requests for confirmation/feedback.
- ❌ Do not reference prior summaries, trends beyond the 3-day window, lab results, weight, or unvalidated devices.

# Workflow
1. Confirm exactly three consecutive days meet the threshold (systolic ≥140 *and* diastolic ≥90, same time window, same arm, validated device).
2. Extract raw BP entries, timestamps, symptom notes, and medication log from the provided record.
3. Assemble clinical output into fixed sections: [Date Range], [BP Readings Table], [Medication & Symptom Summary].
4. Assemble family output as a single paragraph emphasizing context, stability, and next steps — no raw data unless essential.
5. Output both summaries only — no preamble, no follow-up questions, no null/default messages if threshold is unmet.

## Triggers

- generate doctor summary for high BP
- create 3-day BP summary
- make clinical handoff note
- prepare hypertension visit summary
- BP escalation summary
- generate family risk report
- make caregiver action plan
- hypertension follow-up summary
