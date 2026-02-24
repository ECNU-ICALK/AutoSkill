---
id: "42e6e89d-2a36-492d-9568-d2cab3729dfb"
name: "residential-renovation-budget-and-materials-policy"
description: "A reusable skill for generating home renovation plans that strictly adhere to a user-specified total budget cap and enforce hard constraints on main material selection: certified environmental safety (e.g., formaldehyde/VOC limits) and verified durability (e.g., warranty duration, industry-standard lifespan). Applies to two-bedroom apartments under standard urban conditions."
version: "0.1.0"
tags:
  - "renovation"
  - "budget-control"
  - "material-specification"
  - "environmental-compliance"
  - "durability"
triggers:
  - "budget cap"
  - "main materials must be eco-friendly"
  - "durable materials required"
  - "material环保 and long-lasting"
  - "max spend and certified quality"
---

# residential-renovation-budget-and-materials-policy

A reusable skill for generating home renovation plans that strictly adhere to a user-specified total budget cap and enforce hard constraints on main material selection: certified environmental safety (e.g., formaldehyde/VOC limits) and verified durability (e.g., warranty duration, industry-standard lifespan). Applies to two-bedroom apartments under standard urban conditions.

## Prompt

# Goal
Generate a phased, executable home renovation plan (e.g., 70-day schedule) for a two-bedroom apartment, where all cost estimates and material specifications comply with two non-negotiable user constraints: (1) total project cost ≤ <BUDGET> (e.g., ¥180,000), and (2) all main materials (tiles, flooring, cabinets, paint, sanitary ware) must meet documented environmental safety standards (e.g., E1/E0 formaldehyde rating, VOC ≤ 50 g/L) and minimum durability thresholds (e.g., ≥25-year structural warranty for cabinets, ≥10-year waterproofing warranty for bathrooms).

# Constraints & Style
- ✅ MUST calculate and allocate budget across phases (demolition, MEP, tiling, carpentry, painting, installation, finishing) — no phase may exceed its prorated share without explicit trade-off justification.
- ✅ MUST name only mainstream, widely available brands/models with public certification data (e.g., 'Dulux AirPure净味系列', 'Kronospan E0 MDF', 'Häfele soft-close hinges') — never generic terms like 'high-end tile' or 'eco-friendly paint'.
- ✅ MUST cite verifiable compliance evidence for each main material: e.g., 'CMA test report No. XXX shows formaldehyde emission = 0.024 mg/m³ (<0.03 mg/m³ limit per GB/T 18883)', or 'Product warranty card states 25-year cabinet frame guarantee'.
- ❌ MUST NOT assume labor discounts, bulk deals, or unverified 'premium' substitutions unless user explicitly approves them.
- ❌ MUST NOT omit cost drivers: e.g., custom cabinet lead time impacts cash flow timing; low-VOC paint costs ~20% more but avoids rework from off-gassing delays.
- Output format: Markdown table per phase, with columns: Days, Work, Budget Allocation (¥), Approved Materials (with cert/warranty), Compliance Evidence.

# Workflow
None — this is a constraint-enforcement policy, not a multi-stage AI operation.

## Triggers

- budget cap
- main materials must be eco-friendly
- durable materials required
- material环保 and long-lasting
- max spend and certified quality
