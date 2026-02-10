---
id: "55ecfcff-047c-4e0c-97da-305de6e24915"
name: "family-blood-pressure-monitoring-with-quiet-reminders-and-weekly-risk-summary"
description: "A lightweight, non-intrusive protocol for daily home blood pressure monitoring by family caregivers, featuring minimal-alert threshold-based reminders and two distinct clinical outputs: (1) a clinician-ready handoff summary triggered only after explicit confirmation of three consecutive days of elevated readings, and (2) a calm, one-paragraph weekly risk summary highlighting trends and actionable insights — both designed to support informed follow-up without daily disruption."
version: "0.1.3"
tags:
  - "healthcare"
  - "chronic-disease"
  - "family-care"
  - "hypertension"
  - "behavioral-design"
  - "clinical-communication"
  - "health-monitoring"
  - "caregiver-support"
  - "summary-report"
  - "low-intervention"
  - "reporting"
  - "eldercare"
triggers:
  - "每天早晚测血压并提醒复诊"
  - "家庭血压监测不打扰"
  - "简洁版血压异常提醒规则"
  - "高血压随访提醒频率控制"
  - "老人血压记录轻量提醒"
  - "连续3天血压偏高就生成医生沟通摘要"
  - "3天超标就写给医生的话"
  - "自动生成复诊摘要"
  - "每周给家属一个风险周报"
  - "家庭血压监测周报"
  - "老人血压趋势总结"
  - "高血压家庭随访周摘要"
  - "不打扰的血压周度反馈"
  - "每周高血压风险周报"
  - "家属版血压周总结"
  - "家庭血压监测周报生成"
  - "简洁可执行的血压风险报告"
  - "不遗漏检查点的高血压周报"
---

# family-blood-pressure-monitoring-with-quiet-reminders-and-weekly-risk-summary

A lightweight, non-intrusive protocol for daily home blood pressure monitoring by family caregivers, featuring minimal-alert threshold-based reminders and two distinct clinical outputs: (1) a clinician-ready handoff summary triggered only after explicit confirmation of three consecutive days of elevated readings, and (2) a calm, one-paragraph weekly risk summary highlighting trends and actionable insights — both designed to support informed follow-up without daily disruption.

## Prompt

# Goal
Generate a daily blood pressure self-monitoring and alert protocol for a family caregiver supporting a hypertensive older adult, producing: (1) clear timing/method instructions for morning and evening measurements; (2) unambiguous, clinically grounded definitions of 'abnormal' requiring action; (3) a low-frequency, high-signal reminder strategy that avoids disruption; (4) a one-paragraph, clinician-ready handoff summary — but only when explicitly confirmed that three consecutive days of ≥140/90 mmHg have occurred under stable medication adherence; and (5) a one-paragraph weekly risk summary — generated on request from a raw BP log — highlighting trends, % elevated days, systolic/diastolic swing, consecutive elevation status, and a neutral concluding sentence.

# Constraints & Style
- Must use plain, actionable language — no medical jargon without immediate lay explanation (e.g., 'eGFR' → omit; 'kidney function test' → only if essential).
- Specify exact measurement windows: morning = after urination, before medication, between 6:00–10:00; evening = 20:00–22:00, 1 hour before bed, excluding post-bath/post-alcohol/post-exertion.
- Define 'abnormal' strictly as: (a) single reading ≥180/110 mmHg + symptoms → urgent action; (b) three consecutive days of ≥140/90 mmHg (on stable meds) → schedule clinic visit within 72h; (c) sustained drop <110/65 mmHg + dizziness/fatigue → pause morning dose and call doctor *before* next dose.
- Reminders must be ≤2 per day, text-only, under 12 words, scheduled at fixed times (e.g., "⏰ Time to check BP — sit quietly first"), and never include urgency language ('immediately', 'now') unless triggered by confirmed red-flag values.
- The clinical handoff summary must be generated only upon explicit user confirmation of three consecutive ≥140/90 mmHg readings. It must be one paragraph (3–5 sentences), plain text, no markdown or bullets, containing only: (1) confirmation of the 3-day threshold met, (2) date range and most recent reading, (3) adherence status, and (4) absence/presence of red-flag symptoms — using neutral, professional third-person clinical language. Exclude all interpretation, recommendations, or advice.
- The weekly risk summary must be strictly one paragraph (≤120 words), plain text, no markdown, no tables, no bullet points. Include only: (1) week date range, (2) % of days with elevated morning (≥140/90) or evening (≥135/85) readings, (3) largest observed systolic/diastolic swing across days, (4) presence/absence of ≥3 consecutive elevated days, (5) one neutral, non-alarmist concluding sentence (e.g., 'No urgent action needed; continue monitoring.' or 'Warrants discussion at next scheduled visit.'). Never mention absolute values outside defined thresholds; never interpret symptoms or comorbidities; never suggest medication changes. Use only generic terms: 'morning reading', 'evening reading', 'blood pressure', 'elevated', 'swing', 'consecutive days'. Tone: calm, factual, caregiver-facing.
- Weekly reports must be deliverable on Sunday and contain exactly four scannable sections in order: 'Overall Stability', 'Points to Watch', 'Medication Notes', 'One Action' — each introduced by its heading followed by a single declarative sentence (no bullets, dashes, or sub-bullets). All values and dates must use placeholders: [DATE], [VALUE]/[VALUE], [MEDICATION], [DOSAGE].
- Never propose app integrations, automation scripts, or device setup — only human-executable steps.
- Omit all references to Excel templates, voice scripts, or clinician handoffs unless explicitly requested in the current turn.

## Triggers

- 每天早晚测血压并提醒复诊
- 家庭血压监测不打扰
- 简洁版血压异常提醒规则
- 高血压随访提醒频率控制
- 老人血压记录轻量提醒
- 连续3天血压偏高就生成医生沟通摘要
- 3天超标就写给医生的话
- 自动生成复诊摘要
- 每周给家属一个风险周报
- 家庭血压监测周报
