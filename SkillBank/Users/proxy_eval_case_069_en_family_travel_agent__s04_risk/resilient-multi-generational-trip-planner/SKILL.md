---
id: "402fb8ec-bbec-4106-9a31-c211de20bd04"
name: "resilient-multi-generational-trip-planner"
description: "A reusable skill for planning 5–7 day family trips that simultaneously accommodate seniors (65+) and children (≤12), enforce strict budget caps (e.g., <$4,000 USD for up to 4 people), eliminate overnight transfers, minimize walking load (≤0.3 miles/day on flat, paved, shaded paths), embed mandatory daily rest slots with explicit environmental specifications, and include pre-vetted, zero-cost weather fallbacks and transport delay contingencies — all without increasing cost or physical demand."
version: "0.1.3"
tags:
  - "travel-planning"
  - "accessibility"
  - "budgeting"
  - "family-travel"
  - "multi-generational"
  - "contingency-planning"
triggers:
  - "plan a family trip with senior and child"
  - "7-day trip under <NUM> USD"
  - "limit walking and add rest breaks"
  - "add weather fallback and transport delay contingency"
  - "accessible multi-generational travel with transport delay plan"
---

# resilient-multi-generational-trip-planner

A reusable skill for planning 5–7 day family trips that simultaneously accommodate seniors (65+) and children (≤12), enforce strict budget caps (e.g., <$4,000 USD for up to 4 people), eliminate overnight transfers, minimize walking load (≤0.3 miles/day on flat, paved, shaded paths), embed mandatory daily rest slots with explicit environmental specifications, and include pre-vetted, zero-cost weather fallbacks and transport delay contingencies — all without increasing cost or physical demand.

## Prompt

# Goal
Generate a fully resilient, accessible 5–7 day family itinerary for 2 adults, 1 senior (65+), and 1 child (≤12), with strict adherence to: (1) total budget cap ≤ $4,000 USD for up to 4 people; (2) no overnight transfers (same-day arrival/departure, zero hotel changes); (3) ≤0.3 miles total walking per person per day on flat, paved, shaded surfaces with ≥1 rest option per 50 ft; (4) non-negotiable 90-minute daily rest slot labeled 'Recharge Break', specifying climate control/shade level, seating type (armchairs/rocking chairs/beanbags), hydration/snack access, and sensory accommodations (low light/sound, quiet toys, medication timing support); and (5) integrated, pre-validated, zero-additional-cost weather fallbacks and transport delay contingencies.

# Constraints & Style
- Prioritize accessibility: flat, paved, shaded paths only; no stairs, steep grades (>2%), gravel, or timed entry. All venues must offer ADA-compliant parking, ≥1 accessible restroom, ≥3 benches within 100 ft of entry, roll-in showers or nearby accessible restrooms, grab bars, staff readiness for accommodation requests (e.g., folding stools, shaded patio meet-and-greet), and quiet/low-stimulation options.
- Walking load capped: ≤3,000 steps (≈0.3 miles) per person per day — calculate and state estimated step count and longest single walk; justify as flat/shaded/benched; if uncertain, default to '≤2,500 steps' and flag as conservative. Longest single walk must be fully flat, shaded, and offer ≥1 rest option per 50 ft.
- Budget breakdown must be itemized by category (flights, lodging, transport, meals, activities, incidentals), use realistic off-peak pricing (spring/fall), cite source logic (e.g., "Holiday Inn avg $189/night in October per Booking.com"), and sum to ≤$3,950 with ≥$50 buffer.
- All locations must be within 15 minutes’ drive of central lodging (<15 min radius); zero backtracking or multi-hour road trips; all activities within ≤1 hour of base lodging; no activity requires >$200 total entry cost for 4 people or >15 min continuous walking/stairs/queuing without seated options.
- Every activity must offer a pre-bookable, drop-off-to-activity option (ride-share, shuttle, or staff meet-and-greet); no parking-lot walks >100 ft.
- For each outdoor activity, provide exactly one same-day, same-location, zero-additional-cost indoor alternative (e.g., museum wing, library program, hotel amenity) — verified free or included with original admission, fully accessible, requiring ≤0.05 mi additional walking, labeled "☔ Weather Fallback:" and activated on objective triggers (e.g., heat index ≥86°F, rain ≥70%, wind >20 mph).
- For every scheduled ride-share, shuttle, or rental vehicle use, specify: (a) max wait time before triggering fallback, (b) immediate low-effort alternative (e.g., reschedule activity, activate weather fallback, extend rest slot), and (c) vendor communication script (e.g., "We’re running 12 min late due to traffic — please hold our spot or confirm new ETA"), labeled "⏱️ Transport Contingency:". Transport backups must be pre-vetted, same-zone (<0.4 mi radius), covered waiting zones, or hybrid walk-and-ride segments (<0.1 mi each), all within existing transport budget.
- Exclude all attractions requiring unconfirmed accessibility features — if not verifiably documented (e.g., on official site or ADA map), omit or flag as "unconfirmed — call ahead".
- Use neutral, inclusive language — avoid age-based assumptions (e.g., say 'mobility-aware' not 'elderly-friendly'); refer to 'senior' and 'child' consistently.
- Output two versions: (1) a detailed execution plan (for pre-trip prep), including justification, venue notes, and contingency logic; and (2) a compact 1-page cheat sheet (for on-the-ground use), tabular and scannable, with walking totals, rest timing, quick-reference keys for weather swaps and delay protocols, and all fallbacks/contingencies embedded inline.
- Never invent venue names, addresses, pricing, or unconfirmed accessibility features — only include what is publicly verifiable or pre-confirmed via official channels.
- Top-3 cross-cutting risks (e.g., heat stress, mobility fatigue, schedule fragmentation) must be explicitly named and paired with specific, operational mitigations tied to concrete actions, locations, or tools (e.g., 'Risk: Heat-induced fatigue → Mitigation: Auto-swap Day 2 to Asheville Art Museum + provide cooling towel kit').
- Use placeholders <BUDGET_CAP>, <LODGING_NAME>, <ARRIVAL_AIRPORT>, <SOURCE_LODGING>, <TARGET_CITY> for de-identification; omit real URLs, phone numbers, or proprietary service names (e.g., say "NOAA micro-forecast link" not full URL).

## Triggers

- plan a family trip with senior and child
- 7-day trip under <NUM> USD
- limit walking and add rest breaks
- add weather fallback and transport delay contingency
- accessible multi-generational travel with transport delay plan
