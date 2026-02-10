---
id: "14ec635c-3c0d-40c5-a314-b145c5911f2a"
name: "multi-generational-trip-planner-with-accessibility-rest-and-contingency"
description: "Generates balanced, low-physical-load travel itineraries for families including at least one senior and one child, enforcing strict daily rest slots, minimized walking distance, and embedded weather/transport disruption contingencies — all within a single destination and fixed budget, with zero overnight transfers."
version: "0.1.3"
tags:
  - "accessibility"
  - "family-travel"
  - "senior-friendly"
  - "child-friendly"
  - "budget-travel"
  - "rest-integration"
  - "contingency-planning"
triggers:
  - "plan a family trip with senior and child"
  - "make trip low-walking for elderly and kids"
  - "include daily rest time in itinerary"
  - "avoid overnight transfers"
  - "stay under budget with seniors and children"
  - "add weather fallback and transport delay contingency"
  - "ensure rest remains guaranteed during weather or transit disruption"
  - "make itinerary resilient to real-world hiccups"
  - "generate detailed and summary itinerary formats"
---

# multi-generational-trip-planner-with-accessibility-rest-and-contingency

Generates balanced, low-physical-load travel itineraries for families including at least one senior and one child, enforcing strict daily rest slots, minimized walking distance, and embedded weather/transport disruption contingencies — all within a single destination and fixed budget, with zero overnight transfers.

## Prompt

# Goal
Generate a 7-day family trip itinerary for three generations (1 senior, 1 child, 1+ adult), prioritizing accessibility, comfort, sustainability, and real-world resilience — with zero overnight transfers, total cost ≤ <BUDGET> USD, and explicit weather/transport contingency planning. Output two parallel versions: (1) a *detailed execution version* (Executor View) with full rationale, step counts, rest options, fallback logic, verification sources, and contingency triggers; and (2) a *compact stakeholder summary* (Stakeholder Summary) as a concise, benefit-focused, scannable output highlighting safety, rhythm, and peace of mind — both internally consistent and jointly satisfying all constraints.

# Constraints & Style
- MUST limit cumulative walking per person per day to ≤ 2,000 steps (or ≤ 1.5 km paved/level path); explicitly state step count or path length for every activity — verified via Google Maps pedestrian routing + official ADA-compliant path data or venue accessibility reports (never estimated or approximated).
- MUST include at least one dedicated, non-negotiable rest slot per day: ≥ 90 minutes of seated/low-stimulus downtime in climate-controlled or sheltered settings — named, timed (1:00–2:30 PM), and venue-anchored, with ≥3 concrete, bookable or accessible location options per day (e.g., '<VENUE_NAME> Conservatory', '<HOTEL_NAME> lounge', 'indoor café with reservation'); no vague terms like 'somewhere quiet'.
- MUST avoid stairs, unpaved terrain, standing queues >5 min, unsheltered waits >2 min, and activities requiring sustained attention or mobility beyond gentle ambulation.
- MUST anchor all lodging in one central, accessible location (elevator, ground-floor or suite options, proximity to pharmacy/medical services) — no relocation or multi-hotel stays.
- MUST exclude overnight transfers (no trains, buses, or multi-hour drives between cities/accommodations); all daily activities must be reachable within 25–30 minutes by car or accessible shuttle.
- MUST embed two-tiered weather fallbacks: (i) primary indoor/low-sensory alternative for each outdoor activity (≤10-min drive, ≤600 steps, open daily, no added cost, preserves rest slot), triggered on objective thresholds (e.g., '≥70% rain', '<45°F', '>88°F'); and (ii) secondary 'rest-first' option (e.g., hotel lounge, audiobook in car) if both primary and fallback are compromised.
- MUST embed transport delay buffers: add 45–60 min flexible time before timed entries; specify pre-booked backup transport (e.g., 'Uber WAV confirmation code', 'rental SUV with GPS reroute capability'); list nearest sheltered waiting zones (e.g., café with reservation, covered bus stop with bench) at every transit-dependent location; all transport responses must be instantly actionable, ≤$35 cost, preserve rest slot on schedule, and name exact actions (e.g., 'Open Uber app → Tap WAV → Confirm') and services (e.g., 'DART electric shuttle').
- MUST provide transparent, itemized budget estimate (for <NUM_PEOPLE> people) totaling ≤ <BUDGET> USD — broken into accommodation, transport, food, attractions, and incidentals — with ≥10% explicitly labeled 'Weather/Transport Disruption Buffer' and cost-saving rationale for each category; show explicit buffer remaining.
- MUST not assume airfare; treat airport arrival/departure as single-day logistics (e.g., AVL = 20-min drive).
- MUST use placeholder destination (e.g., <MOUNTAIN-TOWN>, <RIVER-CITY>) and de-identify all case-specific entities: replace actual hotel names with <HOTEL_NAME>, venues with <VENUE_NAME>, URLs with <URL>, dollar amounts with <BUDGET>, dates with <DATE>, and traveler count with <NUM_PEOPLE>.
- MUST omit subjective descriptors (e.g., 'charming', 'magical') and unverifiable claims (e.g., 'world-class accessibility'); cite only observable features (e.g., 'paved paths', 'elevator access', 'timed-entry booking available').
- Language: Clear, compassionate, and directive — avoid hedging ('could', 'might'); use 'will', 'must', 'guarantee'.

# Workflow
1. Confirm destination (if unspecified, propose 1–2 options meeting constraints and ask for selection).
2. Select accessible central accommodation with verified amenities (elevator, breakfast included, room flexibility).
3. For each of 7 days:
   a. Assign one primary activity with ≤ 1.5 km total walkable distance and documented accessibility features;
   b. Insert one mandatory rest slot (≥ 90 min, scheduled 1:00–2:30 PM, ≥3 named, accessible locations);
   c. Assign meals with dietary-flexible, low-wait venues (stroller/senior seating confirmed);
   d. Verify transit time ≤ 30 min from lodging to all locations;
   e. Define primary weather fallback (indoor/low-sensory, ≤10-min drive, ≤600 steps, no added cost, open daily, rest-compatible) and secondary 'rest-first' fallback;
   f. Insert 45–60 min buffer before timed entries; name nearest sheltered wait zone; list pre-booked transport backup (type + reference format) and exact action steps.
4. Compile full budget table with source-aligned estimates, discount logic (senior/child rates, free offerings, bundled savings), and ≥10% 'Weather/Transport Disruption Buffer' line item showing remaining balance.
5. Output both versions: (1) detailed execution version (Executor View) with sections for daily plan, step verification, rest options, fallback logic, contingency table, and booking/action instructions; and (2) compact stakeholder summary (Stakeholder Summary) as a plain-language, benefit-focused, rhythm-emphasizing output (≤120 words) highlighting guarantees — both internally consistent and jointly satisfying all constraints.

## Triggers

- plan a family trip with senior and child
- make trip low-walking for elderly and kids
- include daily rest time in itinerary
- avoid overnight transfers
- stay under budget with seniors and children
- add weather fallback and transport delay contingency
- ensure rest remains guaranteed during weather or transit disruption
- make itinerary resilient to real-world hiccups
- generate detailed and summary itinerary formats
