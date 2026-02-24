---
id: "6b910af1-7d77-43a3-9721-c5f0c578368b"
name: "reliable-moving-provider-fallback-protocol"
description: "A standardized 12-hour contingency workflow triggered when a contracted moving provider cancels last-minute, ensuring zero搬家-day disruption for budget-constrained, reliability-focused users."
version: "0.1.0"
tags:
  - "contingency"
  - "moving"
  - "reliability"
  - "budget-control"
  - "contract-enforcement"
triggers:
  - "搬家公司临时取消"
  - "供应商突发退出"
  - "搬家日程中断"
  - "紧急替代方案"
  - "12小时备用流程"
---

# reliable-moving-provider-fallback-protocol

A standardized 12-hour contingency workflow triggered when a contracted moving provider cancels last-minute, ensuring zero搬家-day disruption for budget-constrained, reliability-focused users.

## Prompt

# Goal
Execute a verified 12-hour fallback protocol to secure an equally stable and insured moving service after the primary provider cancels, without exceeding the total budget cap (e.g., ¥50,000) and preserving all contractual safeguards (price lock, itemized insurance, direct accountability).

# Constraints & Style
- Must activate only upon confirmed cancellation (e.g., official SMS/email from provider or >2h no-show with documented contact attempts).
- Replacement must meet the same stability criteria: national licensed carrier (not gig-platform aggregator), ≥98% on-time delivery rate, in-house staff (no subcontracting), minimum 200,000 RMB cargo insurance, and dedicated point-of-contact.
- Zero tolerance for price creep: replacement quote must be ≤ original contracted amount; if higher, apply emergency budget reallocation *only* from pre-approved contingency line (e.g., ¥2,000 buffer), never from core items (housing, utilities, legal admin).
- All documentation (cancellation proof, new contract, insurance addendum) must be timestamped, signed, and stored in a single shared folder within 30 minutes of resolution.
- Never recommend unvetted local movers or app-based spot bookings — only pre-qualified backup partners (e.g., SF Express Logistics, China Post Express Moving, or regional top-3 licensed carriers verified via Transport Ministry database).
- Output must be executable: provide exact steps, contact channels, script for verification calls, and time-bound checkpoints.

# Workflow
1. **T+0 min (Cancellation Confirmed)**: Save cancellation evidence → notify user immediately → open contingency folder.
2. **T+15 min**: Activate pre-vetted backup list (max 3 providers); call first option using script: *“We’re under a 12-hour activation clause per our original booking reference [REF]. Confirm: (a) same vehicle/capacity, (b) full insurance coverage, (c) dedicated manager, (d) written price lock — can you issue contract by T+90 min?”*
3. **T+90 min**: If confirmed, e-sign contract; if declined, escalate to next provider (repeat script).
4. **T+120 min**: Upload signed contract + insurance certificate + manager contact to contingency folder.
5. **T+300 min (5h)**: Verify pickup window alignment with original plan; adjust user’s day-of timeline if needed.
6. **T+720 min (12h)**: Deliver full handover package: updated schedule, labeled contact cards, checklist for user to validate crew ID/vehicle license on-site.

## Triggers

- 搬家公司临时取消
- 供应商突发退出
- 搬家日程中断
- 紧急替代方案
- 12小时备用流程
