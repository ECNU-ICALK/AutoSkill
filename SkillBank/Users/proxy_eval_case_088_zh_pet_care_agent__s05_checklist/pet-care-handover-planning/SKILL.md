---
id: "060d2181-a713-4ce9-955c-2f4ded519d34"
name: "pet-care-handover-planning"
description: "Generates a structured, actionable pet care handover plan for temporary owner absence, covering caregiver briefing, daily routine alignment, emergency protocols, and交接 documentation."
version: "0.1.0"
tags:
  - "pet-care"
  - "handover"
  - "routine-alignment"
  - "contingency-planning"
triggers:
  - "hand over pet care during travel"
  - "prepare pet sitter instructions"
  - "dog care while away"
  - "temporary pet caregiver briefing"
  - "pet care交接 checklist"
---

# pet-care-handover-planning

Generates a structured, actionable pet care handover plan for temporary owner absence, covering caregiver briefing, daily routine alignment, emergency protocols, and交接 documentation.

## Prompt

# Goal
Generate a clear, executable pet care handover plan for a temporary absence (e.g., travel), specifying what to communicate to the caregiver, how to align routines, what to document, and how to prepare for contingencies — all scoped to the pet’s established weekly care schedule.

# Constraints & Style
• Must be grounded exclusively in the pet’s *existing* weekly care plan (e.g., feeding times, walk duration, medication, grooming cadence, weight tracking rhythm); do not invent new care items.
• Include only four mandatory sections: (1) Caregiver Briefing Checklist, (2) Routine Handover Table (mapping each daily care item to caregiver responsibility + notes), (3) Emergency & Contingency Protocol (with clear thresholds for vet contact), (4) Pre-Departure Documentation Requirements.
• Use plain, imperative language — no explanations, no disclaimers, no marketing tone. Avoid phrases like 'we recommend' or 'it’s ideal'.
• Never assume caregiver expertise: specify exact product names (e.g., 'PetSafe automatic feeder model X', 'Frontline Plus vial #A7B2'), dosing (e.g., '½ tablet of Trifexis every Monday AM'), or tool access (e.g., 'Google Sheet link: [redacted]') if provided by user; otherwise use placeholders like <FEEDER_MODEL>, <MEDICATION_NAME>, <TRACKING_SHEET_LINK>.
• Exclude general advice (e.g., 'choose a trustworthy person'), emotional framing, or seasonal/variable tips unless explicitly requested by user.
• Output as a single Markdown table + bullet list structure — no intro, no outro, no emojis.

# Workflow
1. Extract the pet’s current weekly care cadence from the most recent user-provided schedule (e.g., feeding at 7:00/18:30, walks at 30min ×2, ear cleaning on Monday, weight checks Wed/Sun).
2. Map each recurring care item to a handover row: who does it, when, with what tools/supplies, and any non-negotiable notes (e.g., 'must use slow-feeder bowl', 'no off-leash in backyard').
3. Define objective escalation triggers (e.g., 'if >2 episodes of vomiting in 24h → call vet', 'if weight drops >2% in 5 days → pause treat allowance and consult').
4. List required pre-departure artifacts: printed feeding/walk log, labeled medication box, access credentials, vet contact card.

## Triggers

- hand over pet care during travel
- prepare pet sitter instructions
- dog care while away
- temporary pet caregiver briefing
- pet care交接 checklist
