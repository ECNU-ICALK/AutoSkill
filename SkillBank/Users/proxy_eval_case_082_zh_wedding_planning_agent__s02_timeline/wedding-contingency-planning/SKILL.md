---
id: "05521f1e-6ad9-4fd2-9ce6-9337a414be20"
name: "wedding-contingency-planning"
description: "A reusable skill for generating actionable, vendor-specific contingency plans for high-impact wedding risks — specifically rain and supplier no-shows — with pre-defined triggers, role-assigned actions, time-bound responses, fallback resource activation, and explicit identification of non-removable timeline dependencies."
version: "0.1.1"
tags:
  - "contingency"
  - "risk-mitigation"
  - "wedding-planning"
  - "vendor-management"
  - "timeline"
  - "vendor-dependency"
  - "execution-plan"
triggers:
  - "rain backup plan"
  - "supplier no-show预案"
  - "wedding contingency"
  - "weather fallback"
  - "vendor cancellation plan"
  - "compress wedding timeline"
  - "remove one week from plan"
  - "what can't be cut"
  - "non-removable wedding steps"
  - "timeline compression guardrails"
---

# wedding-contingency-planning

A reusable skill for generating actionable, vendor-specific contingency plans for high-impact wedding risks — specifically rain and supplier no-shows — with pre-defined triggers, role-assigned actions, time-bound responses, fallback resource activation, and explicit identification of non-removable timeline dependencies.

## Prompt

# Goal
Generate a concise, executable contingency plan for two critical wedding risks: (1) rain (or other venue-disrupting weather), and (2) key supplier no-show (e.g., photographer, caterer, officiant). The plan must be tied to concrete vendor contracts and timeline milestones — not generic advice. Additionally, identify which steps in the associated execution plan are non-removable due to hard dependencies on external vendors, contractual obligations, physical logistics, or dual-risk contingency activation.

# Constraints & Style
- Output only three clearly labeled sections: '🌧️ Rain Contingency', '🚫 Supplier No-Show Contingency', and '✅ Non-removable Timeline Dependencies'.
- Each contingency section must include: (a) Trigger condition (e.g., 'Weather forecast ≥80% chance of >5mm rain at ceremony time, issued by official source ≤24h pre-event'), (b) Immediate action (≤30 min), (c) Owner (who executes it), (d) Fallback option (pre-vetted, contract-ready alternative), and (e) Required proof/confirmation (e.g., 'signed addendum', 'screenshot of backup vendor’s availability confirmation').
- All fallbacks must be *pre-identified during vendor selection* — no 'search online now' instructions.
- The '✅ Non-removable Timeline Dependencies' section must list bulleted, role-agnostic actions that cannot be removed or delayed because they anchor to at least one of: (1) contractually fixed payment/confirmation deadline, (2) minimum lead time for physical delivery/setup, (3) required pre-activation of fallback resources (e.g., rain venue access, signed备选 contracts), or (4) mandatory verification before D-3 (e.g., final headcount lock, service验收).
- Never mention budget unless directly relevant to fallback activation or contractual obligation (e.g., 'rain tent deposit already paid').
- Use plain, imperative language. No motivational phrasing or reassurance.
- De-identify all specifics: replace names, brands, locations, dates, monetary values, and vendor types with placeholders (e.g., <VENUE_NAME>, <PHOTOGRAPHER_NAME>, <RAIN_TENT_VENDOR>, <D-X>, <vendor-type>, <critical-deliverable>).
- Do NOT invent new steps, timelines, resources, or rationales beyond what is explicitly required for risk mitigation or dependency validation.

## Triggers

- rain backup plan
- supplier no-show预案
- wedding contingency
- weather fallback
- vendor cancellation plan
- compress wedding timeline
- remove one week from plan
- what can't be cut
- non-removable wedding steps
- timeline compression guardrails
