---
id: "4539e665-d482-4738-b3ec-9c09942d83a0"
name: "handle-moving-company-cancellation-with-12h-alternative-plan"
description: "Executes a verified 12-hour contingency workflow when a booked moving company cancels last-minute, ensuring zero delay to the搬家 schedule by activating pre-vetted backup providers and triggering parallel fallback actions."
version: "0.1.0"
tags:
  - "contingency"
  - "moving"
  - "logistics"
  - "risk-mitigation"
  - "time-bound"
triggers:
  - "搬家公司临时取消"
  - "搬家当天供应商失联"
  - "预约搬家服务被取消"
  - "需要12小时替代方案"
  - "突发换搬家公司"
---

# handle-moving-company-cancellation-with-12h-alternative-plan

Executes a verified 12-hour contingency workflow when a booked moving company cancels last-minute, ensuring zero delay to the搬家 schedule by activating pre-vetted backup providers and triggering parallel fallback actions.

## Prompt

# Goal
Ensure continuity of a cross-city move when the primary moving company cancels with ≤24 hours’ notice, by executing a time-bound, pre-validated 12-hour alternative plan that secures replacement service, protects liability, and maintains scheduled move day.

# Constraints & Style
- Must activate *only* upon confirmed cancellation (e.g., official call/email from provider, not rumor or delay).
- All backup vendors must be pre-qualified: verified business license, in-house fleet, ≥3-star average rating (last 6 months), and documented capacity for user’s move scope (e.g., 2-bedroom, 6th-floor no elevator).
- No cost negotiation during activation — fallback vendors operate at pre-agreed fixed rate (≤110% of original quote); budget cap remains binding (e.g., ≤¥10,000 under 50k total).
- Output must include: (1) name/contact of activated backup vendor, (2) signed electronic confirmation timestamp, (3) updated pickup/drop-off windows, (4) revised handover checklist (e.g., 're-verify insurance coverage before loading').
- Never advise DIY alternatives (e.g., rental trucks) unless explicitly permitted by user; assume user requires full-service, insured, staffed relocation.

# Workflow
1. Within 30 minutes of cancellation confirmation: retrieve and contact top-2 pre-vetted backup vendors (from user’s saved list) using scripted verification: “Hi, this is <USER_NAME> — I have an urgent same-week move on <MOVE_DATE> from <OLD_ADDRESS> to <NEW_ADDRESS>, ~<ESTIMATED_BOXES> boxes, <FLOORS> floors, no elevator. Can you confirm availability, fixed quote, and insurance coverage by <CURRENT_TIME + 90 MIN>?”
2. Select first vendor who replies with written confirmation (email/SMS/app message) meeting all criteria; decline others politely but immediately.
3. Within 2 hours: secure e-signature on simplified contract (using pre-filled template: scripts/moving-fallback-contract.md) and pay non-refundable 30% deposit via traceable method.
4. Within 4 hours: notify user’s key stakeholders — landlord (for access), building management (for freight elevator booking), and family (for coordination); provide updated timeline.
5. Within 12 hours: deliver full execution package: (a) vendor’s driver name/license plate, (b) live tracking link (if available), (c) revised packing-labeling instructions (e.g., ‘add “BACKUP-V2” to all box labels’), and (d) emergency escalation path (vendor supervisor direct line).

## Triggers

- 搬家公司临时取消
- 搬家当天供应商失联
- 预约搬家服务被取消
- 需要12小时替代方案
- 突发换搬家公司
