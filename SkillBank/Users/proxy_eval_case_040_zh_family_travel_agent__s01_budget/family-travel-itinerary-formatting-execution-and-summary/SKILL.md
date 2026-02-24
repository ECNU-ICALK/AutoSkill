---
id: "22576cc5-adf4-4f53-81a4-23bcc4d99208"
name: "family-travel-itinerary-formatting-execution-and-summary"
description: "Format travel itineraries for multi-generational families into two versions: detailed execution format for planning and simplified summary format for family group sharing, incorporating mobility constraints and weather contingencies."
version: "0.1.0"
tags:
  - "travel planning"
  - "family itinerary"
  - "multi-format output"
  - "mobility constraints"
  - "weather contingency"
triggers:
  - "format itinerary for families"
  - "create execution and summary versions"
  - "multi-generational travel planning formats"
  - "travel itinerary simplification for families"
---

# family-travel-itinerary-formatting-execution-and-summary

Format travel itineraries for multi-generational families into two versions: detailed execution format for planning and simplified summary format for family group sharing, incorporating mobility constraints and weather contingencies.

## Prompt

# Goal
Convert a comprehensive travel itinerary into two audience-specific formats: execution version (detailed operational plan) and family group version (concise summary).

# Constraints & Style
- Multi-generational family: elderly (knee issues, low walking intensity ≤3000 steps/day, afternoon rest), child-appropriate
- Transportation: High-speed rail preferred, minimal flights
- Weather contingency: Indoor alternatives, ticket change strategies
- Execution version: Daily detailed schedule, budgets, logistics, accessibility details
- Family group version: Daily highlights, key transport times, accommodation, weather tips
- Clear separation of the two versions
- Use family-friendly, non-technical language

# Workflow
1. Analyze input itinerary for activities, destinations, dates, constraints
2. Extract key elements: transportation, accommodation, activities, weather contingencies
3. Generate Execution Version:
   - Full daily itineraries with timestamps
   - Budget breakdown (transport, accommodation, meals, tickets)
   - Transportation details (rail schedules, transfer times, platform info)
   - Accessibility notes (wheelchair rentals, elevators, rest areas)
   - Weather contingency alternatives
4. Generate Family Group Version:
   - Simple daily summary in plain language
   - Key transportation times (departure/arrival)
   - Accommodation highlights
   - Weather considerations
   - Family tips (what to bring, rest breaks, etc.)
5. Format both versions clearly, labeled for their intended audience

## Triggers

- format itinerary for families
- create execution and summary versions
- multi-generational travel planning formats
- travel itinerary simplification for families
