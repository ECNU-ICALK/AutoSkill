---
id: "46125a8d-817a-4555-be69-7f002def4781"
name: "automated-hypertension-weekly-risk-summary"
description: "Generates a concise, clinically meaningful, family-facing weekly risk summary for hypertension management, automatically compiled from 7 days of home blood pressure records and contextual notes — highlighting up to three evidence-informed risk signals, each paired with a concrete, executable action for caregivers."
version: "0.1.1"
tags:
  - "health-monitoring"
  - "chronic-care"
  - "family-caregiving"
  - "hypertension"
  - "risk-reporting"
  - "actionable-reporting"
triggers:
  - "生成本周血压风险周报"
  - "每周家属风险总结"
  - "汇总过去七天血压情况"
  - "出一份家庭血压周报"
  - "高血压周度简报"
  - "每周给家属一个风险周报"
  - "高血压周报里列出最重要的三个风险点和怎么做"
  - "家庭血压周总结要带可操作建议"
---

# automated-hypertension-weekly-risk-summary

Generates a concise, clinically meaningful, family-facing weekly risk summary for hypertension management, automatically compiled from 7 days of home blood pressure records and contextual notes — highlighting up to three evidence-informed risk signals, each paired with a concrete, executable action for caregivers.

## Prompt

# Goal
Generate a de-identified, one-page weekly risk summary for a family caregiver monitoring a hypertensive patient’s home blood pressure. Output must be plain-text, mobile-friendly, and structured for rapid clinical scanning and caregiver action.

# Constraints & Style
- Must include only: (1) week date range, (2) % of days with ≥1 reading ≥140/90, (3) highest/lowest systolic & diastolic values, (4) notable trends (e.g., 'morning drift +5 mmHg', 'evening variability >15 mmHg'), (5) medication adherence status (‘full’, ‘1 missed’, ‘unknown’), (6) reported symptoms or lifestyle changes (summarized in ≤8 words), (7) risk tier: ‘Low’ (0 days ≥140/90), ‘Moderate’ (1–2 days), ‘Elevated’ (3–6 days), ‘Urgent’ (7 days or any ≥180/110), (8) up to three clinically grounded risk signals — each formatted as ‘▪ [plain-language description] → [concrete, family-executable action]’, derived only from observed data (e.g., sustained elevation, circadian shift, measurement gaps, symptom correlation); omit filler if <3 signals exist, (9) a closing reassurance line affirming caregiver agency and normalizing monitoring as protective.
- Never include raw daily logs, names, ages, exact addresses, clinic names, drug batch numbers, averages, thresholds, or generic unlinked terms (e.g., 'stress', 'diet').
- Use only neutral, non-alarmist, jargon-free language — e.g., ‘evening readings consistently higher than morning’ not ‘nocturnal hypertension’; ‘blood pressure doesn’t drop well at night’ not ‘non-dipping pattern’.
- Max length: 12 lines; no markdown, no bullet symbols (use plain dashes ‘—’), no emojis except optional single-line visual cues (📌, ⚠️, 💡) if space permits without exceeding line limit.
- If data is incomplete (<5 days recorded), append: ‘— Summary based on <N> days; encourage consistent logging.’
- Avoid medical jargon and clinical imperatives (e.g., ‘Go to ER’, ‘Consult physician’) — use only family-level actions (e.g., ‘move pillbox next to toothbrush’, ‘set phone reminder for bedtime’).

# Workflow
1. Accept input as a single string containing: week range (e.g., ‘Apr 1–7’), up to 7 days of timestamped BP readings (format: ‘YYYY-MM-DD HH:mm: S/D HR’ or ‘date: S/D’), current medication, adherence note, and brief context.
2. Parse and validate all BP values; discard malformed entries.
3. Compute metrics: elevated-day count, min/max S/D, trend descriptors (based on linear delta across morning/evening medians), adherence label.
4. Detect up to three highest-priority, data-linked risk signals using clinical logic (e.g., ≥3 days ≥140/90; evening > morning on ≥4 days; ≥2 missed measurements; systolic rise >10 mmHg across 3 days with reported sleep loss).
5. For each signal, generate a plain-language description + one concrete, family-executable action.
6. Synthesize into fixed-section output — strictly in this order: Date Range, Elevated Days %, Extremes, Trend, Adherence, Context, Risk Tier, Top Risks + Actions, Reassurance Line.

## Triggers

- 生成本周血压风险周报
- 每周家属风险总结
- 汇总过去七天血压情况
- 出一份家庭血压周报
- 高血压周度简报
- 每周给家属一个风险周报
- 高血压周报里列出最重要的三个风险点和怎么做
- 家庭血压周总结要带可操作建议
