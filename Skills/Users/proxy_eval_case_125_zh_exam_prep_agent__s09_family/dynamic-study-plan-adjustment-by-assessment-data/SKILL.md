---
id: "a2fadada-02c8-4077-b77f-8b1a88bde0d6"
name: "dynamic-study-plan-adjustment-by-assessment-data"
description: "A reusable skill for iteratively refining a study plan based on periodic assessment results, using objective performance metrics to trigger targeted interventions — and generating two aligned, audience-specific versions: one simplified for family support, one fully actionable for learner execution."
version: "0.1.2"
tags:
  - "study-planning"
  - "assessment-driven"
  - "adaptive-learning"
  - "error-analysis"
  - "time-constrained"
  - "exam-prep"
  - "audience-adaptation"
  - "execution-clarity"
triggers:
  - "adjust study plan after mock exam"
  - "respond to stagnant scores"
  - "shift focus to error-type practice"
  - "reallocate study time based on data"
  - "trigger specialized remediation"
  - "prepare final-week low-stress execution"
  - "give family-friendly study summary"
  - "create learner-executable schedule"
  - "dual-audience plan output"
---

# dynamic-study-plan-adjustment-by-assessment-data

A reusable skill for iteratively refining a study plan based on periodic assessment results, using objective performance metrics to trigger targeted interventions — and generating two aligned, audience-specific versions: one simplified for family support, one fully actionable for learner execution.

## Prompt

# Goal
Adjust a multi-week study plan in real time by analyzing biweekly mock exam scores and error patterns, then automatically reprioritizing learning focus to address emerging weaknesses — anchored to a fixed exam date via backward scheduling. Generate two semantically aligned but lexically distinct versions: (1) a concise, jargon-free summary for family members highlighting only support needs and boundaries, and (2) a fully executable, time-anchored version for daily self-execution with precise resources and action verbs.

# Constraints & Style
- Must trigger adjustment every two weeks strictly on mock exam results — no ad-hoc changes without assessment data.
- When performance stagnates (e.g., same or lower module score across ≥2 consecutive mocks *and* <5% accuracy improvement while remaining below domain-specific threshold like <DOMAIN_THRESHOLD>), immediately shift focus to *error-type-specific* remediation — not broad topic review. Classify errors into types: ❗conceptual gap, ⚠️memory confusion, ❌procedural flaw, 💥execution lapse.
- Prioritize interventions by error type frequency and impact: e.g., if "❌procedural flaw" dominates in math problem-solving, replace general practice with stepwise method drills + worked-example shadowing.
- Never extend total weekly study time; reallocate existing hours only — preserve the user’s fixed capacity (e.g., 15.5 hrs/week).
- Output adjustments as concrete, executable micro-tasks (e.g., "30-min concept map on X", "5-varied problems with solution annotation", "record 90-sec self-explanation of Y logic") — no vague directives like 'review better' or 'practice more'.
- Final week (Week 14) must contain *only* a low-cognitive-load execution checklist: no new content, no timed drills, no self-assessment scoring — only restorative, confidence-sustaining actions (e.g., 're-read your personal success log', 'organize exam-day kit', 'listen to 1 recorded self-explanation audio'), formatted as a bulleted, zero-decision checklist.
- Family version: ≤150 words; zero pedagogical terms; use plain language (e.g., 'practice test', 'stuck area', 'final week wind-down'); highlight only what family should know/do (e.g., 'please protect quiet time Tue/Thu 7–8:30pm', 'no new topics after D-7').
- Execution version: time-bound (AM/PM/day labels), resource-specific (e.g., 'p. 42 of <TEXTBOOK>', '<VIDEO_MODULE> 02:15–03:05'), action-verb driven ('re-solve', 'hand-draw', 'record aloud'); includes *only* tasks derived from the original 14-week logic.
- Both versions must reflect the three core policies: (1) biweekly adjustment based on mock results, (2) error-type escalation upon stagnation, (3) strict low-cognitive-load protocol for final 7 days.
- Never invent exam names, dates, personal context, or resources; use placeholders <EXAM_NAME>, <EXAM_DATE>, <DOMAIN_THRESHOLD>, <STAGNATION_MODULE>, <TEXTBOOK>, <VIDEO_MODULE> where needed.
- Exclude all motivational language, emojis, markdown decorations, or assistant self-reference.
- No overlap in wording: versions must be semantically parallel but lexically distinct.

## Triggers

- adjust study plan after mock exam
- respond to stagnant scores
- shift focus to error-type practice
- reallocate study time based on data
- trigger specialized remediation
- prepare final-week low-stress execution
- give family-friendly study summary
- create learner-executable schedule
- dual-audience plan output
