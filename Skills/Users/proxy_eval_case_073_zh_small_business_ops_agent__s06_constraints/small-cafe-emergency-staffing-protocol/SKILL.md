---
id: "b82cfb46-a15e-49f9-81c3-a6ca268d8177"
name: "small-coffee-shop-emergency-staffing-protocol"
description: "A reusable, role-agnostic, tiered emergency staffing protocol for small independent coffee shops (2–3 staff) that activates automatically upon any last-minute staff absence, ensuring operational continuity, food safety, drink quality, and core service promises without real-time decision-making or external tools."
version: "0.1.2"
tags:
  - "emergency-response"
  - "staffing"
  - "coffee-shop"
  - "SOP"
  - "small-business"
  - "operations"
triggers:
  - "突发缺人"
  - "员工临时请假"
  - "应急排班"
  - "staff shortage"
  - "last-minute absence"
---

# small-coffee-shop-emergency-staffing-protocol

A reusable, role-agnostic, tiered emergency staffing protocol for small independent coffee shops (2–3 staff) that activates automatically upon any last-minute staff absence, ensuring operational continuity, food safety, drink quality, and core service promises without real-time decision-making or external tools.

## Prompt

# Goal
Generate a ready-to-deploy, three-tier emergency staffing response plan for a small coffee shop (2–3 staff, no dedicated manager on-site) upon confirmed unexpected staff absence — preserving food safety, drink quality, customer flow, and non-negotiable hygiene/brand standards.

# Constraints & Style
- Must be triggered by *any* unplanned absence (sick call, transport failure, family emergency) — no justification required.
- Must be role-agnostic: actions must work whether one, two, or any subset of the usual 2–3 staff are present; no assumptions about identity, seniority, or role labels.
- Must require zero external tools: use only existing in-store assets — printed materials (e.g., '15-Minute Emergency SOP Card', 'Pre-Printed Menu Abridgement', 'Cup-Timing Cheat Sheet'), magnetic whiteboards, smart lock, handheld thermometer, and pre-loaded digital assets (PDFs/videos in team chat).
- Must preserve three 'non-negotiables': (1) first cup self-tasted & approved by lead barista, (2) all surfaces cleared within 3 minutes of customer departure, (3) no untrained person handles espresso machine calibration or milk steaming above 65°C.
- Must preserve food safety: refrigeration held ≥0°C; temperature checks every 2 hours; limited-edition batches labeled with prep time and discard deadline.
- Must preserve core product integrity: standard drink specs never compromised; complex/custom drinks paused (not downgraded); only serve <STANDARD_DRINK_1>, <STANDARD_DRINK_2>, <STANDARD_DRINK_3>, <STANDARD_DRINK_4> in 'Core 4-Hour Mode' if >1 person absent.
- Must not extend any shift beyond 9 hours or schedule consecutive early+late shifts.
- Language must be directive, imperative, and concrete — no explanations or theory. Use checkmarks (✓), bold verbs, and time-bound triggers (e.g., 'within 5 min', 'by T+15 min').
- Output format: strict Markdown with exactly four sections — ### 🚨 Tiered Response, ### 🛡️ Embedded Safeguards, ### 📋 Physical & Digital Readiness, ### 💬 Pre-Memorized Customer Lines — no extra headings or commentary.
- Exclude all venue-specific details (location, name, dates, staff names, supplier names, exact product SKUs, prices, internal codes); use only portable placeholders like <STANDARD_DRINK_1>, <LIMITED_EDITION>, <PRE-PRINTED_SIGN>, <ITEM>, <TIME>, <AMOUNT>, <ROLE>.
- Explicitly name the physical location of the emergency kit (e.g., 'blue canvas bag with ⚡ icon on leftmost hook under counter').
- Embed the three universal response phrases as verbatim quoted strings — no paraphrasing.
- Never invent thresholds, regulations, or technical specs not grounded in user evidence.

# Workflow
1. T+0–5 min: [Lead Barista] confirms absence → immediately retrieves & distributes '15-Minute Emergency SOP Card' to all present staff.
2. T+5–10 min: [Lead Barista] and [Support Staff] jointly complete verbal 3-item handover (e.g., 'Lactose-free oat milk is in blue jug', 'Today's limited batch is in fridge drawer 2', 'Refund authority cap is <REFUND_CAP>') — verified by brief repeat-back.
3. T+10–15 min: [Any Available Person] sets up 'Pre-Printed Menu Abridgement' at order point and places 'Cup-Timing Cheat Sheet' beside brew station.
4. T+15 min onward: All staff follow card instructions — no ad-hoc decisions. If >1 person absent, default to 'Core 4-Hour Mode'.

## Triggers

- 突发缺人
- 员工临时请假
- 应急排班
- staff shortage
- last-minute absence
