---
id: "0edf0f21-9d73-4f9f-bf75-494471fa87d8"
name: "low-pressure-final-week-daily-checklist"
description: "Generates a concise, time-boxed, day-by-day execution checklist for the final week before a professional exam — optimized for cognitive load reduction, confidence anchoring, and physiological readiness, with no new content or practice."
version: "0.1.0"
tags:
  - "exam-prep"
  - "time-boxed"
  - "low-cognition"
  - "execution-only"
  - "pre-test-routine"
triggers:
  - "final week checklist"
  - "last 7 days study plan"
  - "low stress exam prep"
  - "daily pre-exam routine"
  - "concise exam countdown"
---

# low-pressure-final-week-daily-checklist

Generates a concise, time-boxed, day-by-day execution checklist for the final week before a professional exam — optimized for cognitive load reduction, confidence anchoring, and physiological readiness, with no new content or practice.

## Prompt

# Goal
Generate a single-column, ultra-concise daily checklist for the 7 days before a professional exam (D-7 to D-1), where each day contains exactly one core action, a strict time cap (≤90 min total), and zero open-ended tasks.

# Constraints & Style
- Output only plain Markdown table (no headers, no explanations, no science notes, no emojis, no extra text).
- Columns: | Day | Action | Time |
- 'Day' = 'D-7' through 'D-1'; use abbreviated weekday only if unambiguous (e.g., 'Mon', 'Tue').
- 'Action' = imperative, verb-led, concrete, tool-free (no app/tool names, no references to external resources), and fully self-contained (e.g., 'Read all question stems from last 3 years’ exams — do not solve').
- 'Time' = integer minutes only (e.g., '45'), no ranges, no qualifiers.
- No markdown formatting beyond pipe-table syntax; no bold/italics/lists.
- Strictly omit: rationale, principles, examples, variants, triggers, warnings, or any explanatory clause.
- All content must be de-identified: no exam names, subjects, modules, or domain-specific terms (e.g., avoid 'PMP', '教资', '法规', 'BAC').
- If input includes exam name or domain cues, ignore them — output generic version only.
- Maximum 7 rows. No blank rows.

## Triggers

- final week checklist
- last 7 days study plan
- low stress exam prep
- daily pre-exam routine
- concise exam countdown
