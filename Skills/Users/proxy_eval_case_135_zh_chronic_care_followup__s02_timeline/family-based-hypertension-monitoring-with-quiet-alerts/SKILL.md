---
id: "04b05005-5788-4c74-9892-d0e8cee09644"
name: "family-based-hypertension-monitoring-with-quiet-alerts"
description: "A reusable skill for family caregivers to implement daily home blood pressure monitoring with minimal-interruption, rule-based clinical alerts — designed to avoid over-notification while ensuring timely action on clinically meaningful deviations."
version: "0.1.3"
tags:
  - "hypertension"
  - "family-care"
  - "clinical-alerting"
  - "low-friction-monitoring"
  - "clinical-communication"
  - "risk-reporting"
  - "clinical-thresholds"
triggers:
  - "提醒频率不能太打扰"
  - "尽量简洁"
  - "异常时要提醒复诊"
  - "每天早晚记录血压"
  - "连续3天血压偏高生成沟通摘要"
  - "自动生成复诊沟通内容"
  - "风险周报"
  - "把时间压缩一周"
  - "哪些步骤不能删"
---

# family-based-hypertension-monitoring-with-quiet-alerts

A reusable skill for family caregivers to implement daily home blood pressure monitoring with minimal-interruption, rule-based clinical alerts — designed to avoid over-notification while ensuring timely action on clinically meaningful deviations.

## Prompt

# Goal
Generate a family-friendly hypertension self-monitoring protocol that enforces daily morning/evening BP measurement and triggers *only* high-signal clinical alerts — no routine confirmations, no daily or weekly summaries, no redundant notifications.

# Constraints & Style
- Must define exactly three alert conditions (no more): (1) two consecutive days ≥140/90 mmHg → gentle verbal nudge to schedule review; (2) single reading ≥180/110 mmHg + acute symptom cue → immediate action instruction; (3) sudden drop >20 mmHg systolic/diastolic + symptom → same-day clinician contact prompt.
- All alerts must be phrased as plain-language, non-alarming, caregiver-directed actions (e.g., “Text him: ‘Let’s check in with Dr. Lee this week’”) — never addressed to patient directly unless specified.
- Zero tolerance for daily reminders, weekly recaps, or automated messages — only event-triggered, human-executed prompts.
- Output must exclude clinical rationale, physiology explanations, or device recommendations unless explicitly requested in the current turn.
- Use placeholder <PATIENT_NAME> for personalization; omit age, diagnosis duration, meds, comorbidities, names, dates, symptoms, or identifiers unless provided in input.
- When three consecutive days ≥140/90 mmHg are detected in the same time slot (morning or evening), generate a concise, ready-to-share doctor communication summary: one plain-text paragraph (≤80 words), containing only (a) observation period (e.g., 'Apr 1–3'), (b) pattern ('3 consecutive mornings ≥140/90'), (c) regimen context (e.g., 'on current regimen of <MEDICATION> <DOSE>'), and (d) neutral, action-oriented closing (e.g., 'Requesting brief review of dosing or adherence'). Never interpret symptoms, suggest diagnosis, or include urgency language.
- If fewer than 3 consecutive days meet threshold, output nothing for that condition.
- Weekly summaries are disallowed unless explicitly triggered by ≥3 consecutive elevated readings in same time slot — in which case, output must be plain-text bullet list (max 7 lines), use only ✅/⚠️/❗ icons, aggregate only (no raw values), preserve gap detection (e.g., missing evening readings), medication supply check, and status classification ('Stable' / 'Watch' / 'Act'); close with 'Bring this summary to your next clinical visit.' or equivalent. No section headers beyond 'Weekly Risk Summary'.

## Triggers

- 提醒频率不能太打扰
- 尽量简洁
- 异常时要提醒复诊
- 每天早晚记录血压
- 连续3天血压偏高生成沟通摘要
- 自动生成复诊沟通内容
- 风险周报
- 把时间压缩一周
- 哪些步骤不能删
