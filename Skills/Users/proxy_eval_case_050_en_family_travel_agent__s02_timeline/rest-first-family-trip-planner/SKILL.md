---
id: "d71f4cda-32d6-4a98-83ba-47e6909eb04e"
name: "rest-first-family-trip-planner"
description: "A reusable itinerary planning skill that enforces strict walking limits (≤400 ft/day, ≤80 ft continuous), guarantees named daily rest slots with sensory anchors, and embeds pre-validated weather fallbacks and transport delay contingencies — all while staying within a hard budget cap and avoiding overnight transfers."
version: "0.1.1"
tags:
  - "itinerary"
  - "accessibility"
  - "contingency"
  - "family"
  - "budget"
  - "rest-first"
triggers:
  - "plan a multigenerational trip"
  - "build a low-walking family itinerary"
  - "add weather and delay contingencies"
  - "enforce daily rest slots"
  - "stay under budget with no overnight stays"
---

# rest-first-family-trip-planner

A reusable itinerary planning skill that enforces strict walking limits (≤400 ft/day, ≤80 ft continuous), guarantees named daily rest slots with sensory anchors, and embeds pre-validated weather fallbacks and transport delay contingencies — all while staying within a hard budget cap and avoiding overnight transfers.

## Prompt

# Goal
Generate a 7-day family trip itinerary for mixed-age groups (senior + child) that satisfies four non-negotiable constraints: (1) total cost ≤ $4,000 USD for 4 people; (2) zero overnight transfers (all lodging in one location, day trips ≤90 mins round-trip); (3) cumulative walking load ≤ 400 ft/day, with no segment exceeding 80 ft and all paths fully paved, bench-lined, step-free, and slope <5%; (4) one named, 60-minute daily rest slot featuring a sensory anchor (e.g., warm drink, tactile object, guided audio, shared journaling or creative act) in a climate-controlled, seated, quiet, staff-supported setting.

# Constraints & Style
- Must include explicit weather fallback: For any outdoor activity, specify an *immediately accessible, indoor or sheltered, step-free, climate-controlled alternative* (e.g., museum, science center, accessible theater lounge) with ≤10-min drive from the original location — pre-validated, same-day, no extra cost or booking upgrade required.
- Must include transport delay contingency: For every scheduled activity requiring external transport (rental car, shuttle, Uber WAV, ART bus), define a *buffer protocol*: (a) if delay ≥15 min, auto-swap to next lower-effort activity at same location or hotel; (b) if delay ≥30 min, activate pre-approved rest slot early — no rescheduling or rushing.
- All cost estimates must be itemized by category (accommodation, transport, food, activities, misc.) and sum to ≤$3,990 to preserve $10 buffer.
- Never assume stairs, standing duration, unshaded exposure, or unassisted navigation. Prioritize seated, shaded, AC/heated, staff-supported, and elevator/ramp-accessible options.
- Output two parallel versions: (1) a *detailed execution version* (table with columns [Day, Morning, ✅ Rest Slot, Afternoon, Weather Fallback, Delay Protocol], plus "Walking Load Summary" and "Contingency Notes"); (2) a *compact execution version* (one line per day: "[Day X] [Core activity] → [Rest slot name] → [Fallback trigger] → [Delay response]").
- Language: Clear, directive, third-person, de-identified — no proper nouns (e.g., use "downtown-accessible hotel" not "Hilton Garden Inn"); replace specific vendors with functional descriptors (e.g., "botanical garden with discovery train", "elevator-equipped historic estate village").
- Never include prices, dates, URLs, emails, phone numbers, or real-time booking links — those are runtime inputs, not skill logic.
- Rest slots must be *named*, *sensory-grounded*, and *staff-supported* (e.g., "Cloud-Gazing Pause", "Pinball Pause") — never generic "free time".
- Prioritize clarity over creativity: avoid metaphors, emojis, or decorative formatting in the compact version; retain only functional labels.

# Workflow
1. Confirm destination meets baseline criteria: walkable core, medical access, flat terrain, and ≥3 free/low-cost indoor rain options within 5-min drive.
2. Assign daily rest slot first — name it, assign sensory anchor, and lock its time/location before scheduling any activity.
3. Build morning/afternoon blocks around rest — each must be reachable via ≤80 ft of walking from rest location or transport drop-off.
4. For each outdoor activity, append weather fallback in parentheses (e.g., "Craggy Gardens overlook (fallback: Asheville Museum of Science — elevator access, hands-on exhibits, AC)").
5. For each transport-dependent activity, append delay protocol (e.g., "Biltmore shuttle (delay ≥15 min → activate Vineyard Veranda Break early; ≥30 min → move rest to hotel lobby with tea service)").
6. Validate walking totals, cost sum, and zero overnight transfers before finalizing.

## Triggers

- plan a multigenerational trip
- build a low-walking family itinerary
- add weather and delay contingencies
- enforce daily rest slots
- stay under budget with no overnight stays
