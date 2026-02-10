---
id: "16c24054-20b3-4ac4-8ba3-85f57dd9d275"
name: "generate-clinical-communication-summary-for-3-day-hypertension"
description: "Generate structured doctor communication summary when hypertension persists for 3 consecutive days, including measurement dates/times, values, and physician recommendation."
version: "0.1.0"
tags:
  - "临床沟通"
  - "高血压管理"
  - "摘要生成"
  - "医疗随访"
triggers:
  - "连续3天血压偏高"
  - "生成医生沟通摘要"
  - "3天高血压需要医生沟通"
---

# generate-clinical-communication-summary-for-3-day-hypertension

Generate structured doctor communication summary when hypertension persists for 3 consecutive days, including measurement dates/times, values, and physician recommendation.

## Prompt

# Goal
Generate a concise clinical communication summary documenting 3 consecutive days of elevated blood pressure for physician review.

# Constraints & Style
- Only triggered when BP ≥140/90 mmHg for 3 consecutive days
- Include dates, times, morning/evening readings
- Keep summary brief (150-200 words)
- Use clinical terminology appropriate for physician review
- Include clear recommendation: "Suggest clinic visit within 7 days"
- No emotional language, focus on objective data

# Workflow
1. Verify 3 consecutive days of elevated BP readings
2. Extract measurement details (date, time, morning/evening values)
3. Format into structured clinical note with assessment and recommendation

## Triggers

- 连续3天血压偏高
- 生成医生沟通摘要
- 3天高血压需要医生沟通
