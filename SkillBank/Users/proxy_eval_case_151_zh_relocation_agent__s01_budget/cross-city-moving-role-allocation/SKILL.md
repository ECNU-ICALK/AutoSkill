---
id: "b03f5103-b073-4c5d-8ac1-15c36195d844"
name: "cross-city-moving-role-allocation"
description: "A reusable, de-identified framework for assigning搬家-related tasks across three stakeholder groups — the primary mover, their immediate family (co-residents), and parents (remote supporters) — based on proximity, capability, and accountability boundaries."
version: "0.1.0"
tags:
  - "role-allocation"
  - "task-delegation"
  - "moving-planning"
  - "family-coordination"
triggers:
  - "给我家人父母三套分工清单"
  - "三人分工表"
  - "搬家任务分给三个人"
  - "角色分配清单"
  - "谁负责什么"
---

# cross-city-moving-role-allocation

A reusable, de-identified framework for assigning搬家-related tasks across three stakeholder groups — the primary mover, their immediate family (co-residents), and parents (remote supporters) — based on proximity, capability, and accountability boundaries.

## Prompt

# Goal
Generate a clear, balanced, and executable three-tier role allocation plan for a cross-city move, assigning concrete responsibilities to: (1) the primary mover (user), (2) co-resident family members (e.g., spouse/partner/older children), and (3) geographically distant parents — with no overlap, no assumed availability, and strict separation of physical vs. remote actions.

# Constraints & Style
- Must produce exactly three parallel lists — labeled "You", "Family", and "Parents" — each containing only actionable, discrete tasks (no explanations, no rationale).
- Tasks must be mutually exclusive: no task appears in more than one list; no list delegates work to another.
- Physical presence required? → assign only to "You" or "Family" (never "Parents").
- Remote/administrative/actionable-by-phone-or-app? → may go to any tier, but prefer "Parents" only when verifiably low-friction (e.g., calling banks, updating addresses via web forms) and explicitly authorized by user.
- Exclude all time-bound scheduling (e.g., "Week 3") — only role-based ownership.
- Never include budget decisions, vendor selection, or legal judgment — those remain with "You" unless explicitly delegated in user input.
- Use plain imperative verbs: "Submit", "Call", "Upload", "Photograph", "Confirm", etc.
- No markdown tables; use bullet lists only.
- All content must be fully de-identified: no city names, provider names, app names, or personal identifiers.

# Workflow
None — this is a static role-mapping output. Do not invent steps, phases, or dependencies.

## Triggers

- 给我家人父母三套分工清单
- 三人分工表
- 搬家任务分给三个人
- 角色分配清单
- 谁负责什么
