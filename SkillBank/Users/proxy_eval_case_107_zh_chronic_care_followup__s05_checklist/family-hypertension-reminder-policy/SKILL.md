---
id: "42537fc5-954f-48a9-a525-a759bb7a0967"
name: "family-hypertension-reminder-policy"
description: "生成符合家庭照护场景的高血压随访提醒策略，确保对患者（如父亲）的血压监测提醒频率适中、内容极简、不造成心理或操作负担。"
version: "0.1.0"
tags:
  - "healthcare"
  - "family-care"
  - "hypertension"
  - "reminder-design"
  - "accessibility"
triggers:
  - "remind parent to check blood pressure"
  - "gentle BP reminder"
  - "non-intrusive hypertension follow-up"
  - "low-frequency family health nudge"
  - "concise caregiver alert"
---

# family-hypertension-reminder-policy

生成符合家庭照护场景的高血压随访提醒策略，确保对患者（如父亲）的血压监测提醒频率适中、内容极简、不造成心理或操作负担。

## Prompt

# Goal
Generate a hypertension blood pressure monitoring reminder for a family caregiver (e.g., adult child) to send to their parent — concise, low-friction, non-repetitive, and respectful of the parent's autonomy and routine.

# Constraints & Style
- Must be ≤ 12 words total; no explanations, no questions, no emojis, no markdown.
- Must avoid urgency language (e.g., 'now', 'immediately', 'don’t forget'), medical jargon, or directive tone ('you must').
- Must not repeat daily — reminders should be spaced meaningfully (e.g., only when record is missing, or at fixed low-frequency anchor times like 'morning' and 'evening', not both).
- Must assume parent self-measures; caregiver’s role is passive observation and gentle follow-up only.
- Output only the reminder text — no prefix, no context, no suggestions.

# Workflow
None — this is a single-output generation task. No multi-step AI operations are specified or required.

## Triggers

- remind parent to check blood pressure
- gentle BP reminder
- non-intrusive hypertension follow-up
- low-frequency family health nudge
- concise caregiver alert
