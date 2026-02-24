---
id: "dc9693e4-ec38-4e38-b887-d0acedebdc9e"
name: "canine-appetite-escalation-protocol"
description: "A time-bound, observation-driven veterinary escalation protocol for canine appetite decline, defining objective thresholds and mandatory actions for both owners and non-professional caregivers — designed to prevent delayed intervention in early illness."
version: "0.1.1"
tags:
  - "pet-care"
  - "veterinary-escalation"
  - "family-instruction"
  - "caregiver-protocol"
  - "early-intervention"
triggers:
  - "appetite drop response"
  - "dog not eating protocol"
  - "when to call vet for loss of appetite"
  - "canine anorexia escalation"
  - "dog refuses food action plan"
---

# canine-appetite-escalation-protocol

A time-bound, observation-driven veterinary escalation protocol for canine appetite decline, defining objective thresholds and mandatory actions for both owners and non-professional caregivers — designed to prevent delayed intervention in early illness.

## Prompt

# Goal
Generate a two-part canine appetite decline response protocol: (1) a simplified version for family members (non-expert, minimal jargon, visual cues, zero interpretation), and (2) an execution version for direct caregivers (step-by-step, verb-led, time-bound, binary decision logic).

# Constraints & Style
- Must strictly separate the two versions — no blended language or shared sections.
- Simplified version for family: use only plain language; replace medical terms (e.g., 'vomiting' → 'throwing up', 'abdominal pain' → 'tummy hurts when touched'); include emoji-anchored visual signals (e.g., 🐶→✅/❌); omit all thresholds requiring calculation or measurement beyond counting days or observing behavior.
- Execution version: every instruction must begin with an action verb; specify exact timing (e.g., 'within 5 minutes', 'on Day 5 morning'); define only binary outcomes ('eats' / 'refuses', 'normal' / 'abnormal') — no 'mild/moderate/severe'.
- Both versions must embed the same three-tier escalation logic (yellow/orange/red), but map triggers to role-appropriate observables: family sees *what’s obvious* (e.g., 'won’t eat for 2 whole days', 'throwing up green stuff'), while execution version uses *defined metrics* (e.g., 'intake <50% baseline for 48h', 'vomitus contains bile').
- Red-flag signs are strictly limited to: vomiting, diarrhea, lethargy, fever (>39.2°C), pale gums, or abdominal pain on palpation — no additions.
- Never mention clinical guidelines (AAHA/WSAVA), drug names, lab tests, or pathophysiology. Only observable behaviors, time windows, and required next actions.
- All weight, temperature, or intake thresholds must be expressed as placeholders: <WEIGHT_CHANGE_THRESHOLD>%, <TEMPERATURE_UPPER_LIMIT>°C, <INTAKE_PERCENTAGE>%. Do not instantiate values.
- Prohibit vague terms: no 'monitor closely', 'try tempting foods', or 'if worsening'. Replace with concrete, observable, time-bound directives.
- De-identify: remove all breed/age/health history references; do not assume prior knowledge of Bristol scale, capillary refill, or ear thermometry.

# Workflow
1. First, output the Simplified Version (for family): structured as 3 clearly labeled tiers (🟢 Yellow / 🟠 Orange / 🔴 Red), each containing: (a) plain-language trigger, (b) immediate 'what to do' in ≤10 words, (c) one unambiguous go/no-go signal (e.g., 'If [X] happens → call now').
2. Then, output the Execution Version: structured as a time-ordered table with columns: [Timeframe], [Action], [Observation], [Response]. Each row must be self-contained and executable without cross-reference.
3. End with a single-line note: 'All thresholds (<WEIGHT_CHANGE_THRESHOLD>%, <TEMPERATURE_UPPER_LIMIT>°C, etc.) are configured per individual dog and provided separately.'

## Triggers

- appetite drop response
- dog not eating protocol
- when to call vet for loss of appetite
- canine anorexia escalation
- dog refuses food action plan
