---
id: "2843d1b9-f4a0-4caa-b3f1-261e6cac36a3"
name: "cross-city-moving-role-allocation"
description: "A reusable, de-identified protocol for assigning搬家-related tasks across three stakeholder groups — the primary mover, their immediate family (co-residents), and parents (remote or non-cohabiting support) — based on capability, proximity, authority, and risk sensitivity."
version: "0.1.0"
tags:
  - "role-allocation"
  - "moving-planning"
  - "family-coordination"
  - "task-delegation"
triggers:
  - "三套分工清单"
  - "家人父母分工"
  - "搬家角色分配"
  - "责任划分模板"
  - "跨城搬家任务分派"
---

# cross-city-moving-role-allocation

A reusable, de-identified protocol for assigning搬家-related tasks across three stakeholder groups — the primary mover, their immediate family (co-residents), and parents (remote or non-cohabiting support) — based on capability, proximity, authority, and risk sensitivity.

## Prompt

# Goal
Generate a clear, balanced, and executable three-tier task allocation plan for a cross-city move, assigning responsibilities to: (1) the primary mover (user), (2) co-resident family members (e.g., spouse, adult children living together), and (3) parents (typically remote, advisory, or logistical supporters). The output must be role-specific, avoid overlap, and reflect realistic capacity (e.g., parents do not handle utility logins or contract signing).

# Constraints & Style
• Must exclude all personally identifiable information: no names, cities, dates, company names, phone numbers, or account details.
• Assign only tasks that match each group’s typical access, authority, and physical/logistical capacity:
  – Primary mover: handles all legal, financial, digital, and time-critical actions (e.g., contract signing, app-based address updates, payment, vendor coordination).
  – Co-resident family: handles shared physical execution (e.g., packing, cleaning, labeling, in-person utility appointments, moving-day supervision).
  – Parents: limited to low-risk, high-trust support — e.g., holding emergency funds, storing critical documents offsite, reviewing draft communications, or hosting pre-move stays. Never assign them system logins, financial transactions, or regulatory filings.
• Use plain, imperative language (e.g., "Confirm broadband installation slot", "Pack kitchenware using labeled boxes").
• Output only a clean markdown table with exactly three columns: "Primary Mover", "Co-Resident Family", "Parents" — no explanations, no headers beyond column titles, no extra formatting.
• Do not invent steps; only allocate tasks already implied by standard cross-city moving workflows (e.g., address change, utility transfer, packing, vendor coordination).
• Never include vague or generic advice (e.g., "be supportive", "stay informed"). Every item must be an observable, assignable action.

# Workflow
None — this is a one-time role-mapping operation. No iterative or conditional logic required.

## Triggers

- 三套分工清单
- 家人父母分工
- 搬家角色分配
- 责任划分模板
- 跨城搬家任务分派
