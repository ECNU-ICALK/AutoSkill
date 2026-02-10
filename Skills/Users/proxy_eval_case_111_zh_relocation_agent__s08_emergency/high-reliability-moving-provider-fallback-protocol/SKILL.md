---
id: "71f18635-fafb-4ff3-97a1-bbb7e7b327d8"
name: "high-reliability-moving-provider-fallback-protocol"
description: "A standardized 12-hour contingency workflow triggered when a contracted moving provider cancels, delays by >2 hours, or exceeds budget by >5% within 72 hours of the move date, ensuring zero schedule slippage, no unplanned cost leakage, and maintained reliability through pre-vetted backup providers and parallel, time-boxed task execution across self, immediate family, and parents."
version: "0.1.2"
tags:
  - "contingency"
  - "moving"
  - "reliability"
  - "fallback"
  - "role-allocation"
  - "time-boxed"
  - "risk-mitigation"
  - "family-coordination"
triggers:
  - "搬家公司临时取消"
  - "搬家前72小时内供应商失联或违约"
  - "搬家服务延迟超两小时"
  - "搬家预算超支超过5%"
  - "需要紧急备用搬家公司"
  - "给我、家人、父母三套分工清单"
  - "跨城搬家应急任务分派"
  - "家庭协同应对搬家供应商违约"
---

# high-reliability-moving-provider-fallback-protocol

A standardized 12-hour contingency workflow triggered when a contracted moving provider cancels, delays by >2 hours, or exceeds budget by >5% within 72 hours of the move date, ensuring zero schedule slippage, no unplanned cost leakage, and maintained reliability through pre-vetted backup providers and parallel, time-boxed task execution across self, immediate family, and parents.

## Prompt

# Goal
Ensure zero-schedule-slippage, no unplanned cost leakage, and maintained reliability for a cross-city move when the primary moving provider fails (cancellation, delay >2h, or budget overrun >5%) with ≤72 hours notice — delivering a fully executable fallback plan within 12 hours. This includes confirmed backup vendor, signed contract, assigned driver/vehicle, updated logistics, and role-distributed execution across self, immediate family, and parents — without requiring user re-negotiation, re-estimation, or out-of-pocket spending beyond the pre-allocated ¥3,000 risk reserve.

# Constraints & Style
- MUST activate only upon verified failure: official written/captured notice (screenshot, recording, or timestamped message) from vendor confirming cancellation, delay beyond agreed window, or confirmed budget breach.
- MUST use only pre-approved, contract-ready backup vendors (from user’s vetted shortlist) — no new vendor search, unvetted local drivers, cash-only deals, or verbal agreements.
- MUST auto-generate and send: (1) revised electronic contract with same scope/insurance terms and auto-loaded penalty clauses, (2) driver ID + license plate + contact + real-time tracking link, (3) updated loading sequence and ETA.
- MUST preserve all original commitments: same insurance coverage, packaging materials, floor-level service, and damage liability terms.
- MUST NOT require user to re-submit inventory, measurements, or address details — pull from prior session context.
- MUST confirm completion via timestamped verifiable artifacts: screenshots, signed PDFs, photos, or timestamped messages — including final joint confirmation via voice note or emoji reaction in family chat.
- MUST assign non-overlapping, verb-first, present-tense tasks to three roles: ✅ Self, 👥 Immediate Family, 👵 Parents — each task time-anchored to one of four phases: 0–1h (Trigger & Triage), 1–3h (Assessment & Lock-in), 3–6h (Handover Prep), 6–12h (Execution & Close).
- Parents’ tasks must require zero digital interaction, zero physical lifting >5kg, zero decision-making under ambiguity — only recognition, labeling, handing over, waiting in designated safe zones, or affixing notes.
- Every task must be time-boxed to ≤2-hour windows; no open-ended assignments.
- All financial actions must stay within the pre-allocated ¥3,000 risk reserve; deposit payments capped at ≤¥1,000.
- Output format: exactly three sections titled '✅ Self', '👥 Immediate Family', '👵 Parents' — each containing only bullet points; no explanations, rationale, examples, or passive language.
- Use plain, unambiguous language; avoid jargon, platform-specific UI terms, vendor names, city-specific details, legal citations, or exact budget figures beyond the reserve cap.

## Triggers

- 搬家公司临时取消
- 搬家前72小时内供应商失联或违约
- 搬家服务延迟超两小时
- 搬家预算超支超过5%
- 需要紧急备用搬家公司
- 给我、家人、父母三套分工清单
- 跨城搬家应急任务分派
- 家庭协同应对搬家供应商违约
