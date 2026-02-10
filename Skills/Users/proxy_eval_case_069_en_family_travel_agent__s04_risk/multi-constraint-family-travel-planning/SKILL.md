---
id: "d8260036-13fe-4dcd-9723-cbe25983573e"
name: "multi-constraint-family-travel-planning"
description: "Plans multi-day family trips for multi-generational groups with strict budget limits, accessibility requirements (limited walking distances, daily rest slots), weather and transport contingencies, and activities that engage both seniors and children."
version: "0.1.3"
tags:
  - "travel planning"
  - "budgeting"
  - "accessibility"
  - "multi-generational"
  - "contingency planning"
triggers:
  - "plan family trip with budget limit and accessibility"
  - "travel planning with senior and child mobility needs"
  - "multi-generational trip with rest periods and contingencies"
  - "budget travel with detailed and compact itineraries"
  - "family vacation planning with weather fallbacks"
---

# multi-constraint-family-travel-planning

Plans multi-day family trips for multi-generational groups with strict budget limits, accessibility requirements (limited walking distances, daily rest slots), weather and transport contingencies, and activities that engage both seniors and children.

## Prompt

# Goal
Generate multi-day family trip plans for multi-generational groups that meet strict budget limits and include accessibility features for seniors and children.

# Constraints & Style
- Budget: Must specify strict budget limit and stay within it; provide detailed category breakdowns (accommodation, transportation, food, attractions)
- No overnight transfers: Stay in one hotel for entire trip duration
- Accessibility: Limit walking to under 0.5 miles per activity; include daily rest slots of 1-2 hours (extend to 2 hours on high-activity days); prioritize seated activities with elevator/tram access and flat terrain
- Contingencies: Include weather fallback options (indoor alternatives with heat/fog/rain adjustments) and transport delay contingencies (car rental, ferry cancellations, traffic jams, attraction closures) for each day
- Multi-generational focus: Activities that engage both seniors and children simultaneously
- Output: Provide both detailed and compact execution versions when requested
- Format: Clearly separated daily itineraries with budget breakdowns, rest slots, and contingency plans

# Workflow
1. Parse trip parameters (duration, budget, participant profiles)
2. Select activities matching accessibility and budget constraints
3. Schedule daily itineraries with rest slots
4. Generate weather/transport contingency options
5. Produce detailed version with full descriptions
6. Produce compact version with essential information only

## Triggers

- plan family trip with budget limit and accessibility
- travel planning with senior and child mobility needs
- multi-generational trip with rest periods and contingencies
- budget travel with detailed and compact itineraries
- family vacation planning with weather fallbacks
