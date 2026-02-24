---
id: "5c0aa52d-c3d1-4b78-959f-f797e9a1cf89"
name: "reliable-moving-provider-fallback-protocol"
description: "A time-bound, role-distributed contingency protocol triggered when a contracted moving provider cancels with ≤12 hours notice; ensures zero-delay relocation execution via pre-vetted alternatives, digitally captured handoffs, and clear ownership across primary mover, family, and remote support."
version: "0.1.2"
tags:
  - "contingency"
  - "moving"
  - "reliability"
  - "time-bound"
  - "fallback"
  - "family-coordination"
  - "role-allocation"
  - "execution-only"
triggers:
  - "搬家公司临时取消"
  - "搬家司机失联"
  - "12小时内换车"
  - "原定搬家日被取消"
  - "紧急替换搬家公司"
---

# reliable-moving-provider-fallback-protocol

A time-bound, role-distributed contingency protocol triggered when a contracted moving provider cancels with ≤12 hours notice; ensures zero-delay relocation execution via pre-vetted alternatives, digitally captured handoffs, and clear ownership across primary mover, family, and remote support.

## Prompt

# Goal
Ensure zero-delay relocation execution when a primary moving provider cancels within 12 hours of scheduled service, by activating a verified fallback workflow that guarantees same-day or next-morning replacement with equivalent reliability (insurance, tracking, labor, and scope coverage), full continuity of critical logistics (access, utilities, documentation), and no financial leakage.

# Constraints & Style
- Must not require user to search, negotiate, vet, sign up for, or seek external approvals for new providers in real time — all contacts, templates, permissions, and pre-negotiated terms must be established prior to move week.
- All fallback options must be pre-qualified for: licensed operation, minimum $50k liability insurance, GPS-tracked vehicles, and documented history of <2% last-minute cancellation rate.
- Fallback activation must complete core handoff (confirmed booking, driver details, revised timeline) within 45 minutes of primary cancellation confirmation.
- Output must be a ready-to-execute, role-assigned checklist — no explanations, no optional steps, no verbal assurances.
- Language: concise, imperative, role-assigned (e.g., "You call…", "Family updates…", "Parents verify…").
- Never include unverified platforms (e.g., generic 'Craigslist' or 'Facebook Marketplace') or individual drivers without corporate backing or pre-authorized backup transport.
- All outputs (e.g., shared tracking links, signed contracts, photo/video evidence, receipts) must be digitally captured and stored in the '🚨搬家应急包' folder.
- Prohibited: negotiating price, deferring verification (e.g., skipping ID + order number check before key handover), or using unvetted drivers.
- Output only three labeled sections: `👤 You`, `👨‍👩‍👧 Family`, `👵👴 Parents` — each containing exactly 3–5 bullet points.
- Every bullet must be an atomic, observable action (e.g., 'send SMS with new truck time to物业', not 'coordinate with物业').
- All actions must require ≤60 seconds to initiate and leave digital or physical evidence (screenshot, photo, message timestamp, labeled box).
- Exclude explanations, rationale, or conditional logic (e.g., no 'if… then…' or 'you may want to…').
- Omit all city names, personal identifiers, dates, prices, or vendor names — use placeholders like `<CITY_A>`, `<CITY_B>`, `<ORDER_ID>`.
- Never include setup instructions (e.g., 'save this number first') — assume prep is complete.
- Use plain imperative verbs: 'Screenshot', 'Dial', 'Label', 'Photo', 'Hand over'.
- Max 1 line per bullet; max 12 words per line.
- No markdown tables, no emojis, no bold/italics.
- Final output must be copy-paste ready for printing or texting — no extra text before or after the three sections.

## Triggers

- 搬家公司临时取消
- 搬家司机失联
- 12小时内换车
- 原定搬家日被取消
- 紧急替换搬家公司
