---
id: "e810e2a8-c108-4fcf-aa34-6d410329aff8"
name: "cross-city-moving-role-allocation-and-risk-mitigation"
description: "A reusable, de-identified protocol for assigning non-overlapping responsibilities across user, immediate family, and parents during a cross-city relocation — while embedding top-three operational risk countermeasures directly into each role’s checklist via concrete, time-bound, budget-aware contingency actions."
version: "0.1.1"
tags:
  - "role-allocation"
  - "risk-mitigation"
  - "family-coordination"
  - "relocation"
  - "contingency-planning"
  - "budget-constrained"
triggers:
  - "给我家人父母三套分工清单"
  - "搬家角色分工"
  - "家庭成员任务分配"
  - "跨城搬家谁负责什么"
  - "用户家人父母分工"
  - "跨城搬家三大风险"
  - "搬家核心风险预案"
  - "搬迁风险应对清单"
---

# cross-city-moving-role-allocation-and-risk-mitigation

A reusable, de-identified protocol for assigning non-overlapping responsibilities across user, immediate family, and parents during a cross-city relocation — while embedding top-three operational risk countermeasures directly into each role’s checklist via concrete, time-bound, budget-aware contingency actions.

## Prompt

# Goal
Generate three parallel, role-specific checklists (User / Family / Parents) for a cross-city move, each containing only actions matching the role’s authority, proximity, access, and decision scope — with zero task duplication, explicit handoff points, and integrated top-three risk-mitigated actions.

# Constraints & Style
- Must be fully de-identified: replace all location names, dates, addresses, company names, personal identifiers, and budget values with placeholders (e.g., <ORIGIN_CITY>, <DESTINATION_CITY>, <MOVE_DATE>, <PRIMARY_CONTACT>, <BUDGET_CEILING>).
- User list: actions requiring final approval, financial control, legal signing, real-time judgment, or risk escalation (e.g., contract review, payment release, emergency vendor switch, electronic章 on emergency contract).
- Family list: actions requiring co-location, physical execution, or shared access — including risk-triggered on-site responses (e.g., packing supervision, driver greeting, box labeling, on-site验收, photo log capture upon delivery delay).
- Parents list: actions requiring remote oversight, documentation cross-check, or low-risk verification — including risk-triggered remote validations (e.g., photo log review within 2h of upload, invoice reconciliation against <BUDGET_CEILING> × 10% buffer, template signing upon trigger confirmation).
- Every item must include a clear success criterion (e.g., "✅ Photo of signed contract received", "✅ All <ROOM_NAME> boxes labeled with color + room code", "✅ Confirmed via call that <SERVICE_PROVIDER> confirmed installation time").
- No vague verbs: ban 'coordinate', 'support', 'help', 'assist'; use only concrete verbs: 'sign', 'upload', 'call', 'label', 'verify', 'forward', 'confirm', 'switch', 'capture', 'reconcile'.
- Exactly three risks must be embedded — ranked by likelihood × impact — each mapped to at least one role-specific action with: (1) de-identified trigger condition (e.g., 'primary vendor cancels <48h pre-move'), (2) precise response window (e.g., 'within 12 hours'), and (3) role-assigned action using only verified tools/channels (e.g., 'use only vendors with road transport license + public社保 record').
- Output format: three Markdown tables side-by-side (User | Family | Parents), each with columns: Action | Success Criterion | Deadline (<MOVE_DATE> ± X days). Risk-mitigation actions must appear inline — not as separate section.
- Never invent tasks or standards; only allocate what is logically required by core workflow (housing handover, moving logistics, utility migration, address update) and pre-validated risk countermeasures.

# Workflow
None — this is a static role-and-risk mapping output. Do not add steps, explanations, or conditional logic.

## Triggers

- 给我家人父母三套分工清单
- 搬家角色分工
- 家庭成员任务分配
- 跨城搬家谁负责什么
- 用户家人父母分工
- 跨城搬家三大风险
- 搬家核心风险预案
- 搬迁风险应对清单
