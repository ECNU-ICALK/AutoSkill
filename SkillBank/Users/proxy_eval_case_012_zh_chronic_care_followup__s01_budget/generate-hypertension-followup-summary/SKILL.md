---
id: "0a21169d-2121-4f3e-9a70-9599456ceb4f"
name: "generate-hypertension-followup-summary"
description: "Generates a concise, ready-to-share clinical summary for physician consultation when home blood pressure readings exceed target thresholds for three consecutive days, or a weekly risk summary for family caregivers highlighting trends, anomalies, and actionable next steps."
version: "0.1.1"
tags:
  - "healthcare"
  - "hypertension"
  - "clinical-communication"
  - "home-monitoring"
  - "chronic-care"
  - "family-support"
  - "risk-reporting"
triggers:
  - "连续3天偏高就生成医生沟通摘要"
  - "生成复诊用血压摘要"
  - "整理三天血压给医生看"
  - "输出可直接发给医生的血压总结"
  - "generate weekly blood pressure risk report"
  - "send family caregiver weekly summary"
  - "weekly hypertension update for relatives"
  - "summarize BP trends for family"
  - "BP weekly review for non-clinical caregiver"
---

# generate-hypertension-followup-summary

Generates a concise, ready-to-share clinical summary for physician consultation when home blood pressure readings exceed target thresholds for three consecutive days, or a weekly risk summary for family caregivers highlighting trends, anomalies, and actionable next steps.

## Prompt

# Goal
Generate either (a) a clinician-ready communication summary for 3 consecutive days of elevated morning BP (≥140/90 mmHg), OR (b) a caregiver-facing weekly risk summary — both derived solely from user-provided home BP data (morning/evening readings), with strict adherence to objective computation and no interpretation.

# Constraints & Style
- Output must be plain text (no markdown, no bullets, no icons, no headers); line breaks allowed only for visual separation.
- For the 3-day clinical summary (triggered by explicit 3-day elevation): include exactly these 4 sections in order, each on its own line(s):
  1. "Patient context": age group (e.g., '60+'), hypertension status (e.g., 'stable primary HTN'), and key comorbidities *only if previously stated by user* — otherwise omit.
  2. "Recorded values": list date, morning SBP/DBP for all 3 days, one per line, in ISO date format (YYYY-MM-DD).
  3. "Observations": state only what is directly inferable: 'Morning BP elevated on 3 consecutive days', plus *one* optional note if user mentioned symptoms tied to a specific day (e.g., 'Reported morning dizziness on Day 2') — otherwise omit.
  4. "Request": exactly: 'Please assess need for medication adjustment.'
- For the weekly caregiver summary (triggered by weekly data or caregiver intent): output only the section "Weekly Risk Summary", containing exactly these 4 labeled elements in order:
  1. **Trend Summary**: One sentence comparing current vs prior week’s morning/evening averages (e.g., 'Morning systolic rose +5 mmHg avg vs last week').
  2. **Key Anomaly**: Report *only* the most clinically relevant anomaly — either (a) longest streak of elevated morning readings (≥140/90), (b) largest single-day swing (>30/20 mmHg), or (c) any reading ≥180/110 — whichever occurred most recently.
  3. **Care Action**: One imperative sentence tied *only* to the reported anomaly (e.g., 'Confirm medication adherence for those 3 mornings').
  4. **Doctor Prep Note**: One phrase indicating what to bring or ask — e.g., 'Bring full 7-day log' — selected *only* from pre-approved clinical prompts aligned with the anomaly.
- Never add interpretation, risk assessment, lifestyle suggestions, explanations, disclaimers, tool recommendations, emojis, or formatting beyond bolding the 4 weekly labels (**Trend Summary**, etc.).
- No personal identifiers (names, ages, meds) — use placeholders <PATIENT> or <MEDICATIONS> only if structurally required; otherwise omit.
- All values must be computed from input data — no assumptions, interpolation, or external thresholds beyond: ≥140/90 (morning), ≥135/85 (evening), >30/20 swing, ≥180/110 single.
- If required data is missing for the 3-day summary, output only: 'Insufficient data: missing <X>.'
- If no anomaly meets criteria in weekly mode, state: 'No clinically significant deviations detected this week.'
- Keep total length under 12 lines for either mode.

# Workflow
- Wait for user to provide: (a) three dates with corresponding morning BP values (for clinical summary), OR (b) structured daily entries with at minimum date, morning_sbp_dbp, and evening_sbp_dbp (for weekly summary).
- Validate thresholds strictly: for 3-day mode, confirm all three morning readings meet ≥140/90 mmHg; for weekly mode, compute averages and scan chronologically for anomalies using defined criteria.
- Assemble output strictly per the applicable section set above — no mixing of modes, no extra content.

## Triggers

- 连续3天偏高就生成医生沟通摘要
- 生成复诊用血压摘要
- 整理三天血压给医生看
- 输出可直接发给医生的血压总结
- generate weekly blood pressure risk report
- send family caregiver weekly summary
- weekly hypertension update for relatives
- summarize BP trends for family
- BP weekly review for non-clinical caregiver
