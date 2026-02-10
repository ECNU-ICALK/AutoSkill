---
id: "44987e7a-4eba-43d0-9aed-0d8c7ad05d9c"
name: "wedding-contingency-planning"
description: "A reusable skill for generating actionable, pre-emptive contingency plans for high-stakes wedding execution risks—specifically rain (for outdoor/semi-outdoor venues), supplier no-shows, and guest-related disruptions—aligned to a fixed timeline, budget, and pre-validated contractual or logistical commitments."
version: "0.1.1"
tags:
  - "contingency"
  - "risk-mitigation"
  - "wedding-planning"
  - "contract-enforcement"
  - "budget-bound"
  - "pre-validated-response"
triggers:
  - "下雨应急预案"
  - "供应商爽约怎么办"
  - "婚礼当天供应商没来"
  - "户外婚礼下雨了"
  - "宾客突发状况应对"
  - "婚礼前三大风险预案"
---

# wedding-contingency-planning

A reusable skill for generating actionable, pre-emptive contingency plans for high-stakes wedding execution risks—specifically rain (for outdoor/semi-outdoor venues), supplier no-shows, and guest-related disruptions—aligned to a fixed timeline, budget, and pre-validated contractual or logistical commitments.

## Prompt

# Goal
Generate a concise, executable contingency plan for *one* specified wedding risk (e.g., rain, supplier no-show, guest disruption), scoped to the user’s confirmed wedding scale (e.g., 120 people), venue type, timeline (e.g., D-30), and budget ceiling (e.g., ¥300,000). Output must be immediately usable by non-professionals: concrete actions, clear ownership, time-bound triggers, cost-aware fallbacks, and grounded exclusively in pre-negotiated, contract-backed, or physically prepared responses.

# Constraints & Style
- ✅ MUST include for each risk: (1) A single, unambiguous, externally verifiable trigger condition (e.g., "Central Meteorological Observatory issues Red Rain Warning ≥72h before <D_DAY>"); (2) A pre-validated fallback action (e.g., "Venue activates indoor backup space per Clause 4.2, zero surcharge" or "Pre-recorded AI voice U盘 deployed"); (3) Explicit owner assignment with contact method (e.g., "Total Coordinator via WeChat <CONTACT_ID>"); (4) Hard activation deadline (e.g., "Execute within 2h of trigger" or "Activate by D-1"); (5) Exact cost impact drawn only from pre-allocated emergency fund (e.g., ≤¥15,000) or embedded line-item budgets; (6) Contract or prep anchor (e.g., "Substitute Commitment Letter signed on <DATE>", "B-team photography included in 'Four Pillars' budget").
- ❌ MUST NOT include: generic advice (e.g., "communicate early", "have a backup"), unactionable warnings, vendor recommendations, real-time data access, invented vendors/tools/processes, or explanations/disclaimers.
- Language: Match user’s language (e.g., Chinese); tone: calm, authoritative, procedural—not reassuring or emotional.
- Output format: Strict Markdown table with columns: Trigger | Pre-Validated Response | Owner | Activation Deadline | Cost Impact | Contract Anchor.
- De-identify all specifics: replace venue names, vendor names, exact dates, bank details, city names, and contact IDs with placeholders (e.g., <VENUE_NAME>, <D_DAY>, <BACKUP_VENUE>, <CONTACT_ID>); retain only structural logic and reusable constraints.

# Workflow
None — this is a single-step, constraint-driven generation. No multi-stage AI operations are defined or required.

## Triggers

- 下雨应急预案
- 供应商爽约怎么办
- 婚礼当天供应商没来
- 户外婚礼下雨了
- 宾客突发状况应对
- 婚礼前三大风险预案
