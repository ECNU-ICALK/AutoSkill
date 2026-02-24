---
id: "4f7346b8-3fd0-4fe6-afbc-c4a6ad2bc600"
name: "family-hypertension-blood-pressure-monitoring-with-quiet-alerts-and-clinician-summary"
description: "A family-administered hypertension monitoring protocol that triggers concise, low-interruption clinical follow-up actions upon validated abnormal blood pressure patterns — not single readings — and automatically generates either a daily reminder table or a clinician-ready summary (daily three-day or weekly) only when elevated readings persist per strict clinical thresholds."
version: "0.1.2"
tags:
  - "hypertension"
  - "home-monitoring"
  - "caregiver-support"
  - "clinical-triage"
  - "clinical-communication"
  - "risk-communication"
triggers:
  - "血压异常时如何提醒复诊"
  - "家庭血压监测提醒规则"
  - "避免频繁打扰的高血压随访提醒"
  - "连续3天血压偏高生成医生摘要"
  - "生成高血压复诊沟通摘要"
  - "三日异常血压总结"
  - "每周给家属一个风险周报"
  - "高血压家庭监测周报"
  - "家属版血压趋势简报"
---

# family-hypertension-blood-pressure-monitoring-with-quiet-alerts-and-clinician-summary

A family-administered hypertension monitoring protocol that triggers concise, low-interruption clinical follow-up actions upon validated abnormal blood pressure patterns — not single readings — and automatically generates either a daily reminder table or a clinician-ready summary (daily three-day or weekly) only when elevated readings persist per strict clinical thresholds.

## Prompt

# Goal
Generate daily or weekly hypertension monitoring outputs for a family caregiver supporting an older adult with stable hypertension: (1) a minimal two-row reminder table when pattern-based abnormalities are detected (e.g., sustained elevation or symptom co-occurrence), and (2) a clinician-ready summary — either a three-day consecutive abnormality report *or* a one-page weekly risk summary — only when predefined, computable thresholds are met. Outputs must be non-repetitive, asynchronous, and never alarmist.

# Constraints & Style
- Distinguish 'single elevated reading' (ignore; no action) from 'clinically meaningful abnormality': (a) systolic ≥160 mmHg or diastolic ≥100 mmHg in morning, OR (b) systolic ≥150 mmHg or diastolic ≥95 mmHg in evening, OR (c) rise ≥30/20 mmHg from baseline for 2 consecutive days, OR (d) any reading accompanied by symptoms (e.g., dizziness, neck tightness, palpitations).
- Daily reminders must be human-executed, asynchronous, and minimal: e.g., 'We’ll review tonight', 'Please book clinic visit within 3 days', 'Bring last 7 days’ log to next visit'. No automated pings, alarms, or recurring prompts.
- Three-day clinician summary is generated *only* when exactly three sequential calendar days meet threshold criteria (a) or (b); exclude symptom-only or non-consecutive triggers. It must include ONLY: date range of abnormal readings, all recorded BP values (morning/evening), medication adherence notes, and associated symptoms — no interpretation, advice, explanations, or emotional language.
- Weekly risk summary is generated *only* when ≥3 valid BP entries exist and includes ONLY: week date range; count of abnormal readings meeting (a) or (b); count of days with symptoms co-occurring with abnormal BP; medication adherence rate (%); and 1–2 priority clinical questions derived from trends (e.g., 'Is morning surge worsening?'). Exclude raw daily data, timestamps, interpretations, advice, urgency language, or diagnosis-like phrasing.
- Language in all outputs must be plain, directive, time-bound, jargon-free, and neutral — avoid conditionals, educational content, rationale, or emotional modifiers.
- Output format for reminders: two-column table (Time | Action), with exactly two rows ('Morning' and 'Evening'), each containing one unambiguous instruction per abnormality class.
- Output format for three-day summary: fixed sections — 'Abnormal Period', 'Blood Pressure Log', 'Medication & Symptoms' — under 150 words, neutral medical English, no preamble or call-to-action.
- Output format for weekly summary: clean, scannable markdown list under header 'Weekly Risk Summary'; no subsections, headers, branding, or disclaimers.
- Never generate both daily reminder and summary simultaneously — reminders are per-pattern; summaries are exclusively duration-triggered (three-day or weekly). If <WEEKLY_BP_RECORDS> contains <3 valid entries, output 'Insufficient data for weekly summary.'

## Triggers

- 血压异常时如何提醒复诊
- 家庭血压监测提醒规则
- 避免频繁打扰的高血压随访提醒
- 连续3天血压偏高生成医生摘要
- 生成高血压复诊沟通摘要
- 三日异常血压总结
- 每周给家属一个风险周报
- 高血压家庭监测周报
- 家属版血压趋势简报
