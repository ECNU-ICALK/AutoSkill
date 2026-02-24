---
id: "615e7945-fa96-4116-bd0b-91c6cc1b9ae2"
name: "adaptive-study-plan-adjustment-by-stagnation"
description: "A reusable skill for dynamically adjusting study focus when progress stalls, using objective performance and process signals to trigger targeted, time-boxed remediation on error patterns — embedded within a dual-week iterative planning framework with mandatory weekly review."
version: "0.1.1"
tags:
  - "study-planning"
  - "adaptive-learning"
  - "error-analysis"
  - "performance-monitoring"
  - "intervention-design"
  - "review-routine"
triggers:
  - "when progress stalls"
  - "if scores don't improve"
  - "when stuck on same error"
  - "after repeated mistakes"
  - "if no gain across two tests"
  - "weekly review and adjustment"
  - "stagnation-triggered intervention"
  - "performance-based study recalibration"
---

# adaptive-study-plan-adjustment-by-stagnation

A reusable skill for dynamically adjusting study focus when progress stalls, using objective performance and process signals to trigger targeted, time-boxed remediation on error patterns — embedded within a dual-week iterative planning framework with mandatory weekly review.

## Prompt

# Goal
Adjust study priorities in real time when learning progress stagnates — specifically by detecting consecutive unimproved performance or incomplete error closure on a given question type, then activating a focused, evidence-based intervention; embed this logic within a dual-week iterative plan that enforces structured weekly review to calibrate focus, effort, and resource allocation.

# Constraints & Style
- Must trigger only after **two or more consecutive assessment cycles** (spaced ≥3 days apart) show **no improvement** (e.g., same or lower accuracy, unchanged time-per-question, repeated identical errors) on a specific question type — OR after **≥3 consecutive days** of incomplete daily error annotation/completion (<80% completion rate).
- The intervention must be **type-specific and time-boxed (≤20 minutes)**: e.g., if 'calculation errors in time-value-of-money problems' recur, activate a 3-step drill (identify step → isolate arithmetic → verify unit logic); do NOT re-teach full content or broaden scope.
- All actions must be observable, self-verifiable, and avoid subjective language (e.g., no 'try harder', 'review basics', or 'practice more').
- Weekly review is a discrete, scheduled step (e.g., every Sunday evening) with three fixed components: (i) modality check (what was *actually* done vs. planned), (ii) metric triage (which KPIs shifted meaningfully: accuracy? timing? completion rate?), and (iii) rule-governed adjustment (e.g., 'if <QUESTION_TYPE> error recurrence >2x, replace next week’s input video with self-explanation protocol').
- Output must name the stalled question type or process gap, cite the evidence of stagnation (e.g., '<QUESTION_TYPE> accuracy: 40% → 35% → 40% over 3 assessments'), prescribe one validated remediation method matched to the error class (memory/understanding/application/misreading), and specify the next review checkpoint (after exactly 3 practice attempts or 5 days — whichever comes first).
- Use placeholders for runtime inputs: <QUESTION_TYPE>, <ASSESSMENT_KPI>, <DAILY_TASK_COMPLETION_RATE>, <WEEKLY_METRIC_THRESHOLD>.
- Do NOT introduce new taxonomies, tools, rubrics, or external references — preserve only user-originated logic and terminology.

# Workflow
1. Monitor assessment results per question type (grouped by cognitive demand and format, not just subject label) and track daily error annotation/completion rates.
2. Flag any question type where performance metrics plateau or regress across ≥2 spaced assessments — OR flag any process metric (e.g., error closure rate) falling below threshold for ≥3 consecutive days.
3. Classify the dominant error pattern (e.g., 'misapplied formula', 'ignored constraint clause', 'unit conversion omission') or process failure mode.
4. Activate the pre-mapped remediation protocol for that pattern:
   - Memory failure → spaced retrieval + self-explanation prompt
   - Conceptual gap → minimal-example contrast table + 1-sentence definition test
   - Application flaw → scaffolded reconstruction (solve → hide → reconstruct steps → compare)
   - Misreading → annotation protocol (underline constraint, circle action verb, box output target) + timed re-read drill
5. Schedule next check-in after exactly 3 practice attempts or 5 days — whichever comes first.
6. Conduct weekly review with modality check, metric triage, and rule-governed adjustment — output as labeled temporal slots (e.g., 'Weekend Day 2', 'Post-Monday Review Slot').

## Triggers

- when progress stalls
- if scores don't improve
- when stuck on same error
- after repeated mistakes
- if no gain across two tests
- weekly review and adjustment
- stagnation-triggered intervention
- performance-based study recalibration
