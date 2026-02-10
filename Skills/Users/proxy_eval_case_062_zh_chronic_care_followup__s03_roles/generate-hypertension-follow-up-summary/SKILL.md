---
id: "cd2c1828-767f-4d46-b2b9-d0305f6bb1aa"
name: "generate-hypertension-follow-up-summary"
description: "Automatically generates a concise, clinician-ready communication summary when home blood pressure readings exceed target thresholds for three consecutive days."
version: "0.1.0"
tags:
  - "healthcare"
  - "chronic-disease"
  - "clinical-communication"
  - "automation"
triggers:
  - "连续3天血压偏高生成医生摘要"
  - "生成高血压随访沟通摘要"
  - "整理三天异常血压给医生看"
---

# generate-hypertension-follow-up-summary

Automatically generates a concise, clinician-ready communication summary when home blood pressure readings exceed target thresholds for three consecutive days.

## Prompt

# Goal
Generate a structured, one-page doctor communication summary based on three consecutive days of elevated home blood pressure readings. The output must enable efficient clinical triage — highlighting trends, context, and actionable questions — without requiring manual data re-entry.

# Constraints & Style
- Output format: plain Markdown (no tables, no emojis, no markdown headers beyond # and ##)
- Length: strictly ≤ 150 words; prioritize signal over detail
- Content must include only: (1) patient identifier placeholder (<PATIENT_AGE_GROUP>), (2) date range of the 3-day elevation, (3) raw BP values (morning + evening per day), (4) notable symptoms or contextual notes from records (e.g., 'missed dose Day 2', 'reported dizziness Day 1'), (5) 2–3 focused clinical questions (e.g., 'Consider uptitration of ACEi?', 'Assess for orthostatic hypotension?')
- Never infer diagnosis, suggest drug changes, or include advice — only report and ask
- Exclude all personal identifiers (names, IDs, exact addresses, phone numbers)
- Use neutral, objective clinical language (e.g., 'observed elevation' not 'problematic spike')
- Do not include instructions, disclaimers, or assistant commentary

# Workflow
1. Confirm exactly three consecutive calendar days meet: morning BP ≥140/90 mmHg OR evening BP ≥140/90 mmHg
2. Extract all recorded BP pairs and associated brief notes from those days
3. Synthesize into a single summary using the structure in # Constraints & Style
4. Output only the summary — no preamble, no follow-up offer

## Triggers

- 连续3天血压偏高生成医生摘要
- 生成高血压随访沟通摘要
- 整理三天异常血压给医生看
