---
id: "51c6f5ab-612c-4022-8eb3-2225fe3fda43"
name: "hypertension-blood-pressure-reminder-policy"
description: "A concise, low-interruption reminder policy for family caregivers to trigger hypertension follow-up actions based on home blood pressure readings."
version: "0.1.0"
tags:
  - "healthcare"
  - "chronic-care"
  - "family-care"
  - "bp-monitoring"
  - "clinical-alert"
triggers:
  - "remind me when blood pressure is high"
  - "alert on abnormal home BP"
  - "send quiet follow-up reminder"
  - "minimal BP alert"
  - "non-disruptive hypertension nudge"
---

# hypertension-blood-pressure-reminder-policy

A concise, low-interruption reminder policy for family caregivers to trigger hypertension follow-up actions based on home blood pressure readings.

## Prompt

# Goal
Generate a minimal, non-intrusive reminder message for a family caregiver when a hypertensive patient's home blood pressure reading meets predefined clinical thresholds — only when action is clinically indicated.

# Constraints & Style
- Output must be a single-line plain-text message (no markdown, no emojis, no explanations).
- Only trigger reminders for two conditions: (1) any morning or evening reading ≥140/90 mmHg → output '⚠️ Schedule follow-up visit'; (2) any reading ≥180/110 mmHg → output '🚨 Seek urgent medical care'.
- Never generate reminders for normal or mildly elevated values (<140/90).
- Never include time-of-day qualifiers, names, instructions, or next-step advice — only the standardized action phrase.
- No greetings, signatures, or emotional language.
- If input contains no valid BP reading (e.g., missing numbers, malformed), output nothing (empty string).

## Triggers

- remind me when blood pressure is high
- alert on abnormal home BP
- send quiet follow-up reminder
- minimal BP alert
- non-disruptive hypertension nudge
