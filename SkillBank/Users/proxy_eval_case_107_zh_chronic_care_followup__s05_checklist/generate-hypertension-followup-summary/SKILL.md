---
id: "f2854301-70b0-4ab5-bc20-b4ac32761418"
name: "generate-hypertension-followup-summary"
description: "Automatically generates a concise, clinician- or caregiver-ready summary when home blood pressure readings exceed target thresholds for three consecutive days, formatted for direct use in clinical discussion."
version: "0.1.1"
tags:
  - "healthcare"
  - "chronic-disease"
  - "clinical-handoff"
  - "caregiver-support"
  - "template"
triggers:
  - "3-day high BP handoff to doctor"
  - "hypertension follow-up summary"
  - "家庭血压连高三天输出给医生的简报"
  - "连续3天血压偏高就生成医生沟通摘要"
---

# generate-hypertension-followup-summary

Automatically generates a concise, clinician- or caregiver-ready summary when home blood pressure readings exceed target thresholds for three consecutive days, formatted for direct use in clinical discussion.

## Prompt

# Goal
Generate a structured, one-page summary triggered by three consecutive days of elevated home blood pressure (≥140/90 mmHg), using only the provided raw data and standard clinical context. Output must be self-contained, printable, and ready for direct use in a doctor visit — either as a clinician handoff artifact or caregiver-facing report.

# Constraints & Style
- Include exactly: (1) patient identifier placeholders (<PATIENT_NAME>, <AGE>, <CURRENT_MEDS>), (2) date range of the 3-day abnormal window (<DATE_RANGE>), (3) tabulated raw BP values (morning/evening per day, labeled as 'top/bottom number'), (4) structured checklist of common modifiable factors (e.g., missed dose, sleep, salt, stress), (5) one pre-written, clinician-aligned concluding statement — factual, non-alarming, no interpretation, advice, or diagnosis.
- Format as a clean markdown table with columns: Date | Time | BP (mmHg) | Medication Taken? | Symptoms Reported.
- Add fixed header: "Clinical Summary for Provider Review — Triggered by 3 Consecutive Days ≥140/90 mmHg (Home Measurement)".
- Language must be neutral, factual, and plain-language; avoid medical jargon beyond essential terms (e.g., 'mmHg', 'top/bottom number', 'medication').
- Never infer missing values; leave blank cells empty.
- Zero personal data: all identifiers, dates, values, and medications must be placeholders (e.g., <BP_MORNING_DAY1>, <DATE_RANGE>).
- No explanations, disclaimers, footnotes, tips, reminders, emoji, or text outside the summary body.
- Length capped at ~180 words; fit on one A5 or half-page.
- Output only the final formatted summary — nothing before or after.

## Triggers

- 3-day high BP handoff to doctor
- hypertension follow-up summary
- 家庭血压连高三天输出给医生的简报
- 连续3天血压偏高就生成医生沟通摘要
