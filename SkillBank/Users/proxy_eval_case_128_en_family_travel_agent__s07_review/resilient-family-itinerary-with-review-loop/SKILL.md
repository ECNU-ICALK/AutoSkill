---
id: "c49e3240-8201-4225-b14e-24f0ff7a611b"
name: "resilient-family-itinerary-with-review-loop"
description: "Generates executable, accessibility-first multi-day family itineraries (3–7 days) for mixed-age groups including at least one senior (65+) and one child (6–10), enforcing strict daily walking limits (≤2,000 verified steps), mandatory timed rest slots, pre-validated weather and transport delay contingencies, and a built-in weekly review loop with objective metrics and automatic adjustment rules — all centered on a single accessible base location."
version: "0.1.3"
tags:
  - "accessibility"
  - "family-travel"
  - "itinerary-planning"
  - "rest-optimization"
  - "contingency-planning"
  - "weather-resilience"
  - "transport-flexibility"
  - "review-loop"
  - "resilience"
triggers:
  - "plan a family trip with senior and child"
  - "limit walking for mixed-age group"
  - "add rest breaks to itinerary"
  - "make trip accessible for mobility needs"
  - "balance activity and recovery daily"
  - "add weather fallback to family itinerary"
  - "include transport delay contingency"
  - "make rest slots resilient to disruptions"
  - "plan for mixed-age group with weather sensitivity"
  - "build adaptable accessibility into trip plan"
  - "provide both detailed and compact execution versions"
  - "generate rest-resilient itinerary"
  - "add weather and delay contingencies to family plan"
  - "output dual-format accessible itinerary"
  - "balance rigor and usability in trip planning"
  - "add weekly review to family itinerary"
  - "adjust itinerary based on rest adherence"
  - "review walking load mid-trip"
  - "build feedback loop into accessible travel plan"
  - "make family itinerary self-correcting"
---

# resilient-family-itinerary-with-review-loop

Generates executable, accessibility-first multi-day family itineraries (3–7 days) for mixed-age groups including at least one senior (65+) and one child (6–10), enforcing strict daily walking limits (≤2,000 verified steps), mandatory timed rest slots, pre-validated weather and transport delay contingencies, and a built-in weekly review loop with objective metrics and automatic adjustment rules — all centered on a single accessible base location.

## Prompt

# Goal
Generate a detailed, executable multi-day family trip itinerary (3–7 days) for a group including at least one senior (65+) and one child (6–10), centered on a single accessible base lodging. Enforce three non-negotiable operational constraints: (1) daily walking load capped at ≤2,000 steps per person, calculated *only* from verified accessible path routing (ramps, elevators, flat pavers) via Google Maps pedestrian directions — never estimated; (2) two mandatory, timed rest slots per day — each ≥30 minutes, seated, low-stimulus, logistically feasible (e.g., café patio, shaded park bench, hotel lounge), with explicit location name, seating type, environmental features (e.g., 'shade', 'AC', 'misting'), and accessibility notes (e.g., 'benches every 50 ft', 'no threshold'); (3) pre-validated weather fallbacks and transport delay contingencies for each day that preserve rest timing, step count, energy budget, emotional continuity, and total cost cap — plus a built-in weekly review loop with objective pass/fail metrics and automatic adjustment rules.

# Constraints & Style
- All activities must be reachable via flat, paved, or ramp-accessible paths; no stairs-only access, steep inclines (>5% slope), or unpaved trails.
- Prioritize venues with verified accessibility features: on-site wheelchairs/strollers, grab bars, seating every ≤100 ft, quiet zones, and climate-appropriate shelter.
- Never assume mobility — explicitly state path surface type (e.g., 'smooth concrete', 'compact gravel'), slope (<5%), and distance between rest points.
- Output must include a step-count column in the daily itinerary table, derived from official trail maps or Google Maps walking directions (shortest accessible route).
- Rest slots must be named (e.g., 'Maple Street Café Pause', 'Hotel Garden Bench Reset') and assigned fixed start/end times — and preserved *identically* across all variants (original, weather, delay).
- For each day, include:
  • A primary weather fallback (e.g., indoor museum extension, café-based activity, hotel amenity swap) activated if rain chance ≥70%, wind >20 mph, or temperature <45°F / >88°F — must be fully indoor, ≤5-min shuttle/walk from base lodging, ADA-compliant, zero added cost, and already budgeted.
  • A transport delay contingency (e.g., 'if van tour runs 25+ mins late, shift afternoon session to on-site quiet lounge + extend Rest Slot #2 by 20 mins') — must preserve rest timing, step count, energy budget, include real-time adjustment, 45-min pace buffer (never cut rest or activity), emergency ride reserve (e.g., Uber WAV, $22 covered in incidentals), and 'stay put' hotel-based enrichment.
- Weekly review loop must include: (a) three objective midweek (Day 3–4) metrics: average daily steps, rest slot adherence %, and fallback usage count; (b) pass/fail thresholds: steps >2,000 → fail; rest adherence <100% → fail; ≥2 fallbacks used → trigger full review; (c) adjustment rules: if fail, reduce next day’s AM activity duration by 30 min *and* add 15 min to both rest slots — no exceptions.
- Exclude all overnight transfers, flights, or multi-hotel stays — single base location only.
- Budget cap is $4,000 USD total for up to 4 people; exclude airfare unless user specifies origin airport. All fallbacks, contingencies, and review-triggered adjustments must remain within this cap and draw exclusively from original budget allocation (e.g., activity buffer, incidentals).
- Use neutral, inclusive language — avoid ageist terms (e.g., 'elderly-friendly'); say 'step-free', 'seating-dense', 'pace-adaptive', or 'climate-resilient'.
- Do not invent attractions, hotels, or services — only use verifiably existing, publicly listed options with documented accessibility features.
- Replace case-specific proper nouns with generic descriptors (e.g., 'historic hillside resort with accessible rooms', 'local chocolate lounge with outdoor patio', 'regional nature center with loaner wheelchairs').
- Use placeholders for location-specific inputs: <DESTINATION>, <FAMILY_COMPOSITION>, <TRAVEL_DATES>, <WEATHER_FORECAST>, <TRANSPORT_MODE>, <BASE_LODGING>, <GROUP_PROFILE>, <DURATION>, <BUDGET>.
- Output in two parallel versions: (a) a *detailed execution version* (structured with tables, explicit timing, venue accessibility notes, step counts, rest location specs, contingency triggers, and review metrics); and (b) a *compact execution version* (single-column, icon-driven, time-anchored cards — one per day — with only essential cues: activity name, start/end times, rest icons 🪑×2, step count badge, fallback trigger symbol 🌧️/🚗, and review status indicator 🔁). Both versions must contain identical constraints, metrics, and rules — and the compact version must fit on one A4/Letter page with clear visual hierarchy (bold headers, emoji cues, minimal text).

## Triggers

- plan a family trip with senior and child
- limit walking for mixed-age group
- add rest breaks to itinerary
- make trip accessible for mobility needs
- balance activity and recovery daily
- add weather fallback to family itinerary
- include transport delay contingency
- make rest slots resilient to disruptions
- plan for mixed-age group with weather sensitivity
- build adaptable accessibility into trip plan
