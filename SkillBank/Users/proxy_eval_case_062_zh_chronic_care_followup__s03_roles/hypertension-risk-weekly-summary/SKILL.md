---
id: "0126ce82-3e95-4960-b196-1d6c7d0d7d1d"
name: "hypertension-risk-weekly-summary"
description: "Generates a concise, clinically grounded weekly risk summary for family caregivers when home blood pressure monitoring shows emerging patterns—focused on trend interpretation, contextual factors, and actionable next steps—not raw data rehash."
version: "0.1.0"
tags:
  - "hypertension"
  - "caregiver"
  - "weekly-report"
  - "risk-communication"
  - "clinical-summary"
triggers:
  - "每周风险周报"
  - "高血压家庭周报"
  - "血压趋势简报"
  - "家属版健康周总结"
  - "不打扰的风险提示"
---

# hypertension-risk-weekly-summary

Generates a concise, clinically grounded weekly risk summary for family caregivers when home blood pressure monitoring shows emerging patterns—focused on trend interpretation, contextual factors, and actionable next steps—not raw data rehash.

## Prompt

# Goal
Generate a one-paragraph weekly hypertension risk summary for a family caregiver, based solely on 7 days of home blood pressure records. Output must be self-contained, require zero external context, and fit in a single WhatsApp/WeChat message.

# Constraints & Style
- Must NOT include raw numbers, dates, or table formats — summarize trends only (e.g., '3 elevated morning readings', 'increasing evening variability')
- Must explicitly link observed patterns to *plausible non-urgent contributors* (e.g., 'coincided with 4 nights of <5h sleep', 'followed initiation of new NSAID') — never imply causation
- Must state *exactly one* clear, low-effort next step: either (a) continue current monitoring rhythm, (b) add one specific observation (e.g., 'note if dizziness occurs within 1h of dosing'), or (c) schedule brief clinician check-in (only if ≥3 days ≥140/90 *and* ≥1 red-flag symptom noted)
- Tone: calm, factual, non-alarming; avoid words like 'concern', 'worry', 'abnormal', 'problem'; use 'pattern', 'shift', 'notable', 'worth noting'
- Length: 60–90 characters max (excluding greeting/closing)
- No markdown, no bullet points, no placeholders — fully resolved output

# Workflow
1. Parse input as structured list of 7 daily entries: {date, am_bp, pm_bp, hr, notes}
2. Identify trend signals: (a) ≥3 days with AM ≥140 or PM ≥90, (b) ≥2 days with AM/PM difference >30 mmHg, (c) ≥1 day with HR <55 or >100 + BP change >20 mmHg
3. Cross-reference notes for co-occurring contextual flags (sleep <6h, NSAID use, missed dose, acute illness, salt-heavy meal)
4. Synthesize into single paragraph meeting all constraints above

## Triggers

- 每周风险周报
- 高血压家庭周报
- 血压趋势简报
- 家属版健康周总结
- 不打扰的风险提示
