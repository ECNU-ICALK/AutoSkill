---
id: "fe08c2af-de8b-42de-893c-df712571b8ac"
name: "adaptive-exam-study-plan-with-biweekly-adjustment"
description: "Generates a time-bound exam study plan that incorporates scheduled biweekly diagnostic assessments and dynamically reallocates focus areas based on resulting performance data."
version: "0.1.1"
tags:
  - "exam-prep"
  - "adaptive-planning"
  - "assessment-driven"
  - "time-boxed"
  - "feedback-loop"
  - "error-analysis"
triggers:
  - "adjust study plan every two weeks"
  - "update focus based on mock scores"
  - "biweekly exam-based revision"
  - "reallocate study time after模考"
  - "adapt plan using test results"
---

# adaptive-exam-study-plan-with-biweekly-adjustment

Generates a time-bound exam study plan that incorporates scheduled biweekly diagnostic assessments and dynamically reallocates focus areas based on resulting performance data.

## Prompt

# Goal
Generate a structured, time-boxed exam preparation plan (e.g., 14 weeks) that includes fixed biweekly milestones for full-length or modular simulated exams, and explicitly defines how subsequent study priorities must be revised based on those scores — not as optional advice, but as a required adaptation rule.

# Constraints & Style
- Must schedule exactly 6 biweekly mock exams at fixed intervals (Weeks 2, 4, 6, 8, 10, 12), with progressive fidelity: early mocks = single-module; later mocks = full-syllabus + timed + simulated interface.
- Must embed exactly one explicit adjustment trigger: "Every two weeks, after completing a timed, full-syllabus or modular mock exam, re-prioritize the next two weeks’ study focus strictly according to the lowest-scoring domain or question type from that exam."
- Must define objective stagnation triggers: (a) same knowledge domain or question type scoring ≤55% on two consecutive mocks; OR (b) ≥2 daily 'stuck' markers in self-reported review cards over 3 consecutive days.
- Upon trigger, replace planned content with a targeted 'error-type专项' (e.g., 'concept-confusion', 'misreading-trap', 'context-transfer') — not generic re-teaching.
- Do not assume or invent scoring thresholds, weightings, or domain taxonomies — only enforce feedback-driven reallocation logic.
- Exclude all generic study tips (e.g., 'take breaks', 'review notes') unless directly tied to the biweekly adjustment mechanism or final-week execution.
- Output must include: (a) fixed timing of mock exams, (b) clear instruction for score-based reprioritization, (c) placeholder for domain/question-type names (e.g., <WEAKEST_DOMAIN>, <QUESTION_TYPE>), and (d) a standalone 'Final Week Low-Pressure Execution Checklist' containing only: 3x 20-min active recall sessions (<TOPIC_A>, <TOPIC_B>, <TOPIC_C>), 1x 45-min timed mini-mock (50% length), and 3x 'confidence anchoring' prompts.
- Never generate adaptive logic without anchoring it to the biweekly cadence and mock-based evidence.
- Exclude all exam-specific content (names, syllabi, formulas, laws); use placeholders like <EXAM_NAME>, <DOMAIN>, <QUESTION_TYPE>, <TOTAL_WEEKS>.
- Output must be fully de-identified: no proper nouns, dates, tools, platforms, or personal identifiers.

# Workflow
1. Confirm total duration (e.g., 14 weeks) and exam name (to scope syllabus); otherwise retain as <TOTAL_WEEKS> and <EXAM_NAME>.
2. Schedule full-length or modular mock exams at fixed biweekly intervals (Week 2, 4, 6, 8, 10, 12), increasing fidelity over time.
3. For each post-mock phase (e.g., Weeks 3–4), mandate that study emphasis shifts exclusively to the lowest-performing domain or question type identified in the prior mock.
4. Apply rule-based priority shift: if domain X fails twice → increase its next-week weight by ≥20%, decrease highest-scoring domain’s weight proportionally.
5. Reserve elastic 'adjustment days' (e.g., Weeks 3, 7, 11) for error-type专项.
6. For each mock, auto-generate a diagnosis template: [Knowledge Domain], [Error Type], [Self-Rated Mastery (1–5★)], [Time Spent per Item].
7. Append a pre-defined 'Final Week Low-Pressure Execution Checklist' — no new content; only activation of recall, timing calibration, and cognitive ease rituals.

## Triggers

- adjust study plan every two weeks
- update focus based on mock scores
- biweekly exam-based revision
- reallocate study time after模考
- adapt plan using test results
