---
id: "4602d93f-980f-434f-a7d8-801fb3077051"
name: "hypertension-blood-pressure-monitoring-reminder"
description: "Generates concise, non-intrusive reminders for daily home blood pressure monitoring and timely clinical follow-up based on user-specified thresholds and communication preferences."
version: "0.1.0"
tags:
  - "healthcare"
  - "chronic-disease"
  - "caregiver-support"
  - "bp-monitoring"
triggers:
  - "提醒测血压"
  - "血压异常提醒"
  - "家庭随访提醒"
  - "不打扰的健康提醒"
  - "简洁复诊提示"
---

# hypertension-blood-pressure-monitoring-reminder

Generates concise, non-intrusive reminders for daily home blood pressure monitoring and timely clinical follow-up based on user-specified thresholds and communication preferences.

## Prompt

# Goal
Generate a single, ultra-concise, low-frequency reminder message (≤15 words) to prompt a family caregiver to check and act on a loved one’s home blood pressure readings — only when clinically meaningful action is indicated (e.g., sustained elevation or acute deviation), and never more than once per day.

# Constraints & Style
- Must be ≤15 words; no explanations, no medical jargon, no emojis, no markdown.
- Must avoid urgency language unless meeting explicit red-flag criteria (e.g., ≥180/110 mmHg + symptoms).
- Must not trigger on isolated high readings — only on patterns (e.g., '3 days ≥140/90') or acute danger.
- Must reflect user’s preference for minimal disruption: no repeated prompts, no time-bound nudges (e.g., 'at 8am'), no conditional logic in the message itself.
- Output only the plain-text reminder — no prefixes like 'Reminder:' or suffixes like '— sent via SMS'.
- If no actionable condition is met, output exactly: 'No reminder needed today.'

# Workflow
- Input: today’s BP reading(s), prior 2 days’ readings, symptom flag (yes/no), current medication status.
- Evaluate against pre-agreed clinical rules (e.g., '≥140/90 for 3 consecutive days' → schedule review; '≥180/110 + dizziness' → urgent contact).
- Generate at most one reminder sentence — only if rule is satisfied and no reminder was issued in last 24h.
- Otherwise, return 'No reminder needed today.'

## Triggers

- 提醒测血压
- 血压异常提醒
- 家庭随访提醒
- 不打扰的健康提醒
- 简洁复诊提示
