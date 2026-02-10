---
id: "fb8d3ae2-d886-4a45-8c07-116e78f2ecde"
name: "hypertension-daily-monitoring-with-automated-clinical-summary"
description: "A reusable skill that monitors daily home blood pressure readings and automatically generates a concise, action-oriented clinical summary for physician communication when elevated readings persist for three consecutive days."
version: "0.1.0"
tags:
  - "health-monitoring"
  - "clinical-communication"
  - "chronic-disease"
  - "automation"
  - "elderly-care"
triggers:
  - "连续3天血压偏高就生成医生沟通摘要"
  - "三天血压高了自动写给医生的话"
  - "家庭血压记录满三天异常时输出就诊摘要"
  - "生成临床简报用于复诊沟通"
---

# hypertension-daily-monitoring-with-automated-clinical-summary

A reusable skill that monitors daily home blood pressure readings and automatically generates a concise, action-oriented clinical summary for physician communication when elevated readings persist for three consecutive days.

## Prompt

# Goal
Monitor daily home blood pressure (BP) measurements and, upon detecting three consecutive days where either morning or evening BP meets or exceeds threshold values (morning ≥140/90 mmHg OR evening ≥135/85 mmHg), generate a standardized, clinician-ready communication summary — no manual calculation or formatting required.

# Constraints & Style
- ✅ Input: Exactly 3 consecutive days of structured BP entries (date, morning BP, evening BP, optional symptoms/heart rate)
- ✅ Output: Plain-text, single-paragraph summary (<120 words); includes only: (1) observation period, (2) pattern (e.g., 'morning systolic consistently elevated'), (3) highest recorded values, (4) relevant symptoms if reported, (5) clear ask ('Please advise on medication adjustment or further evaluation')
- ❌ No interpretation, diagnosis, or treatment suggestions
- ❌ No markdown, tables, bullet points, or placeholders — output is copy-paste ready for SMS/email to clinician
- ❌ Do not trigger for isolated highs, non-consecutive days, or values below thresholds
- Language: Clear, neutral, third-person clinical tone; avoid emotive or caregiver-centric phrasing (e.g., 'we noticed' → 'recorded values show')

# Workflow
1. Accept 3 consecutive daily BP records as input
2. Validate each day contains at least one qualifying reading (morning ≥140/90 OR evening ≥135/85)
3. Extract dates, values, and any documented symptoms
4. Synthesize into one cohesive clinical paragraph using fixed phrasing templates
5. Output only the final summary — no preamble, no explanations

## Triggers

- 连续3天血压偏高就生成医生沟通摘要
- 三天血压高了自动写给医生的话
- 家庭血压记录满三天异常时输出就诊摘要
- 生成临床简报用于复诊沟通
