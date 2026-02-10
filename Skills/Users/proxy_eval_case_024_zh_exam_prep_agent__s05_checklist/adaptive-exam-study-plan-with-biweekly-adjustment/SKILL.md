---
id: "511e5c8c-0eec-4812-bdcb-05abdc8d936d"
name: "adaptive-exam-study-plan-with-biweekly-and-stagnation-adjustment"
description: "Generates a time-bound, phase-structured professional exam study plan (e.g., 14 weeks) with scheduled biweekly adjustments based on mock exam performance, plus an escalation protocol that triggers error-type- or module-specific targeted interventions when consecutive mocks show stagnation (≤±2–3% score/accuracy change and persistent underperformance in a defined domain or error type)."
version: "0.1.2"
tags:
  - "study-planning"
  - "adaptive-learning"
  - "exam-prep"
  - "feedback-loop"
  - "time-budgeting"
  - "error-analysis"
  - "data-driven-learning"
triggers:
  - "adjust study plan every two weeks"
  - "update prep focus based on mock scores"
  - "biweekly exam plan recalibration"
  - "adapt schedule using practice test results"
  - "adjust study plan when mock scores stall"
  - "switch to error-type or module-specific practice on stagnation"
  - "detect consecutive low improvement in mocks"
---

# adaptive-exam-study-plan-with-biweekly-and-stagnation-adjustment

Generates a time-bound, phase-structured professional exam study plan (e.g., 14 weeks) with scheduled biweekly adjustments based on mock exam performance, plus an escalation protocol that triggers error-type- or module-specific targeted interventions when consecutive mocks show stagnation (≤±2–3% score/accuracy change and persistent underperformance in a defined domain or error type).

## Prompt

# Goal
Generate a 14-week professional exam study plan with two-tiered adaptation: (1) routine biweekly adjustment after Weeks 2, 4, 6, 8, 10, and 12 based on the most recent mock exam score and diagnostic feedback; and (2) stagnation-triggered escalation that overrides standard rules when ≥2 consecutive mocks show ≤±2% absolute score change *or* ≤±3% module/question-type accuracy change *and* no improvement relative to a user-provided target threshold (e.g., <TARGET_ACCURACY>) — while also showing persistent dominance of a specific error type (e.g., 'unit conversion errors appear in >65% of calculation mistakes') or persistent underperformance in a specific knowledge module (e.g., '<MODULE_NAME> accuracy remains < 60%').

# Constraints & Style
- Must preserve the foundational 4-phase structure: (1) Weeks 1–2: diagnostic + framework; (2) Weeks 3–8: modular deep work + error analysis; (3) Weeks 9–11: timed full-length practice; (4) Weeks 12–14: high-yield review + test-day conditioning.
- Biweekly adjustment must be explicit: for each checkpoint, specify (a) interpretation of mock score and diagnostic dimensions (e.g., module accuracy, timing, error clustering), (b) reprioritization of content domains or skill types, and (c) reallocation of time within the fixed weekly budget (e.g., reduce theory review by 20%, add 30 mins/day targeted practice).
- Stagnation detection must compare the two most recent mocks for both score/accuracy delta *and* domain- or error-type-level persistence; if criteria are met, mandate a minimum 3-day focused intervention on the *specific error type* or *knowledge module* — including concrete exercise format (e.g., '5 timed unit-conversion chains/day'), time-boxing (e.g., <INTERVENTION_DURATION>), and a discrete success checkpoint (e.g., '≥90% accuracy on 10-item drill for 2 consecutive days' or 'pass 5-question lightning quiz at 100%').
- Do not invent scoring thresholds, domain taxonomies, diagnostic dimensions, or error taxonomies — use only categories and benchmarks the user provides (e.g., 'case analysis', 'regulation recall', 'calculation speed', 'interference item misselection').
- All time allocations must respect the user’s hard constraints: weekday 90 min (ideally split), weekend max 4 hours (with built-in breaks and active recall); adjustments affect *content emphasis*, *resource selection*, and *practice format* — never total hours or phase duration.
- Include a dedicated 'Adjustment Log' column in the weekly table showing: prior mock score, observed gaps, stagnation status, and concrete changes made for the next cycle.
- Never assume exam name, syllabus, or baseline — keep all domain references placeholder-driven (e.g., <EXAM_NAME>, <WEAK_MODULE>, <MOCK_SCORE>, <ERROR_TYPE>, <MODULE_NAME>, <TARGET_ACCURACY>, <INTERVENTION_DURATION>).
- Exclude subjective advice (e.g., 'stay motivated'), generic study tips, or unmeasurable directives (e.g., 'review thoroughly'); only include rules driven by quantifiable metrics and discrete actions.
- Final output must be fully de-identified: no proper nouns, platform names, app names, or proprietary tool references — replace with neutral descriptors (e.g., 'a free mobile practice app with auto-graded reports', 'a spreadsheet template that highlights declining trends') unless user explicitly named them as required tools.

## Triggers

- adjust study plan every two weeks
- update prep focus based on mock scores
- biweekly exam plan recalibration
- adapt schedule using practice test results
- adjust study plan when mock scores stall
- switch to error-type or module-specific practice on stagnation
- detect consecutive low improvement in mocks
