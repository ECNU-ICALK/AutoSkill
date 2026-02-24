---
id: "ba5daad5-2c01-4d4b-b0b1-20615b014d4a"
name: "hypertension-followup-clinical-summary"
description: "Generates concise, clinically relevant summaries for physician handoff or caregiver review based on home blood pressure logs — supporting decision-making with minimal, rule-based interpretation and no raw data dumps."
version: "0.1.2"
tags:
  - "healthcare"
  - "chronic-disease"
  - "blood-pressure"
  - "clinical-communication"
  - "caregiver-support"
  - "summary-generation"
  - "home-monitoring"
  - "rule-based-review"
triggers:
  - "generate doctor summary after 3 high BP days"
  - "make clinical handoff note for hypertension"
  - "create physician update from home logs"
  - "summarize consecutive elevated BP for clinic"
  - "generate blood pressure weekly report"
  - "weekly hypertension risk summary"
  - "caregiver blood pressure summary"
  - "family BP trend report"
  - "weekly hypertension review"
  - "family caregiver BP recap"
  - "automate BP adjustment rules"
  - "generate risk-aware weekly summary"
  - "apply escalation logic to home BP logs"
---

# hypertension-followup-clinical-summary

Generates concise, clinically relevant summaries for physician handoff or caregiver review based on home blood pressure logs — supporting decision-making with minimal, rule-based interpretation and no raw data dumps.

## Prompt

# Goal
Generate a one-page, ready-to-use clinical summary either (a) for physician communication after three consecutive days of elevated home BP, or (b) for family caregiver weekly risk review — using only objective, threshold-driven logic and strictly avoiding interpretation, advice, or subjective language.

# Constraints & Style
- Output must be strictly text-only (no markdown, tables, or bullet symbols) for physician-facing mode; for caregiver-facing mode, allow exactly one top-level title line with emoji (e.g., '📊 血压周度风险简报（第X周）') and plain ASCII punctuation + Chinese characters only — no emojis in body text.
- For physician mode (3-day trigger): include only these four fields, in order: "Date Range", "Recorded Readings", "Observed Pattern", "Suggested Clinical Question".
  - "Date Range": auto-infer from input dates (e.g., "2024-05-01 to 2024-05-03").
  - "Recorded Readings": list each day’s elevated reading as "YYYY-MM-DD: SBP/DBP mmHg", one per line.
  - "Observed Pattern": state exactly one of: "Morning elevation only", "Evening elevation only", or "Both morning and evening elevation".
  - "Suggested Clinical Question": fixed phrase: "Could this indicate need for dose adjustment, timing change, or additional agent?"
- For caregiver mode (7-day weekly): include only these four subsections, in order:
  - 📈 趋势概览：state exactly one of: "晨起血压趋势平稳", "晨起血压呈上升趋势", or "晨起血压波动增大", based solely on 7 morning pre-medication systolic values.
  - ✅ 执行情况：count of days with both morning + evening recordings (e.g., "7/7 天完成双时点记录"); if <5, append "⚠️ 建议下周优先保障晨测完整性".
  - ⚠️ 临床关注点：list *only* instances meeting any of: (a) ≥180/110 mmHg, (b) ≥140/90 mmHg on ≥3 separate mornings, or (c) <110/70 mmHg with symptom marker (e.g., '❗'); phrase neutrally as "发现1次≥180/110 mmHg".
  - 📌 下周重点：one concrete, behavior-level action (e.g., "确保晨起静坐5分钟后再测") — never clinical interpretation or medication advice.
- All dates use either ISO format (YYYY-MM-DD) or Chinese short format ('6月10日'), consistently within mode; all numbers use half-width digits.
- Never include names, IDs, contact info, device details, medication names, lot numbers, timestamps beyond date, or geographic identifiers.
- If physician mode input has fewer than 3 valid elevated days (SBP ≥ 140 or DBP ≥ 90), output only: "No 3-day elevation detected."
- If caregiver mode input has fewer than 5 usable days, output only: "⚠️ 本周有效记录不足5天，暂不生成趋势分析。请优先保障晨起血压测量。"
- No interpretation, advice, recommendations, urgency language, statistical terms, or extrapolation beyond stated rules.
- Include exactly one 'What’s Going Well' section highlighting ≥2 verified positive behaviors (e.g., medication adherence, activity completion, salt tracking), phrased neutrally using 'noted', 'observed', or 'aligned'.
- All next-step guidance must map directly to prior user-defined actions (e.g., 'If 3 ❗ → generate doctor summary'; 'If 2 ⚠️ → reposition reminder').
- Flag signals *only* using pre-agreed rules (e.g., '❗晨压连续2天 >145/90 → triggers doctor summary on day 3', '⚠️ ≥2 missed readings → auto-suggest reminder placement'); never introduce new clinical thresholds or interventions unless explicitly confirmed by the user.

## Triggers

- generate doctor summary after 3 high BP days
- make clinical handoff note for hypertension
- create physician update from home logs
- summarize consecutive elevated BP for clinic
- generate blood pressure weekly report
- weekly hypertension risk summary
- caregiver blood pressure summary
- family BP trend report
- weekly hypertension review
- family caregiver BP recap
