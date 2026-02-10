---
id: "e2dafa5c-523c-411b-b5f6-75a93da2a3b8"
name: "daily-hypertension-self-care-checklist"
description: "Generates a minimal, executable daily checklist for hypertension self-management at home, designed for older adults — focused on observability, low cognitive load, and zero ambiguity."
version: "0.1.0"
tags:
  - "hypertension"
  - "eldercare"
  - "checklist"
  - "low-cognition"
  - "executable"
triggers:
  - "每日清单版本"
  - "可以直接执行的每日清单"
  - "高血压日常执行清单"
---

# daily-hypertension-self-care-checklist

Generates a minimal, executable daily checklist for hypertension self-management at home, designed for older adults — focused on observability, low cognitive load, and zero ambiguity.

## Prompt

# Goal
Generate a single-column, time-agnostic daily checklist (max 5 items) for home hypertension self-care, strictly limited to observable, binary (done/not done), non-clinical actions — no interpretation, no numbers, no medical terms.

# Constraints & Style
- Language: Plain, warm, Mandarin — use active verbs like '测'、'吃'、'放'、'记'； avoid '应'、'需'、'建议'、'可能'、'注意'；
- Format: One item per line, emoji-led (✅/🔘/🗓️/💊/📝), no bullets or numbering; no explanations, no sub-bullets;
- Content scope only: blood pressure measurement, medication intake, salt-aware eating, record placement, and one optional wellness anchor (e.g., step count or hydration);
- Must NOT include: thresholds (e.g., '≥140'), symptoms (e.g., '头晕'), clinical rationale, doctor instructions, or any conditional logic;
- All items must be physically verifiable by sight/touch within 10 seconds;
- Output must be exactly 5 lines — no more, no less.

# Workflow
None — this is a static template generator. No input parsing, no data aggregation, no state tracking. Input is empty; output is deterministic.

## Triggers

- 每日清单版本
- 可以直接执行的每日清单
- 高血压日常执行清单
