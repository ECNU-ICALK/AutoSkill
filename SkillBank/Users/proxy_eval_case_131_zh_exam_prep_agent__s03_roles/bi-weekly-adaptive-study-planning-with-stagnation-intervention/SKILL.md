---
id: "9bd44bcc-8733-4697-b964-d97df8fbb441"
name: "bi-weekly-adaptive-study-planning-with-stagnation-intervention"
description: "A reusable study planning capability that dynamically adjusts focus every two weeks based on mock exam scores, and triggers targeted remediation for persistent performance plateaus by switching to error-type-specific drills."
version: "0.1.1"
tags:
  - "adaptive-planning"
  - "exam-prep"
  - "performance-feedback"
  - "error-analysis"
  - "intervention-protocol"
  - "study-optimization"
triggers:
  - "adjust study focus every two weeks"
  - "switch to error-type practice"
  - "handle stagnant mock scores"
  - "adapt plan based on performance data"
  - "trigger specialized drills on plateau"
---

# bi-weekly-adaptive-study-planning-with-stagnation-intervention

A reusable study planning capability that dynamically adjusts focus every two weeks based on mock exam scores, and triggers targeted remediation for persistent performance plateaus by switching to error-type-specific drills.

## Prompt

# Goal
Generate a 14-week exam preparation plan that adapts every two weeks using mock exam results, and automatically shifts to error-type-focused practice when performance stagnates across consecutive assessments.

# Constraints & Style
- Must enforce a strict bi-weekly cycle: each cycle ends with a timed, exam-fidelity mock test.
- After each mock, analyze score trends *by question type or subtopic* (not just total score) to identify low-yield/high-weight areas; shift ≥20% of upcoming study time toward those areas.
- Define 'stagnation' as either (a) ≥2 consecutive days with ≥40% error rate on the same question type, OR (b) ≥3 consecutive mock attempts with <±2 point score variance in the same scored module.
- If stagnation is detected in ≥1 category, immediately replace the next cycle’s core study block with a dedicated, time-boxed 'error-type专项包' containing: one principle refresher, three annotated exemplar problems, and two guided practice items — all scoped to the exact error pattern (e.g., 'C3-审题漏条件').
- Preserve the user’s fixed time budget: maintain 90 min/day on weekdays and ≤4 hrs/day on weekends — reallocate time *within* those bounds (e.g., reduce theory review by 30%, add 30 min daily error-type drill).
- Output must be fully de-identified: use placeholders <EXAM_NAME>, <CURRENT_BASELINE>, and <TARGET_DATE>; never assume exam name, content, baseline, or date.
- Include a dedicated low-pressure execution checklist for the final week before <TARGET_DATE>, containing only maintenance activities: light review, error-pattern scanning, timing calibration, and psychological readiness prompts — zero new content or drilling.
- Never invent scoring rubrics, subject matter, or resource links; reference only generic, reusable assets (e.g., '错题归因速查表', '思维断层自查清单').
- Never assume exam name, content, or baseline — require explicit user input before generating any schedule.
- Output must be self-contained: include only adaptive logic, not static templates or generic advice.

# Workflow
1. Confirm <EXAM_NAME>, <CURRENT_BASELINE>, and <TARGET_DATE> from user input.
2. Initialize 14-week skeleton with four bi-weekly cycles (C1–C4), each ending in a diagnostic mock at Weeks 2, 4, 6, and 14.
3. After Mock C1 and Mock C2: compare per-category scores; if stagnation detected in ≥1 category, activate error-type specialization in C3.
4. After Mock C3: re-evaluate all categories; if stagnation persists or shifts, update specialization in C4 accordingly.
5. Embed explicit 'stagnation trigger' and 'switch action' markers in the plan (e.g., '⚠️ Stagnation detected in “calculation accuracy” → C3 Days 1–3: 25-min targeted drill + error log review').

## Triggers

- adjust study focus every two weeks
- switch to error-type practice
- handle stagnant mock scores
- adapt plan based on performance data
- trigger specialized drills on plateau
