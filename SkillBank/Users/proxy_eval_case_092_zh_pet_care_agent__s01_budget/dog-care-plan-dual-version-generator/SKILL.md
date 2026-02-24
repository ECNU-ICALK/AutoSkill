---
id: "36b2d9fc-5c0b-4f7e-8dad-f42188cf8ebf"
name: "dog-care-plan-dual-version-generator"
description: "A reusable protocol that generates two synchronized, context-aligned care plans — a daily self-management version and a delegation-ready handover version — both enforcing consistent feeding, walking, grooming, deworming, and weight tracking policies, with embedded clinical escalation rules for appetite decline."
version: "0.1.0"
tags:
  - "pet-care"
  - "delegation"
  - "health-monitoring"
  - "protocol-generation"
  - "clinical-escalation"
triggers:
  - "give me daily and handover versions"
  - "make two versions: one for me, one for the sitter"
  - "generate self-use and delegation plans"
  - "split into owner mode and caregiver mode"
  - "need both personal and handoff checklist"
---

# dog-care-plan-dual-version-generator

A reusable protocol that generates two synchronized, context-aligned care plans — a daily self-management version and a delegation-ready handover version — both enforcing consistent feeding, walking, grooming, deworming, and weight tracking policies, with embedded clinical escalation rules for appetite decline.

## Prompt

# Goal
Generate two parallel, mutually consistent dog care plan versions: (1) a **Daily Self-Management Version**, optimized for owner execution with fixed timing, precise metrics, and behavioral cues; and (2) a **Delegation-Ready Handover Version**, designed for reliable third-party execution with unambiguous instructions, observable success criteria, and embedded clinical escalation triggers — all grounded in the same baseline parameters (e.g., meal grams, walk minutes, deworming schedule, weight baseline).

# Constraints & Style
- Must derive *all* quantitative baselines (e.g., g/meal, kg/weight, min/walk) exclusively from user-provided or previously confirmed values — never invent or estimate.
- The Daily Version must emphasize rhythm, consistency, and subtle behavioral monitoring (e.g., '5+ min free sniffing', 'tail carriage during walk', 'stool texture on Wed').
- The Handover Version must eliminate ambiguity: replace 'as needed' with 'if [observable condition], then [concrete action]'; convert habits into checkable facts (e.g., 'weigh every Sunday at 7am → record value + photo of scale display').
- Both versions must share identical clinical escalation logic for appetite decline: red-line thresholds (e.g., single meal <50% + vomiting), yellow-warning duration (e.g., 2 consecutive sub-70% meals), and mandatory response windows (e.g., 'vet within 2 hours if red-line met').
- Never include brand names, product URLs, or personal identifiers (names, addresses, clinic IDs); use placeholders like <DRUG_NAME>, <VET_CLINIC_CONTACT>, or <WEIGHT_BASELINE_kg>.
- Output format: two clearly labeled Markdown tables or sections — no merged or hybrid layouts.

# Workflow
1. Extract or confirm baseline parameters: feeding amount (g/meal), current weight (kg), walk schedule (times/duration), next deworming date, and appetite decline escalation thresholds.
2. Generate Daily Version: 7-day table with columns for feeding, walking, grooming, deworming, weight tracking, and integrated health observation (e.g., Wednesday as 'Appetite & Stool Check Day').
3. Generate Handover Version: structured by phase (Pre-Handover, During, Post-Return), each with time-bound actions, required artifacts (e.g., 'photo of scale reading'), and decision trees tied to objective signals (e.g., 'if food left >30g AND lip-licking observed → call vet').
4. Cross-validate: ensure all shared elements (e.g., weight measurement protocol, deworming date, meal gram count) match exactly between versions.

## Triggers

- give me daily and handover versions
- make two versions: one for me, one for the sitter
- generate self-use and delegation plans
- split into owner mode and caregiver mode
- need both personal and handoff checklist
