---
id: "9d756ef0-f12f-4ccd-8483-fc9a8813b287"
name: "wedding-payment-schedule-planning"
description: "Creates structured milestone-based payment schedules for wedding vendors within a specified budget cap, ensuring phased allocations across key service categories."
version: "0.1.0"
tags:
  - "budgeting"
  - "payment milestones"
  - "vendor management"
  - "wedding planning"
triggers:
  - "set payment milestones"
  - "budget allocation by vendor"
  - "track wedding payments"
---

# wedding-payment-schedule-planning

Creates structured milestone-based payment schedules for wedding vendors within a specified budget cap, ensuring phased allocations across key service categories.

## Prompt

# Goal
Develop a payment milestone framework for wedding vendors that adheres to a maximum budget while defining deposit, interim, and final payment stages per service category.

# Constraints & Style
- Must enforce <BUDGET_TOTAL> budget cap through proportional allocation
- Require 3 payment phases per vendor node: deposit (30-60%), pre-wedding installment (20-40%), post-wedding settlement (10-20%)
- Mandate milestone verification against service scope (e.g., venue walkthrough, menu tasting, final proofs)
- Exclude one-time fixed costs from phased payments (e.g., stationery design fees)
- Track adjustments for guest count fluctuations (±5% tolerance)

# Workflow
1. Parse vendor categories from planning scope
2. Assign phase percentages based on service criticality
3. Map payment dates to planning timeline milestones
4. Generate verification checkpoints for each phase

## Triggers

- set payment milestones
- budget allocation by vendor
- track wedding payments
