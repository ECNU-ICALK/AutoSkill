---
id: "1f78004a-4793-4643-9e4d-de861d7bd57c"
name: "adaptive-exam-study-plan-with-biweekly-mock-driven-adjustment"
description: "Generates a 14-week professional exam study plan that dynamically adjusts subject focus, practice intensity, and intervention strategy every two weeks based on biweekly mock exam performance, quantified stagnation signals, and error-pattern analysis — culminating in a low-stress, neurocognitively optimized, copy-paste-friendly final-week execution checklist."
version: "0.1.3"
tags:
  - "exam-prep"
  - "adaptive-planning"
  - "performance-feedback"
  - "biweekly-review"
  - "mock-driven"
  - "stagnation-response"
  - "error-analysis"
  - "pivot-rule"
  - "low-pressure-execution"
  - "stress-reduction"
  - "execution-clarity"
  - "copy-paste"
triggers:
  - "调整备考重点"
  - "根据模考成绩优化计划"
  - "动态调整学习计划"
  - "每两周复盘考试表现"
  - "按分数反馈更新复习策略"
  - "连续停滞时切到错题类型专项"
  - "最后给考前一周低压力执行清单"
  - "模考驱动的重点迁移"
  - "考前一周执行清单"
  - "最后七天怎么安排"
  - "低压力冲刺计划"
---

# adaptive-exam-study-plan-with-biweekly-mock-driven-adjustment

Generates a 14-week professional exam study plan that dynamically adjusts subject focus, practice intensity, and intervention strategy every two weeks based on biweekly mock exam performance, quantified stagnation signals, and error-pattern analysis — culminating in a low-stress, neurocognitively optimized, copy-paste-friendly final-week execution checklist.

## Prompt

# Goal
Generate a 14-week exam preparation plan for a professional certification or civil service exam, structured in biweekly cycles (Weeks 1–2, 3–4, ..., 13–14), where content emphasis, practice intensity, review strategy, and targeted interventions are explicitly conditioned on the user’s simulated exam scores, timing metrics, and progress stagnation signals — and conclude with a strictly non-adaptive, low-stress, plain-text 7-day pre-exam checklist.

# Constraints & Style
- Must include exactly 7 biweekly phases — no weekly granularity unless nested under a biweekly heading.
- Each phase must specify: (a) primary adjustment triggers (e.g., 'if <CURRENT_SCORE> < 70%', 'if same <QUESTION_TYPE> accuracy ≤ previous +5% across ≥2 mocks', 'if same <SUBJECT_AREA> repeated errors ≥2/week in error log', 'if no improvement in <TIME_PER_ITEM> or % correct for <SUBJECT_AREA> over ≥2 mocks'), (b) revised focus areas (e.g., 'shift 70% of practice time from theory to timed application drills'), and (c) concrete success criteria for exiting the phase (e.g., 'achieve ≥80% accuracy on 3 consecutive topic sets').
- When stagnation or repeated error patterns are detected, insert a time-bound, slot-resident 'error-type专项' intervention block (e.g., 'misapplied formula drills', 'premise-conclusion mismatch analysis', 'time-wasting step elimination') — specified as '10-min concept refresher + 5 annotated re-solves' — scheduled within existing time budget (<DAILY_MINUTES>, <WEEKEND_HOURS>).
- Each biweekly mock anchor (end of Weeks 2, 4, 6, 8, 10, 12) must be followed by a standardized 5-minute dual-dimension analysis: lowest correct-rate topic AND highest time-overrun module.
- After each pivot, enforce a '48-hour validation check': 3 new same-source questions under timed conditions, with pass/fail criteria and fallback protocol.
- Include a standalone 'Final Week Low-Pressure Execution Checklist' containing only concrete, binary tasks — formatted as plain text (no tables, no markdown syntax), labeled D-7 through D-1, each with 'Core goal:' and 'Tasks:' lines; all tasks imperative, time-bounded (<90 min total/day), executable without external tools, and embedded with at least one sensory or behavioral anchor (e.g., 'while listening to white noise', 'say aloud once'); zero new learning, zero full-length practice, zero error correction, zero flashcards; total output under 35 lines; ends with 'Principles: No new input. Only retrieval. Only control.'
- Do not assume or invent baseline scores, passing thresholds, exam structure, syllabi, laws, or resource names — all logic must be parameterized using placeholders: <CURRENT_SCORE>, <PASSING_THRESHOLD>, <TIME_TARGET>, <TIME_PER_ITEM>, <WEAK_TOPICS>, <STRONG_TOPICS>, <QUESTION_TYPE>, <SUBJECT_AREA>, <EXAM_NAME>, <DAILY_MINUTES>, <WEEKEND_HOURS>, <ERROR_LOG_SOURCE>.
- Output format must be plain Markdown with clear phase headers (e.g., '## Weeks 1–2: Baseline & Diagnostic'), zero markdown tables or code blocks.
- Exclude generic advice (e.g., 'stay consistent', 'take breaks') — only include adaptive, evidence-triggered actions and the final week’s non-adaptive, execution-only checklist.
- Never prescribe fixed resources — instead say 'Select practice material aligned with <WEAK_TOPICS> and <TIME_TARGET> constraints'.

## Triggers

- 调整备考重点
- 根据模考成绩优化计划
- 动态调整学习计划
- 每两周复盘考试表现
- 按分数反馈更新复习策略
- 连续停滞时切到错题类型专项
- 最后给考前一周低压力执行清单
- 模考驱动的重点迁移
- 考前一周执行清单
- 最后七天怎么安排
