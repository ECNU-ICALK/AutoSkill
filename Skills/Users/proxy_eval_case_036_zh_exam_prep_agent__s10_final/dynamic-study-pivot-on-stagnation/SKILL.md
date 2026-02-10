---
id: "c33b6d9a-bd5e-4972-9775-15c343ad37be"
name: "dynamic-study-pivot-on-stagnation"
description: "A reusable skill that triggers an immediate shift from scheduled content to targeted practice on the specific question type(s) causing persistent performance plateaus, based on objective progress metrics."
version: "0.1.2"
tags:
  - "adaptive-learning"
  - "performance-pivot"
  - "error-driven-practice"
  - "exam-prep"
  - "question-type-focus"
  - "data-triggered"
  - "low-cognition"
  - "check-pointed"
triggers:
  - "当连续模考某题型正确率不提升时"
  - "学习停滞时切到错题类型专项"
  - "连续两次卡在同一类题上"
---

# dynamic-study-pivot-on-stagnation

A reusable skill that triggers an immediate shift from scheduled content to targeted practice on the specific question type(s) causing persistent performance plateaus, based on objective progress metrics.

## Prompt

# Goal
Automatically pivot the study plan to a focused, time-boxed专项 (specialized drill) on the exact question type(s) identified as causing consecutive stagnant or declining performance in timed assessments.

# Constraints & Style
- Pivot only when two or more consecutive full-length or module-level timed assessments show no improvement (≤±3% absolute score change) and absolute accuracy < 60% for a specific question type (e.g., 'multi-step calculation with unit conversion', 'jurisdictional conflict analysis', 'pedagogical scenario matching').
- The专项 must be strictly limited to that question type — no mixed-topic practice, no bundling, no expansion to related topics.
- All materials must be de-identified: replace exam-specific names with <EXAM_MODULE>, statutes/cases with <KEY_RULE> or <GOVERNING_PRINCIPLE>, and session duration with <SESSION_DURATION>.
- Use only questions, analysis data, and notes from the user’s own prior assessments — no new content, explanations, theories, or external resources.
- Must include explicit self-diagnosis step before starting: user identifies *why* this type fails (e.g., 'misreads conditional phrasing', 'fails to map facts to rule', 'runs out of time before final step').
- Never pivot based on subjective frustration, self-reported effort, or single low score — require objective, quantified stagnation across at least two assessments.
- Cap total intervention to 3–5 days, with daily commitment strictly 45–90 minutes (<SESSION_DURATION>), segmented into fixed blocks (e.g., 25+25+25 min) each with binary observable check points (e.g., 'Circle 3 trigger words', 'Write 1-sentence fix', 'Complete 3 timed items').
- Do not introduce motivational content, resource recommendations, or open-ended reflection without concrete anchors.

# Workflow
1. Monitor assessment results for repeated low/flat performance on a discrete question type.
2. Confirm stagnation meets the two-assessment threshold and is isolated to one type (or max two if tied).
3. Pause current syllabus progression.
4. Launch专项: (a) re-attempt 3 prior incorrect items of that type, (b) annotate error root cause, (c) apply one verified correction strategy, (d) attempt 3 new parallel items under timed conditions.
5. Log outcome: accuracy delta, time delta, and root-cause refinement.
6. Resume main plan only after success criteria are met: ≥15% accuracy gain *or* two consecutive sessions with ≥10% improvement *or* ≥75% accuracy on a 3-item timed mini-check.

## Triggers

- 当连续模考某题型正确率不提升时
- 学习停滞时切到错题类型专项
- 连续两次卡在同一类题上
