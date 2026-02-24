---
id: "f697cda1-389b-4e0f-8923-9d847f199a58"
name: "multi-generational-trip-planner-with-accessibility-rest-and-contingency"
description: "A skill that generates 7-day family trip itineraries for three generations (senior ≥65, child 6–10, and adults), centered in a single destination, with strict limits on walking distance, mandatory daily rest slots, budget-conscious execution, and built-in weather and transport delay contingencies."
version: "0.1.3"
tags:
  - "accessibility"
  - "family-travel"
  - "contingency-planning"
  - "budget-control"
  - "multi-generational"
  - "low-mobility"
triggers:
  - "plan a family trip with senior and child"
  - "make itinerary accessible for mobility limits"
  - "limit walking and add rest time daily"
  - "keep trip under $<NUM> with no overnight transfers"
  - "balance multi-generational needs"
  - "plan multi-generational trip with weather and delay backup"
---

# multi-generational-trip-planner-with-accessibility-rest-and-contingency

A skill that generates 7-day family trip itineraries for three generations (senior ≥65, child 6–10, and adults), centered in a single destination, with strict limits on walking distance, mandatory daily rest slots, budget-conscious execution, and built-in weather and transport delay contingencies.

## Prompt

# Goal
Generate a 7-day family trip itinerary for 4 people (2 adults, 1 senior ≥65, 1 child aged 6–10), centered in a single destination. Ensure full adherence to five non-negotiable constraints: (1) total walking per day ≤ 0.3 miles (or ≤ 1,200 steps) of flat, paved walking — no stairs, no inclines >2%, no gravel; (2) at least one dedicated 90-minute protected rest slot daily (climate-controlled, no scheduling pressure, preserved across all contingencies); (3) zero overnight transfers — all accommodations and day trips must be within same city/region with same-day return; (4) explicit weather fallback for every scheduled activity (indoor, climate-controlled, equally accessible, same location or <10-min shuttle ride), auto-triggered by objective conditions (e.g., NWS >80% rain / heat index ≥95°F / visibility <¼ mile); and (5) explicit transport delay contingency for every activity (e.g., SLA-backed backup transport, time-flexible version, or on-site 'hub mode' substitute if shuttle delayed >25 mins).

# Constraints & Style
- Prioritize wheelchair/stroller-accessible venues with confirmed elevator/lift access, seating every ≤50 ft, restroom proximity <100 ft, sensory-friendly options, and Flex-Time Pass compatibility — never assume; cite only venues with publicly verified or vendor-confirmed accessibility features.
- Use conservative pacing: no back-to-back scheduled activities; insert buffer time before/after each outing.
- Exclude airfare from budget calculations; enforce strict budget cap (e.g., $3,600–$3,999 USD) — itemize by category (accommodation × 6 nights, meals × 7 days for 4, local transport, admissions, incidentals), verify sum matches target exactly, and state verification status (e.g., "✅ All fallbacks use existing admissions").
- Present cost breakdown in a clear table with categories, assumptions, and mid-range estimates — explicitly call out excluded items (e.g., airfare) and footnote estimated airfare range separately.
- Avoid generic advice (e.g., 'stay hydrated'); instead, embed concrete, actionable accommodations (e.g., 'provide portable folding stool', 'pre-book lift-equipped door-to-door shuttle', 'pack layered clothing and hydration packs').
- Never recommend multi-city routing, long drives (>90 min one-way), or activities requiring sustained standing/walking (e.g., museum marathons, unguided hikes >0.3 miles).
- Use inclusive language: refer to 'senior' and 'child' as distinct, co-prioritized stakeholders — not as afterthoughts to adult preferences.
- Lodging must offer at minimum: roll-in shower option, quiet room location, complimentary portable stool, and concierge 'Rest First' support.
- Local transport must be pre-booked, lift-equipped, door-to-door shuttle service — no rental cars or public transit.
- Use only de-identified destinations (e.g., '<DESTINATION>') and venues (e.g., '<HOTEL>', '<MUSEUM>'); retain only reusable capability markers (e.g., 'Flex-Time Pass', 'Rest First concierge tag') — exclude one-off proper nouns (phone numbers, suite names, staff names).
- Output two parallel versions: (1) a **Detailed Execution Version**, fully elaborated with timing, accessibility specs, cost line items, and contingency logic; and (2) a **Compact Execution Version**, as a clean, scannable, ASCII-friendly, printable table (Day | Morning | 🛋️ Rest Slot | Afternoon | Evening) with fallback icons (🌧️/⏱️) and minimal descriptive text — avoid markdown tables in Compact Version; use plain-space-aligned or pipe-delimited rows suitable for CSV ingestion.
- For ≥3 outdoor-heavy days, assign pre-verified indoor fallbacks meeting all accessibility, cost, and zero-walking criteria — triggered by NWS forecasts (rain >80%, heat index ≥95°F, or visibility <¼ mile).
- All fallbacks and contingencies must be pre-confirmed with partners and referenced via capability (e.g., 'hotel’s Flex-Time Pass network'), not invented.
- Maintain warm, precise, caregiver-aware tone — avoid clinical, bureaucratic, or hedging language (no 'may', 'could', disclaimers); all claims must be operationally binding.

# Workflow
1. Confirm destination feasibility: verify walkability score, medical infrastructure proximity, availability of accessible shuttles/vans, and mild seasonal climate.
2. Select one fully accessible base accommodation (suite-style, roll-in shower option, quiet location, complimentary portable stool, concierge 'Rest First' support) with on-site amenities to minimize external transit.
3. Build daily schedule with: (a) max one primary outing, (b) built-in 90-min protected rest slot at biologically appropriate time (e.g., post-lunch or mid-afternoon), (c) ≤0.3 miles total walking (track via venue-provided path maps or Google Maps wheelchair routing), (d) meal timing aligned with energy rhythms (e.g., early dinner if child naps late), (e) weather fallback (indoor, climate-controlled, equally accessible, same location or <10-min shuttle), and (f) transport delay contingency (time-flexible, abbreviated, or on-site substitute if shuttle delayed >25 mins).
4. Calculate and validate full cost against budget cap — itemize by category, apply verified discounts (senior/child), flag estimates as 'conservative' or 'range-based', and confirm all fallbacks incur zero added cost.
5. Output final plan with explicit accessibility notes per activity (e.g., 'Biltmore House: elevators to 3 floors; audio tour available in large-print'), rest-slot justification (e.g., 'Day 3 PM: 90-min in-room wind-down post-museum — includes storytime + snack'), and contingency icons (🌧️ for weather fallback, ⏱️ for delay contingency, 🛋️ for rest slot).

## Triggers

- plan a family trip with senior and child
- make itinerary accessible for mobility limits
- limit walking and add rest time daily
- keep trip under $<NUM> with no overnight transfers
- balance multi-generational needs
- plan multi-generational trip with weather and delay backup
