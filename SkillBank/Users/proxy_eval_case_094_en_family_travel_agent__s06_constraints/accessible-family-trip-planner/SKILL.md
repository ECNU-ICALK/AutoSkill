---
id: "e380428c-219a-4219-8748-a070f1edc45f"
name: "accessible-family-trip-planner"
description: "Generates balanced multi-day family travel itineraries that explicitly accommodate both seniors with mobility considerations and children, while enforcing strict budget, pacing, accessibility, and contingency constraints."
version: "0.1.2"
tags:
  - "travel-planning"
  - "accessibility"
  - "family-travel"
  - "budget-travel"
  - "senior-care"
  - "child-travel"
  - "contingency-planning"
  - "low-mobility"
  - "itinerary"
triggers:
  - "plan a family trip with senior and child"
  - "make a trip accessible for elderly and kids"
  - "budget family vacation under 4000"
  - "reduce walking on family itinerary"
  - "add rest time to travel plan"
  - "add weather fallback and transport delay contingency"
  - "make itinerary resilient to rain or delays"
  - "build rest-first travel plan with contingencies"
  - "plan a resilient family trip with senior and child"
  - "generate weather-and-transport-resilient itinerary"
  - "make a trip plan with built-in rest and fallbacks"
  - "balance senior mobility and child joy in itinerary"
---

# accessible-family-trip-planner

Generates balanced multi-day family travel itineraries that explicitly accommodate both seniors with mobility considerations and children, while enforcing strict budget, pacing, accessibility, and contingency constraints.

## Prompt

# Goal
Generate a detailed, executable 5–7 day family trip plan for 3 people (2 adults + 1 child), explicitly optimized for one senior (65+ with mild-to-moderate mobility needs) and one child (6–10 years old). Output must be a single cohesive itinerary — not options or alternatives.

# Constraints & Style
- Total cost must be ≤ $4,000 USD (all-inclusive: flights, lodging, transport, meals, activities, buffer) — show transparent line-item breakdown with realistic mid-range estimates.
- Zero overnight transfers: all accommodations in one base city; all excursions must be day trips ≤ 1 hour each way by car.
- Strict walking load limitation: no activity requiring > 0.4 miles of total daily walking, all on flat, paved, stroller- and walker-accessible routes with benches or rest points every ≤50 ft; zero stairs required anywhere.
- Mandate daily rest slots: at least one protected 60–90 minute recharge window each afternoon (in-room, shaded outdoor, or quiet lounge — no activity scheduled), explicitly named and timed in the daily schedule; never canceled, shortened, or scheduled over.
- Prioritize venues with verified accessibility: elevators, ground-floor access, accessible restrooms, reservation-supported mobility aids (wheelchairs, electric carts), and staff trained for mixed-age groups.
- Meals must offer concurrent options for soft/low-chew diets (senior) and kid-friendly formats (small portions, familiar foods, high chairs) — name restaurant types known for both, using placeholders like <ACCESSIBLE_RESTAURANT> unless user specifies names.
- Exclude luxury markup unless justified by irreplaceable accessibility features; default to value-optimized but fully accessible alternatives.
- Weather fallbacks must be immediately actionable: for each day, provide one pre-verified, fully accessible indoor/low-effort alternative (same location or ≤5-min drive, no rebooking, no extra cost) triggered by ≥70% rain, heat index ≥90°F, humidity >85%, or mountain fog (<¼ mi visibility).
- Transport delay contingencies must specify: (a) minimum 25-minute buffer before next commitment, (b) nearest covered/waiting location (e.g., hotel lobby, café patio, visitor center), and (c) one zero-prep pivot activity within 1 mile (e.g., museum gallery seating, observation deck bench, pinball cluster); additionally include three layered safeguards: (1) pre-booked WAV ride reserved via hotel concierge, (2) pre-mapped low-elevation alternate route for mountain road closures, and (3) automatic rest-slot advancement if traffic delay >20 mins (monitored via real-time API).
- Never assume unconfirmed preferences (e.g., ‘dinosaur interest’) or walking tolerance beyond seated or <5-min level-ground transitions (e.g., car → bench, door → booth).
- Output in clean Markdown table format for Days 1–7 with columns: Day, Morning, Rest Slot, Afternoon, Evening — plus a final 'Contingency Summary' section listing weather fallbacks and transport pivots per day, using standardized phrasing: 'If [WEATHER ISSUE]: go to <COVERED_FALLBACK_VENUE>. If [TRANSPORT DELAY]: wait at <SHELTERED_WAITING_AREA> and do <PIVOT_ACTIVITY>.'
- Exclude all one-off proper nouns unless user explicitly names them as non-negotiable; use portable placeholders like <ACCESSIBLE_HOTEL>, <COVERED_FALLBACK_VENUE>, <PIVOT_ACTIVITY>.
- Design integratively: all activities, meals, and rest experiences must serve both senior and child concurrently (e.g., shared seated experiences, dual-age-friendly menus, co-engaged activities); do not separate or silo their needs.
- Do not include unconfirmed venues, speculative discounts, or generic advice (e.g., 'check weather'); all fallbacks and contingencies must be pre-verified and actionable.

## Triggers

- plan a family trip with senior and child
- make a trip accessible for elderly and kids
- budget family vacation under 4000
- reduce walking on family itinerary
- add rest time to travel plan
- add weather fallback and transport delay contingency
- make itinerary resilient to rain or delays
- build rest-first travel plan with contingencies
- plan a resilient family trip with senior and child
- generate weather-and-transport-resilient itinerary
