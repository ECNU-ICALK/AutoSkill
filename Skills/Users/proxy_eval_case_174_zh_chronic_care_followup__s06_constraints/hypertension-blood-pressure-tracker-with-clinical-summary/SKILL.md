---
id: "2893166f-a886-4acd-9d4d-d45d8645b4ae"
name: "hypertension-blood-pressure-tracker-with-clinical-summary"
description: "A lightweight, family-friendly blood pressure tracking protocol that triggers automated clinical summary generation after three consecutive days of elevated readings (≥140/90 mmHg), designed to reduce caregiver burden while ensuring timely clinical escalation — with plain-text, mobile-optimized output for EHRs, messaging, or clinic intake."
version: "0.1.1"
tags:
  - "healthcare"
  - "chronic-disease"
  - "family-care"
  - "bp-monitoring"
  - "clinical-communication"
  - "plain-text"
triggers:
  - "generate doctor summary"
  - "3-day high BP report"
  - "clinical handoff note"
  - "hypertension escalation summary"
  - "automated clinic comms"
  - "weekly blood pressure summary"
  - "family caregiver risk report"
  - "copy-paste hypertension update"
  - "mobile-friendly clinical handoff"
---

# hypertension-blood-pressure-tracker-with-clinical-summary

A lightweight, family-friendly blood pressure tracking protocol that triggers automated clinical summary generation after three consecutive days of elevated readings (≥140/90 mmHg), designed to reduce caregiver burden while ensuring timely clinical escalation — with plain-text, mobile-optimized output for EHRs, messaging, or clinic intake.

## Prompt

# Goal
Automatically generate a concise, doctor- and caregiver-ready clinical communication summary when a patient records elevated blood pressure (≥140/90 mmHg) on three consecutive calendar days — using only the raw BP values and optional minimal context (e.g., symptoms, medication adherence notes) provided in daily responses.

# Constraints & Style
- ✅ Output must be strictly plain-text, no markdown, no headers, no bullet points, no tables, no alignment-dependent formatting — optimized for pasting directly into EHR messaging, clinic intake forms, WhatsApp, SMS, or email.
- ✅ Include only: date range of the 3 elevated readings, list of all recorded BP values (with time if specified), any reported symptoms (e.g., 'dizziness', 'headache'), and confirmed medication adherence status (e.g., 'missed dose on Day 2').
- ✅ Never infer, interpret, or add clinical advice — e.g., do not say 'consider dose increase'; only report what was observed.
- ✅ Do not include explanations, disclaimers, caregiver instructions, or speculative guidance in the summary.
- ✅ If fewer than 3 days of ≥140/90 are present, output nothing — silence is required.
- ✅ Treat '136/82-78' as ambiguous: only parse if format clearly separates morning/evening (e.g., '136/82,142/88') or includes explicit time markers.
- ✅ Avoid clinical jargon: use 'top number' instead of 'systolic', 'bottom number' instead of 'diastolic', and plain-language symptom descriptors (e.g., 'when standing up' instead of 'orthostatic').
- ✅ Prioritize scannability: lead with risk level and action; defer context to the end — but retain strict clinical fidelity for provider use.
- ✅ If no abnormal pattern is detected across the rolling 3-day window, output only: '✅ All readings within target range.'

## Triggers

- generate doctor summary
- 3-day high BP report
- clinical handoff note
- hypertension escalation summary
- automated clinic comms
- weekly blood pressure summary
- family caregiver risk report
- copy-paste hypertension update
- mobile-friendly clinical handoff
