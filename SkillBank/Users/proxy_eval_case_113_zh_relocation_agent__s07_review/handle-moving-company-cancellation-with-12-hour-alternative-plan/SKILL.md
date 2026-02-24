---
id: "b6349e71-44a9-4ac2-8556-4e64c4e78a02"
name: "handle-moving-company-cancellation-with-12-hour-alternative-plan"
description: "A reusable protocol for responding to last-minute moving company cancellation, guaranteeing a verified backup solution within 12 hours — triggered automatically during weekly cross-city move reviews when vendor cancellation or material term changes are confirmed."
version: "0.1.1"
tags:
  - "contingency"
  - "logistics"
  - "reliability"
  - "time-bound"
  - "review-triggered"
triggers:
  - "搬家公司临时取消"
  - "搬家服务突然取消"
  - "供应商违约应急"
  - "12小时替代方案"
  - "备用搬家公司流程"
  - "vendor cancellation confirmed"
  - "moving vendor terms changed"
---

# handle-moving-company-cancellation-with-12-hour-alternative-plan

A reusable protocol for responding to last-minute moving company cancellation, guaranteeing a verified backup solution within 12 hours — triggered automatically during weekly cross-city move reviews when vendor cancellation or material term changes are confirmed.

## Prompt

# Goal
Generate a time-bound, executable 12-hour alternative plan when a booked moving company cancels unexpectedly — including immediate verification steps, pre-vetted fallback options, and clear handoff instructions. Output only the plan; no explanations or disclaimers.

# Constraints & Style
- Must be triggered *only* upon confirmed cancellation (e.g., official call/email with no reschedule offer) — or during a weekly review when vendor cancellation or material term change (e.g., price hike, coverage gap) is confirmed.
- All fallback providers must be pre-qualified: hold valid road transport license, offer real-time GPS tracking, and provide on-the-record damage liability terms.
- Exclude generic advice (e.g., "search online") or unverified leads (e.g., "contact local Facebook groups").
- Budget adherence: fallback cost must stay within original approved range (no premium surcharges without explicit user override).
- Output format: strict markdown table with columns: Time Window | Action | Owner | Verification Required.
- No names, phone numbers, URLs, or city-specific vendor IDs — use placeholders like <LICENSED_FALLBACK_PROVIDER>.
- Do not include emotional language, reassurance, or motivational statements.

# Workflow
1. Within 0–30 minutes of cancellation confirmation: freeze all packing activity; retrieve original booking ID and service scope.
2. Within 1–3 hours: activate pre-loaded fallback list — contact exactly two providers meeting all licensing and liability criteria; obtain written quote + ETA + vehicle details.
3. Within 4–8 hours: select and confirm one provider; share updated schedule with all stakeholders (landlord, new property manager, family).
4. Within 9–12 hours: verify driver assignment, vehicle plate, and insurance coverage via official platform dashboard or direct call to provider’s compliance desk.

## Triggers

- 搬家公司临时取消
- 搬家服务突然取消
- 供应商违约应急
- 12小时替代方案
- 备用搬家公司流程
- vendor cancellation confirmed
- moving vendor terms changed
