---
id: "b362c006-5d6c-43bd-ba1b-b706dff78772"
name: "hypertension-risk-weekly-summary"
description: "Generates a concise, de-identified weekly risk summary for family caregivers based on home blood pressure readings, highlighting trends and clinical implications without daily noise."
version: "0.1.0"
tags:
  - "health-monitoring"
  - "caregiver-support"
  - "hypertension"
  - "summary-report"
  - "low-interruption"
triggers:
  - "weekly blood pressure summary"
  - "family caregiver risk report"
  - "hypertension weekly update"
  - "BP trend digest"
  - "quiet weekly health snapshot"
---

# hypertension-risk-weekly-summary

Generates a concise, de-identified weekly risk summary for family caregivers based on home blood pressure readings, highlighting trends and clinical implications without daily noise.

## Prompt

# Goal
Generate a one-paragraph weekly hypertension risk summary for a family caregiver, summarizing blood pressure trends, flagging clinically meaningful patterns (e.g., sustained elevation), and suggesting next-step actions — all in ≤80 words, with zero daily alerts or subjective commentary.

# Constraints & Style
- Must use only objective data: count of days with SBP ≥140 mmHg and/or DBP ≥90 mmHg; longest streak of elevated readings; presence of any reading ≥180/110 mmHg.
- Never include raw daily values, timestamps, or symptom logs.
- Use neutral, non-alarming language (e.g., 'elevated trend' not 'dangerous spike').
- End with exactly one actionable suggestion tied to evidence (e.g., 'Consider scheduling follow-up if ≥3 consecutive elevated days occur next week').
- No questions, no requests for input, no emojis, no markdown.

## Triggers

- weekly blood pressure summary
- family caregiver risk report
- hypertension weekly update
- BP trend digest
- quiet weekly health snapshot
