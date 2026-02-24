---
id: "9c927aa0-e62e-4b79-bdbc-1213ccbf8332"
name: "adaptive-study-plan-with-assessment-and-contingency"
description: "A reusable skill for dynamically adjusting a study plan based on periodic assessment data while incorporating pre-defined, mutually exclusive contingency branches for real-world disruptions including exam cancellation, delay, or resource/budget overrun."
version: "0.1.2"
tags:
  - "study-planning"
  - "adaptive-learning"
  - "assessment-driven"
  - "error-analysis"
  - "exam-prep"
  - "contingency"
  - "cognitive-load-management"
triggers:
  - "当模考分数连续两次无提升时"
  - "检测到学习停滞"
  - "错题类型重复出现"
  - "每两周根据模考分数调整重点"
  - "最后给考前一周低压力执行清单"
  - "考试临时取消"
  - "考试延期"
  - "预算超支"
  - "资源不可用"
  - "计划需应急调整"
---

# adaptive-study-plan-with-assessment-and-contingency

A reusable skill for dynamically adjusting a study plan based on periodic assessment data while incorporating pre-defined, mutually exclusive contingency branches for real-world disruptions including exam cancellation, delay, or resource/budget overrun.

## Prompt

# Goal
Adjust a multi-week study plan in real time using objective assessment data — detect stagnation (two consecutive mock exams with ≤+2% score gain and/or ≥70% recurrence of same error type) or recurring error patterns, then apply one of three evidence-based interventions: (1) topic-weight rebalancing every two weeks, (2) error-type-specific '专项' drill upon confirmed stagnation, or (3) low-cognitive-load execution mode during the final week before an exam. Additionally, embed three explicit, mutually exclusive contingency branches for: (a) exam cancellation, (b) exam delay, (c) resource/budget overrun — each triggered only by user-confirmed condition and executed *instead* of forward-looking schedule changes.

# Constraints & Style
- Trigger primary adjustments only on objective, quantifiable data: (a) subject score change ≤ ±2% across two consecutive timed mock exams AND below 90% of target passing score; OR (b) identical error type (e.g., 'conceptual confusion', 'unit conversion omission') appearing ≥3 times across mocks.
- All interventions must preserve the user’s fixed time budget: workdays = 90 minutes/day, weekends = ≤4 hours/day.
- Final-week plan must contain zero new content, zero timed drills, and zero open-ended tasks — only retrieval practice, error-pattern rehearsal, and ritualized rehearsal (e.g., re-reading annotated summaries, verbalizing key frameworks, scanning flashcards).
- Output adjustments as concrete, executable task shifts — not abstract advice. Example: 'Replace Week 7 Day 3 “read chapter 5” with “rework 5 high-frequency legal clause mismatch problems using dual-column justification template”'.
- Never invent scoring thresholds, subject weightings, resource links, or error taxonomies — rely only on observed scoring trends and documented error patterns from prior diagnostics.
- Do not override core weekly structure — insert remediation *within* existing time blocks (e.g., replace one review session with专项 drill).
- Intervention must be error-type-specific, not topic-generic: e.g., 'repeated misapplication of Bayes’ theorem in probability word problems', not 'study statistics more'.
- Output adjustment must name the exact error category, prescribe a bounded activity (≤30 min/day for 3–5 days), and reference a concrete practice resource (e.g., '5 targeted items from [Resource ID] focusing on conditional vs. joint probability framing').
- Contingency branches must be mutually exclusive, each triggered by a single confirmed condition ('exam cancelled', 'new date: <DATE>', 'budget exceeded'), and specify: immediate action (≤2 steps), duration impact (pause/extend/compress), and resource reallocation (e.g., shift to maintenance mode, activate archive review, suspend non-core modules).
- All output must remain strictly time-bound and role-agnostic: no proper nouns, no dates, no platform names, no tool-specific syntax.
- Keep total length ≤ 1 page; use tables or bullet lists only; avoid paragraphs.
- Never introduce new learning objectives, topics, or external resources in any branch.
- When a contingency is active, discard all forward-looking schedule changes and output only the next 7-day actionable block (D-7 to D-1 style), fully adapted to the branch’s constraints.

# Workflow
1. After each scheduled mock exam, compute per-subject % score and tag all errors by type (using user-defined or co-developed taxonomy).
2. Compare against prior mock: if stagnation criteria are met, activate ‘error-type专项’ workflow (including diagnosis → focused resource → deliberate practice → verification).
3. Every two weeks (after mocks at W2/W4/W6/etc.), rebalance upcoming week’s task allocation using weighted priority: (1 − current_score / target_score) × topic_weight.
4. In the final 7 days before exam date, auto-switch to pre-defined low-pressure execution list: only retrieval practice, error-pattern rehearsal, and environmental priming (e.g., 'simulate exam start time').
5. Before applying any forward-looking adjustment, check for active disruption signal — if present, execute only the matching contingency branch and output only the next 7-day actionable block.

## Triggers

- 当模考分数连续两次无提升时
- 检测到学习停滞
- 错题类型重复出现
- 每两周根据模考分数调整重点
- 最后给考前一周低压力执行清单
- 考试临时取消
- 考试延期
- 预算超支
- 资源不可用
- 计划需应急调整
