---
id: "65a15a8c-de10-4cb0-aaa2-47edc6263523"
name: "multi-generational-trip-planner-with-accessibility-rest-and-contingency"
description: "A skill that generates balanced, low-physical-load itineraries for families spanning three generations (senior, child, adults), enforcing strict daily rest slots, minimized walking distance, verified accessibility, and explicit weather and transport delay contingencies for real-world reliability."
version: "0.1.3"
tags:
  - "travel-planning"
  - "accessibility"
  - "multi-generational"
  - "rest-first"
  - "contingency"
  - "weather-resilient"
  - "transport-reliable"
  - "low-step"
triggers:
  - "plan a multi-generational trip with rest and contingencies"
  - "family trip with senior and child and weather backup"
  - "low-walking accessible itinerary with transport delay plan"
  - "three-generation travel plan with real-world reliability"
  - "accessible trip under 4000 with rest slots and fallbacks"
---

# multi-generational-trip-planner-with-accessibility-rest-and-contingency

A skill that generates balanced, low-physical-load itineraries for families spanning three generations (senior, child, adults), enforcing strict daily rest slots, minimized walking distance, verified accessibility, and explicit weather and transport delay contingencies for real-world reliability.

## Prompt

# Goal
Generate a single-page, checkpoint-complete 7-day family trip itinerary for 3–4 people including at least one senior (65+) and one child (5–12), with fully accessible logistics, zero overnight transfers, total cost under $4,000 USD (excluding airfare), and built-in weather fallbacks and transport delay contingencies. Output must be a concrete, executable plan — not advice or options — optimized for printing or mobile viewing with no external dependencies.

# Constraints & Style
- MUST limit cumulative daily walking to ≤ 2,000 steps per person (measured door-to-door; exclude steps inside venues unless core to activity); use flat, paved, bench-equipped routes only — no stairs, gravel, steep inclines, or uneven terrain; max 50 ft from vehicle drop-off to entrance
- MUST include a fixed, pre-booked/restored 90-minute midday rest slot daily (1:00–2:30 PM), explicitly labeled 'REST', offering climate control, quiet, seating support, and optional light refreshment; rest location and timing are invariant — never optional, negotiable, or relocatable
- MUST prioritize venues with verified accessibility: step-free entry, elevator/stroller/wheelchair access, on-site mobility support (e.g., scooters, reserved seating), indoor rest areas, and proximity to restrooms; NEVER invent unconfirmed features — omit or substitute with confirmed options; all venue names must be real, publicly verifiable, and confirmed wheelchair/stroller/senior-accessible via official website or ADA directory
- MUST exclude all attractions requiring >15 min continuous walking, timed entry without flexibility, standing queues, crowded festivals, or unconfirmed accessibility features
- MUST embed cost transparency: itemize accommodation, transport, food, activities, and incidentals — total must be ≤ $3,850 (to allow $150 buffer)
- MUST assume shoulder-season travel (April or October) for pricing and weather reliability
- MUST include, for each day: (a) a weather fallback plan (triggered by ≥70% rain, temp <45°F or >88°F, or wind >25 mph) using only pre-verified indoor, seated, low-sensory alternatives at the same or adjacent location (≤0.2 miles or ≤5-min drive), and (b) a transport delay contingency for each inter-venue leg — a same-day, same-location alternative reachable on foot in ≤5 minutes (or via pre-booked flat-rate accessible ride), preserving rest slot timing and adding ≤10 min total latency; include 'Pause & Pivot' rest hubs (AC, restrooms, Wi-Fi) and concierge-coordinated driver support via hotel front desk
- MUST omit airfare but clarify that arrival/departure must occur same-day (no overnight layovers or transfers)
- MUST avoid generic phrasing (e.g., 'consider', 'you might'); use imperative, actionable language (e.g., 'Book X', 'Walk Y', 'Rest from Z to A')
- MUST output in a flat, chronological list — one day per section — with bolded headers (**Day 1**, **AM**, **REST**, **PM**, **Weather Fallback**, **Delay Fix**) and no nested structure, tables, or grid syntax; use only line breaks, dashes, and bolded headers for scannability
- MUST use only mid-range, fully accessible accommodations with kitchenettes and free breakfast (e.g., Homewood Suites, Residence Inn)
- MUST use placeholder notation only where user-provided values are required: <SOURCE_CITY>, <TRAVEL_DATES>, <HOTEL_NAME>, <VEHICLE_TYPE>

## Triggers

- plan a multi-generational trip with rest and contingencies
- family trip with senior and child and weather backup
- low-walking accessible itinerary with transport delay plan
- three-generation travel plan with real-world reliability
- accessible trip under 4000 with rest slots and fallbacks
