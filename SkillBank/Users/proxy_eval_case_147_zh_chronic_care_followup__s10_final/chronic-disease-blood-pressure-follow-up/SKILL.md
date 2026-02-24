---
id: "9da923d3-0852-4447-abf6-c4a04137bc54"
name: "chronic-disease-blood-pressure-follow-up"
description: "A daily hypertension follow-up protocol that records morning/evening blood pressure, generates doctor communication summaries when BP remains elevated for 3+ consecutive days, and uses minimal reminders to avoid disturbing daily life."
version: "0.1.0"
tags:
  - "healthcare"
  - "chronic-disease"
  - "blood-pressure"
  - "patient-care"
  - "communication"
  - "reminders"
triggers:
  - "高血压随访提醒"
  - "每日血压记录"
  - "连续3天血压偏高"
  - "医生沟通摘要生成"
  - "慢性病管理"
---

# chronic-disease-blood-pressure-follow-up

A daily hypertension follow-up protocol that records morning/evening blood pressure, generates doctor communication summaries when BP remains elevated for 3+ consecutive days, and uses minimal reminders to avoid disturbing daily life.

## Prompt

# Goal
Generate a hypertension follow-up protocol that includes twice-daily blood pressure monitoring, simplified record keeping, automatic generation of doctor communication summaries when BP remains elevated for 3+ consecutive days, and minimal reminder frequency.

# Constraints & Style
- Record blood pressure twice daily: morning (7:00 AM) and evening (7:00 PM)
- BP elevation threshold: ≥140/90 mmHg
- Generate doctor communication summary when BP ≥140/90 mmHg for 3+ consecutive days
- Summary content: date range, BP values, symptoms, current medications
- Reminder frequency: only 2 daily reminders (7:00 AM and 7:00 PM)
- Record format: minimal (e.g., "132/84"), no complex tables
- Emergency protocol for BP ≥180/110 mmHg
- Language: simple, actionable, patient/family-friendly
- Include weekly summary check on Sunday

# Workflow
1. Set daily reminders at 7:00 AM (measure BP + medication) and 7:00 PM (measure BP + record)
2. Record BP values in minimal format (morning and evening)
3. Check daily: is BP ≥140/90 mmHg?
4. If yes for 3+ consecutive days: generate doctor communication summary
5. Otherwise: continue daily monitoring
6. On Sunday evening: perform 10-second review of week
7. For emergency (BP ≥180/110): trigger immediate action protocol

## Triggers

- 高血压随访提醒
- 每日血压记录
- 连续3天血压偏高
- 医生沟通摘要生成
- 慢性病管理
