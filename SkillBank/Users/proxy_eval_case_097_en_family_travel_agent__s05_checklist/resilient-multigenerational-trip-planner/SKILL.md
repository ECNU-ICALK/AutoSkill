---
id: "0366ae16-7b23-4f50-9363-b34e355093f5"
name: "resilient-multigenerational-trip-planner"
description: "Generates accessible, low-walk multigenerational family itineraries with guaranteed daily rest slots and built-in weather fallbacks and transport delay contingencies — optimized for seniors, children, and mixed mobility needs."
version: "0.1.3"
tags:
  - "accessibility"
  - "family-travel"
  - "senior-friendly"
  - "child-friendly"
  - "contingency-planning"
  - "budget-travel"
  - "resilience"
  - "itinerary"
  - "operational-checklist"
triggers:
  - "plan family trip with senior and child"
  - "limit walking for multigenerational travel"
  - "add daily rest slots to itinerary"
  - "make trip accessible without overnight transfers"
  - "include weather fallbacks in itinerary"
  - "plan for transport delays in accessible trip"
  - "provide detailed and compact itinerary versions"
  - "make multigenerational trip resilient to weather and delays"
  - "create day-by-day accessibility checklist"
  - "generate operational itinerary for mixed-mobility group"
  - "build fallback-ready travel plan"
  - "enforce rest slot integrity in itinerary"
  - "validate step count for primary and fallback activities"
---

# resilient-multigenerational-trip-planner

Generates accessible, low-walk multigenerational family itineraries with guaranteed daily rest slots and built-in weather fallbacks and transport delay contingencies — optimized for seniors, children, and mixed mobility needs.

## Prompt

# Goal
Generate a detailed, executable 5–7 day family trip itinerary for mixed-age travelers (including at least one senior with mild mobility considerations and one child aged 6–10), strictly adhering to: (1) walking load ≤1,500 steps/day on flat, paved, step-free routes; (2) one dedicated 90-minute rest slot per day (Days 1–6), scheduled within 11:30 AM–2:30 PM, in a climate-controlled or shaded, seated, low-stimulus location; and (3) explicit, actionable weather fallbacks and transport delay contingencies for every outdoor or transit-dependent activity.

# Constraints & Style
- Prioritize same-day arrival and departure — no overnight transfers; all travel occurs within Days 1–7.
- Total budget cap: $4,000 USD for 3 people (2 adults + 1 child); itemize cost categories with realistic mid-season estimates and maintain ≥$50 buffer.
- Accommodations must offer ground-floor/elevator access, in-room seating, and proximity to core activities (<10 min transit or walk).
- Transportation must avoid rental cars; rely on accessible public transit, pre-booked accessible rideshares, or private shuttles.
- Exclude strenuous, unshaded, stairs-dependent, gravel, or standing-only experiences — no hiking trails, narrow sidewalks, or inaccessible venues.
- For every outdoor or weather-exposed activity: specify (a) the triggering condition (e.g., >30% rain chance, temps <45°F or >88°F, wind >15 mph), and (b) an immediate, on-site or nearby indoor alternative requiring ≤200 additional steps and zero new transit — fully accessible and seated.
- For every activity dependent on shuttle, rideshare, or public transit: specify (a) the acceptable delay threshold (e.g., >15 min for booked ride, >10 min for bus arrival), and (b) a time-boxed (≤20 min), zero-transit backup (e.g., adjacent indoor venue, hotel-based activity, pre-downloaded audio experience) — with no added walking or access barriers.
- All fallbacks and contingencies must reuse existing bookings, budgeted incidentals ($200), or pre-authorized hotel services — no new costs or external dependencies.
- Enforce *exactly one* daily rest slot: 90 minutes, non-negotiable, pre-scheduled, and never encroached upon — even during weather or transport disruptions.
- Cap total walking at ≤1,500 steps/day; verify step count for *both* primary activity *and* each fallback option.
- All activities and fallbacks must require ≤200 steps *beyond drop-off point* — no stairs, no unpaved surfaces, no standing-only zones.
- Every outdoor activity must have a same-day, zero-cost, zero-step indoor/weather fallback — pre-identified, location-proximate (<0.3 mi), and accessible via same transport mode or shorter.
- Every scheduled transport leg must include three-tiered delay response: (1) wait-and-rebook protocol, (2) pre-coordinated backup provider (e.g., hotel shuttle), and (3) zero-effort guest option (e.g., staff-driven cart or in-room activation).
- All contingency triggers must be atomic and user-actionable: single SMS keyword (e.g., "RAIN"), voice phrase (e.g., "RIDESHARE CODE <CITY>-7"), or pre-loaded digital asset (e.g., iPad tour).
- Never assume real-time internet, app access, or guest-initiated rebooking — fallbacks must be pre-authorized, pre-briefed, and staff-executed on demand.
- Never conflate 'accessible' with 'low-effort' — explicitly exclude any step requiring guest navigation, wayfinding, or decision latency (e.g., 'choose from 3 options').
- Use placeholder destination (<DESTINATION>) — remain portable across cities with strong ADA infrastructure (e.g., Portland, Charleston, San Diego); do not assume Asheville unless specified.
- Output two parallel versions in one response:
  • **Detailed Execution Version**: Full table-based itinerary (Day 1–7) with time-blocked activities, verified step counts, rest slot timing, accessibility notes, and embedded fallback/contingency callouts per day.
  • **Compact Execution Version**: A single-column, scannable list (one line per day) using concise, standardized syntax: "[Day X] [AM] → [PM] | Rest: [time] | Fallback: [trigger] | Contingency: [tier-1 action]". Omit explanations, totals, or notes — only actionable, atomic facts.
- Use only de-identified, reusable logic: e.g., "text RAIN to concierge", "call CONCIERGE CODE <CITY>-7", "use pre-saved 'Accessible Vehicle' filter" — no personal names, dates, IDs, or origin cities.
- Output must include: daily schedule in table format (Morning / Rest Slot / Afternoon / Evening), step-load rationale and verified daily/total step count, transport mode per leg, accessibility notes per activity, rest justification (location, duration, modality), and a concise 'Contingency At-a-Glance' section.
- Never omit rest or contingency justification — explicitly state *where*, *how long*, *why*, and *how* each meets the need.
- 📄 Output format: plain-text, tabular, day-by-day, with columns: [Time Block | Action | Verification Required | Fallback Trigger | Step Count].
- 🧩 De-identify all location names, contact details, pricing, and proprietary service names — use generic placeholders (e.g., <MUSEUM>, <SHUTTLE_PROVIDER>, <HOTEL>).

## Triggers

- plan family trip with senior and child
- limit walking for multigenerational travel
- add daily rest slots to itinerary
- make trip accessible without overnight transfers
- include weather fallbacks in itinerary
- plan for transport delays in accessible trip
- provide detailed and compact itinerary versions
- make multigenerational trip resilient to weather and delays
- create day-by-day accessibility checklist
- generate operational itinerary for mixed-mobility group
