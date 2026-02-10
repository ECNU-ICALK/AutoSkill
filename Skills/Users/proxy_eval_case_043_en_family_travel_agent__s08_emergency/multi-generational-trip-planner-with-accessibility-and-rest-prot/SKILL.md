---
id: "a4d334b1-e2b1-4023-bcdb-af59422fa6c3"
name: "resilient-multi-generational-trip-planner-with-accessibility-rest-contingencies"
description: "Generates balanced, accessible 7-day family trip itineraries for mixed-age groups (e.g., seniors and children), enforcing strict walking load limits (≤500 m/day on paved, ADA-compliant paths), mandatory daily rest slots (≥90 minutes, 1:30–3:00 PM), and three-tiered contingency planning — weather fallbacks, transport delay pivots, and an explicit emergency branch for cancellations, schedule collapse, or budget overruns — all within a fixed budget cap and zero overnight transfers."
version: "0.1.3"
tags:
  - "accessibility"
  - "family-travel"
  - "itinerary-planning"
  - "senior-travel"
  - "child-travel"
  - "contingency-planning"
  - "weather-resilience"
  - "budget-control"
  - "emergency-response"
triggers:
  - "plan a family trip with senior and child"
  - "make itinerary accessible for mixed ages"
  - "limit walking on family vacation"
  - "add rest time to travel plan"
  - "avoid overnight transfers in trip design"
  - "add weather fallback to family itinerary"
  - "include transport delay contingency in trip plan"
  - "add emergency branch to itinerary"
  - "handle cancellation or budget overrun in travel plan"
  - "make multi-gen trip resilient to rain heat delays and schedule collapse"
---

# resilient-multi-generational-trip-planner-with-accessibility-rest-contingencies

Generates balanced, accessible 7-day family trip itineraries for mixed-age groups (e.g., seniors and children), enforcing strict walking load limits (≤500 m/day on paved, ADA-compliant paths), mandatory daily rest slots (≥90 minutes, 1:30–3:00 PM), and three-tiered contingency planning — weather fallbacks, transport delay pivots, and an explicit emergency branch for cancellations, schedule collapse, or budget overruns — all within a fixed budget cap and zero overnight transfers.

## Prompt

# Goal
Generate a 7-day family trip itinerary for a group including at least one senior and one child (~7 years), centered in a single base city (no overnight transfers), with all day trips returning same-day (<90 min each way). Output must include: (1) a daily schedule with timed activities, (2) explicit walking load annotations (e.g., '≤500m total flat walking', 'no stairs', 'stroller/wheelchair accessible', 'benches every ≤200m', 'paved path <1% grade', 'shade/cover options'), (3) a dedicated, non-optional daily rest slot of ≥90 minutes — labeled clearly as 'Rest Slot' — scheduled between 1:30–3:00 PM with ≥3 interchangeable, seated, low-sensory, zero-transition options (e.g., hotel lounge time, quiet reading, pool relaxation), and (4) for every outdoor activity, an explicitly named indoor, climate-controlled weather fallback (≤50 yd walk, same-zone, open daily) viable in rain (≥70% forecast), heat (≥85°F or UV ≥8), cold (<45°F), or fog/low visibility; a transport delay contingency (actionable pivot ≤10 min, ≤100 yd walk, e.g., 'If ride-hailing >25 min late, switch to pre-booked ART bus route #7 with ramp access'); and an explicit emergency branch for full/partial activity cancellation, multi-hour schedule collapse, or projected budget overrun (>2% of total), specifying: (a) immediate de-escalation action (e.g., return to hotel for rest + recalibration), (b) pre-identified zero-cost or negative-cost recovery options (e.g., free museum days, complimentary hotel amenities), (c) budget reallocation rules (e.g., shift funds from incidentals → lodging; cap overspend at $0 via pre-locked line-item ceilings), and (d) one-touch contact escalation path (e.g., concierge, rental desk) with script-ready phrasing — all pre-verified, budgeted, and requiring no rebooking or extra payment.

# Constraints & Style
- Must keep total estimated cost under <BUDGET_CAP> USD for <GROUP_COMPOSITION> (e.g., 2 adults, 1 senior, 1 child), excluding flights unless specified; if flights included, assume realistic mid-week, non-peak pricing and apply AARP/AAA discounts where applicable. All cost line items must map transparently to budget categories (flights, lodging, car, meals, activities, incidentals, local transport) using only publicly verifiable unit costs.
- All lodging must be in one accessible, centrally located base (elevator access, ground-floor or suite options, proximity to dining/transport).
- Zero overnight transfers: no hotels or stays outside the base city; all excursions are same-day return.
- Walking load per day must be explicitly quantified and minimized: prioritize paved, flat, short-loop trails (<0.5 mi), avoid stairs/unpaved paths, and annotate accessibility features (e.g., 'rental electric cart available', 'restrooms/benches every 200m', 'bench density ≥1 per 100 yds', 'shade/cover options').
- Daily rest slot must be scheduled, named ('Rest Slot'), and ≥90 minutes — not optional, not bundled with meals or transit, and not replaced by 'flex time' or 'Plan B'.
- Use neutral, inclusive language: avoid ageist assumptions; instead, specify functional accommodations (e.g., 'seated engagement options', 'shade access', 'hydration points').
- Exclude generic advice (e.g., 'pack sunscreen') unless tied to a specific scheduled activity.
- Do not invent attractions, policies, or pricing not grounded in widely verifiable public data.
- For every outdoor activity, specify an indoor, accessible, same-location weather fallback viable in rain, heat (>85°F), cold (<45°F), or fog/low visibility; prioritize climate-controlled, shaded, or covered spaces.
- Do not assume seasonal weather stability or unconfirmed accessibility features (e.g., 'elevator available') unless verified by official source or user-provided reference.
- Use only de-identified locations (e.g., 'downtown cultural center', 'botanical garden with paved loop', 'historic village with flat brick paths'); omit proper nouns unless essential to accessibility and budgeted.
- Output two parallel versions: (1) a **detailed execution version**, including timing, accessibility specs (benches, ramps, restrooms), booking notes, contingency triggers, and emergency branch logic; and (2) a **compact execution version**, formatted as a clean, scannable table (Day | Morning | Rest Slot | Afternoon | Weather Fallback | Delay Pivot | Emergency Trigger) with icons (☔/☀️/🌫️/🛑) and ≤12 words per cell.
- Prioritize clarity over charm: avoid emoticons, excessive branding, or promotional language. Retain only functional descriptors (e.g., 'zero-entry ramp', 'AC lobby with couches', 'pre-loaded Uber WAV code').
- All contingencies — weather fallbacks, transport delay pivots, and emergency branch actions — must be specific, pre-validated, named, locationally anchored, and confirmable (e.g., timed entry reserved, app code saved, route tested); no unbooked or hypothetical options.
- Budget must be fixed, itemized, and internally consistent (e.g., $3,965 total with $120 incidentals covering all cushions, kits, credits, and emergency picnic); no unaccounted assumptions.

## Triggers

- plan a family trip with senior and child
- make itinerary accessible for mixed ages
- limit walking on family vacation
- add rest time to travel plan
- avoid overnight transfers in trip design
- add weather fallback to family itinerary
- include transport delay contingency in trip plan
- add emergency branch to itinerary
- handle cancellation or budget overrun in travel plan
- make multi-gen trip resilient to rain heat delays and schedule collapse
