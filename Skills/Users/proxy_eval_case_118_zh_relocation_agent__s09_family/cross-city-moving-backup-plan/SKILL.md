---
id: "5353eaa5-085e-4a19-916d-b408c5bd7283"
name: "cross-city-moving-backup-plan"
description: "A standardized 12-hour contingency workflow triggered when a contracted moving company cancels last-minute, ensuring continuity of relocation without budget or timeline breach."
version: "0.1.0"
tags:
  - "contingency"
  - "moving"
  - "logistics"
  - "risk-mitigation"
  - "contract-compliance"
triggers:
  - "搬家公司临时取消"
  - "搬家当天供应商失联"
  - "合同方突然退出"
  - "需要12小时内备用搬家方案"
---

# cross-city-moving-backup-plan

A standardized 12-hour contingency workflow triggered when a contracted moving company cancels last-minute, ensuring continuity of relocation without budget or timeline breach.

## Prompt

# Goal
Execute a verified, time-bound fallback protocol within 12 hours of confirmed cancellation by the primary moving company — securing an equally stable, contract-compliant replacement service while preserving all pre-negotiated terms (insurance, vehicle type, labor, and liability coverage).

# Constraints & Style
- Must use only pre-vetted, A-level logistics providers (verified via China Federation of Logistics & Purchasing certification, ≥5 years operation, zero major complaints on 12315 platform).
- All replacement quotes must include: written itemized pricing, explicit insurance coverage (min. ¥100,000 declared value), GPS-tracked vehicle, and licensed driver ID.
- No verbal agreements: contract must be signed digitally *before* any deposit is paid; payment only after full contract upload to shared document folder.
- Prohibited: brokers, unregistered drivers, platforms without enterprise verification tags (e.g., non-‘Enterprise’ labeled listings on Huolala), or services requiring cash-on-delivery.
- Output format: plain-text checklist with timestamps (HH:MM), action owner (you/assistant), and verification step (e.g., '✅ Screenshot of A-level certificate in企查查').

# Workflow
1. Within 0–2 hours of cancellation: retrieve and re-verify top 3 pre-screened backup vendors from your ‘Stable Provider Whitelist’ (e.g., ‘Blue Rhinoceros’, ‘Dazhong Moving’, ‘Wanlong Moving’) using企查查 + 12315 + transport license lookup.
2. Within 2–5 hours: contact all 3 vendors simultaneously via official channels (not WeChat); request same-day written quote matching original scope (distance, volume, floors, disassembly, insurance) — require PDF contract draft.
3. Within 5–8 hours: compare quotes *only* on compliance (not price); select vendor whose contract mirrors original terms *exactly* — especially liability clause, payout timeline for damage, and cancellation policy.
4. Within 8–10 hours: e-sign contract; pay deposit (≤30%) via traceable method (bank transfer with purpose note); save all comms + contract + payment receipt.
5. Within 10–12 hours: confirm driver name, plate number, and real-time tracking link; share updated schedule with all stakeholders (landlord, new property manager, family).

## Triggers

- 搬家公司临时取消
- 搬家当天供应商失联
- 合同方突然退出
- 需要12小时内备用搬家方案
