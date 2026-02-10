---
id: "f7e90af1-b650-4fbf-9c22-76cfe7b7264c"
name: "cross-city-move-family-role-allocation"
description: "Generates role-specific, time-bound task checklists for cross-city relocation, assigning distinct responsibilities to the primary mover, co-resident family members, and aging parents based on capability, access, and accountability boundaries."
version: "0.1.0"
tags:
  - "relocation"
  - "role-allocation"
  - "family-coordination"
  - "task-decomposition"
triggers:
  - "给我家人父母三套分工清单"
  - "搬家任务怎么分给不同人"
  - "跨城搬家角色分工"
  - "老人孩子怎么参与搬家"
  - "家庭成员搬家责任划分"
---

# cross-city-move-family-role-allocation

Generates role-specific, time-bound task checklists for cross-city relocation, assigning distinct responsibilities to the primary mover, co-resident family members, and aging parents based on capability, access, and accountability boundaries.

## Prompt

# Goal
Generate three parallel, non-overlapping task checklists — for the primary mover (‘Me’), immediate family co-relocating (‘Family’), and aging parents staying behind or joining later (‘Parents’) — covering all core relocation domains: housing search, moving logistics, utility migration, and address updates. Each list must be executable independently, with clear ownership, no shared dependencies, and explicit handoff points where applicable.

# Constraints & Style
- Must de-identify all location, personal, and financial specifics: replace cities with <SOURCE_CITY> and <TARGET_CITY>; replace budgets, dates, and IDs with placeholders (e.g., <BUDGET>, <MOVE_DATE>, <UTILITY_ACCOUNT_NUMBER>).
- Assign tasks strictly by functional capacity: ‘Me’ handles contractual, financial, and platform-mediated actions; ‘Family’ handles physical coordination, documentation prep, and real-time verification; ‘Parents’ handle only low-friction, identity-verified, or delegation-enabled actions (e.g., signing pre-filled forms, confirming receipt, attending scheduled appointments with support).
- Prohibit any task requiring mobility, tech fluency, or decision-making beyond verified capability (e.g., no app logins, no live negotiation, no unassisted travel).
- All deadlines must be relative (e.g., ‘D−7’, ‘D+3’) anchored to <MOVE_DATE>, not calendar dates.
- Output format: three Markdown tables side-by-side (or stacked if narrow), each with columns: Task | When | Owner Action | Verification Required.
- Never include advice, explanations, or rationale — only executable steps.

# Workflow
1. Parse the relocation scope from user context: confirm it is domestic cross-city (not international), involves rental housing, and includes utility transfer and multi-party address updates.
2. For each domain (housing, moving, utilities, address), decompose tasks into atomic, assignable units.
3. Allocate each unit using the capacity-based rule set above.
4. Resolve interdependencies by inserting explicit handoff markers (e.g., ‘Me provides signed lease copy to Family by D−5’).
5. Output only the three finalized tables — no intro, summary, or metadata.

## Triggers

- 给我家人父母三套分工清单
- 搬家任务怎么分给不同人
- 跨城搬家角色分工
- 老人孩子怎么参与搬家
- 家庭成员搬家责任划分
