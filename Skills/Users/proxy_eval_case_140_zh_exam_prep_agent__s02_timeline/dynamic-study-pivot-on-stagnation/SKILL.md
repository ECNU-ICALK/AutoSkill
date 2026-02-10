---
id: "f0819151-1bcb-4669-be19-efc176e2fe73"
name: "dynamic-study-pivot-on-stagnation"
description: "A reusable study adaptation rule that triggers a focused shift to error-type-specific practice when performance plateaus across consecutive assessments."
version: "0.1.2"
tags:
  - "adaptive-learning"
  - "error-analysis"
  - "study-pivot"
  - "performance-monitoring"
  - "micro-intervention"
  - "plateau-response"
triggers:
  - "连续停滞时切到错题类型专项"
  - "成绩卡在平台期就专攻错因"
  - "两次模考没进步就锁定一类错误猛练"
  - "分数不动就换打法，只打一种错"
---

# dynamic-study-pivot-on-stagnation

A reusable study adaptation rule that triggers a focused shift to error-type-specific practice when performance plateaus across consecutive assessments.

## Prompt

# Goal
Automatically pivot from broad topic review to targeted, high-yield practice on a specific error type (e.g., 'misapplied formula', 'inference beyond text', 'time-pressure omission') when the user's score or mastery metric shows no improvement across two or more consecutive scheduled assessments.

# Constraints & Style
- Must trigger only on objective evidence of stagnation: (a) ≤±3% absolute score change in same question type/knowledge point across two consecutive timed assessments (e.g., 模考, quizzes), OR (b) ≥2 identical error patterns observed in daily practice sessions over 3 consecutive days, OR (c) user self-reports subjective stagnation (e.g., 'I understand the solution but can’t reproduce it').
- Must not assume *why* stagnation occurred—only respond to observed lack of progress in quantifiable output (e.g., 模考分数, quiz accuracy, timed task completion rate) or validated self-report.
- Pivot must be narrow: isolate *one* dominant error category per pivot, mapped strictly to one of four validated taxonomy categories: [Knowledge Gap / Process Error / Attention Lapse / Strategy Mismatch] OR [concept-confusion / process-blockage / calculation-repetition / memory-fuzziness]; do not invent new types.
- Each pivot includes exactly three components: (1) 15–20 minutes of diagnostic re-attempt on 3 representative items, (2) 10 minutes of root-cause annotation using the fixed 4-category taxonomy, and (3) 25 minutes of deliberate, scaffolded repetition of that *exact* error type — all using only previously introduced materials and formats.
- All interventions must be time-bound: ≤20 minutes for weekday execution (e.g., 3×15-minute blocks); weekend deep-dive variants may extend up to 2 hours but must include a built-in verification step (e.g., 3-item post-test, oral recitation, checklist sign-off).
- Never extend pivot duration beyond one session unless explicitly re-triggered by another stagnation signal.
- Do not introduce new content, tools, or resources during the pivot — only reuse previously introduced materials, formats, and optionally reference pre-validated tooling (e.g., 'Use Anki flashcard set: error-type-calc-npv-v2').
- Output must include: (1) diagnosed error type, (2) exact intervention steps, (3) verification method, and (4) optional tool reference.

# Workflow
1. Monitor assessment results for two consecutive cycles (e.g., Week 4 & Week 6 模考, or Quiz A & Quiz B) OR analyze daily practice logs for ≥2 identical error patterns across 3 consecutive days OR accept validated self-report.
2. If absolute score change ≤ ±3% *and* no sub-skill domain shows ≥10% gain, or if ≥2 identical error patterns are confirmed, or if self-report is provided, flag as 'stagnation'.
3. Identify the single highest-frequency error type from the most recent assessment’s error log or practice session artifacts (question stem, answer attempt, correct answer, timing context).
4. Classify into one of the four validated error categories using linguistic/logical/structural features (e.g., misused temporal clause, omitted constraint, swapped actor-action pairing).
5. Execute the three-part pivot sequence (diagnostic → annotation → repetition) in the next scheduled study block, embedding it as a replaceable 'elastic slot' without displacing core weekly goals.
6. Reset monitoring window: next stagnation check begins after this pivot session.

## Triggers

- 连续停滞时切到错题类型专项
- 成绩卡在平台期就专攻错因
- 两次模考没进步就锁定一类错误猛练
- 分数不动就换打法，只打一种错
