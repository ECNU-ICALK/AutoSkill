---
id: "a7cd6df3-da30-452e-85d2-78b6c1adc18c"
name: "budget-and-transfer-constraints-trip-planning"
description: "Creates multi-day travel itineraries that stay within strict budget limits while incorporating accessibility constraints (minimal walking load, scheduled rest periods) and comprehensive contingency planning for weather, transport delays, and emergencies."
version: "0.1.1"
tags:
  - "travel-planning"
  - "budget-constraints"
  - "accessibility"
  - "family-travel"
  - "budgeting"
  - "contingency-planning"
  - "travel"
  - "risk-management"
triggers:
  - "Keep budget below"
  - "avoid overnight transfers"
  - "family trip with budget constraints"
  - "same-day travel only"
  - "budget-constrained travel plan"
  - "accessible family itinerary"
  - "weather transportation contingencies"
  - "emergency fallback planning"
  - "multi-format itinerary output"
---

# budget-and-transfer-constraints-trip-planning

Creates multi-day travel itineraries that stay within strict budget limits while incorporating accessibility constraints (minimal walking load, scheduled rest periods) and comprehensive contingency planning for weather, transport delays, and emergencies.

## Prompt

# Goal
Generate a detailed travel itinerary that stays within user-specified budget, accommodates accessibility needs for diverse audiences, and includes weather, transport, and emergency contingency branches.

# Constraints & Style
- Budget cap must be respected with clear cost breakdown and adjustment options
- Walking load strictly limited with scheduled rest slots (2-3 per day, 30-45 minutes each)
- Weather fallback: Every outdoor activity must have indoor alternative with cost estimates
- Transport contingency: Backup options for every transfer (public transit, alternative destinations)
- Emergency branch: Protocols for cancellations, delays, and budget overruns with tiered responses
- Accessibility features: Wheelchair/stroller access, shaded seating, flat terrain, senior/child-friendly options
- Multi-format output: Detailed version with full descriptions AND compact quick-reference version
- No overnight transfers; all activities within same-day travel radius

# Workflow
1. Budget breakdown with category allocations and flexible adjustment points
2. Daily itinerary with time slots, walking load assessment, and rest period scheduling
3. Contingency mapping for each activity (weather, transport, emergency branches)
4. Detailed version generation with full descriptions and accessibility notes
5. Compact version creation with actionable steps, costs, and contingency triggers
6. Validation against budget cap and accessibility constraints

## Triggers

- Keep budget below
- avoid overnight transfers
- family trip with budget constraints
- same-day travel only
- budget-constrained travel plan
- accessible family itinerary
- weather transportation contingencies
- emergency fallback planning
- multi-format itinerary output
