---
id: "9d1c6e2b-bfbe-49a4-a83e-e5ab2827fe3e"
name: "cross-city-moving-role-allocation"
description: "A reusable, de-identified framework for assigning relocation tasks across three stakeholder groups — the primary mover, their immediate family, and their parents — based on capability, availability, risk sensitivity, and time-bound execution windows, with distinct outputs for operational rigor and shared clarity."
version: "0.1.1"
tags:
  - "relocation"
  - "role-allocation"
  - "family-coordination"
  - "task-delegation"
  - "emergency-response"
triggers:
  - "给我家人父母三套分工清单"
  - "生成三方搬家任务分配"
  - "如何让父母和家人一起参与搬家但不混乱"
  - "跨城搬家角色分工"
---

# cross-city-moving-role-allocation

A reusable, de-identified framework for assigning relocation tasks across three stakeholder groups — the primary mover, their immediate family, and their parents — based on capability, availability, risk sensitivity, and time-bound execution windows, with distinct outputs for operational rigor and shared clarity.

## Prompt

# Goal
Generate two complementary versions of a time-anchored, role-specific task allocation plan for a cross-city move: (1) a simplified version for family members and parents, using plain-language imperatives and zero decision authority; (2) an operational version for the primary mover, specifying strict T+X time windows, mandatory verification actions, required tools/platforms, and non-negotiable red-line constraints.

# Constraints & Style
- Must produce exactly three parallel checklists — one per group (primary mover, immediate family, parents) — using consistent structure: [Task] | [Owner] | [Deadline] | [Critical Success Condition]. No task may appear in more than one list.
- High-risk or legally binding actions (e.g., contract signing, ID-based verifications, financial transfers) must be assigned *only* to the primary mover.
- Parents’ list must contain *zero* digital-first or real-time coordination tasks (e.g., no app logins, no live tracking); only offline-verifiable, low-frequency, preparation-oriented actions (e.g., packing designated boxes, confirming document copies).
- Family list may include shared physical tasks (e.g., labeling, loading) but *excludes* administrative/legal/financial decisions.
- All deadlines must be expressed relative to T-day (moving day) using standardized offsets: T−7, T−3, T−1, T+0, etc.
- The simplified version must contain only: role name, 3–5 bullet points in imperative voice (e.g., "Send the address map with elevator code"), zero jargon, no timecodes, and no decision authority — all decisions rest with the primary mover.
- The operational version must include: exact time windows (e.g., "T+0:00–0:05"), mandatory verification actions (e.g., "Screenshot and post to emergency relocation group chat"), required tools (e.g., "Use <VERIFIED_E_SIGN_PLATFORM> → 'Immediate Signing' flow"), and non-negotiable red lines (e.g., "Never pay >30% deposit without signed contract and insurance confirmation").
- Both versions must reference a shared coordination channel (e.g., "emergency relocation group chat") and enforce information traceability (all actions must leave auditable evidence).
- Use placeholder syntax: <ORIGIN_CITY>, <DESTINATION_CITY>, <FAMILY_SIZE>, <PARENTS_AGE_RANGE>, <VERIFIED_E_SIGN_PLATFORM>, <VERIFIED_LOGISTICS_PLATFORM>.
- Never specify names, IDs, contact details, vendor names, URLs, phone numbers, exact dates, budget figures, or unvalidated tools/platforms — only retain those explicitly named and validated by user in prior turns.
- Output only plain Markdown tables and bullet lists — no prose, no explanations, no headers beyond the three list titles and version labels.

## Triggers

- 给我家人父母三套分工清单
- 生成三方搬家任务分配
- 如何让父母和家人一起参与搬家但不混乱
- 跨城搬家角色分工
