---
id: "7ba5d7f2-e0af-4cb7-b0dc-00ea1de09af5"
name: "family-blood-pressure-role-allocation"
description: "Defines and enforces clear, sustainable role assignments and handoff points among family caregivers for home blood pressure monitoring, trend review, escalation, and clinical communication."
version: "0.1.0"
tags:
  - "care-coordination"
  - "role-allocation"
  - "handoff-design"
  - "chronic-care"
  - "family-health"
triggers:
  - "明确家庭成员分工"
  - "血压管理角色分配"
  - "家人交接节点"
  - "照护责任划分"
  - "家庭健康协作机制"
---

# family-blood-pressure-role-allocation

Defines and enforces clear, sustainable role assignments and handoff points among family caregivers for home blood pressure monitoring, trend review, escalation, and clinical communication.

## Prompt

# Goal
Generate a durable, written family role allocation plan for hypertension self-management — specifying who does what, when handoffs occur, and how accountability is maintained across monitoring, interpretation, action, and clinical coordination.

# Constraints & Style
- Must assign exactly four roles: **Recorder**, **Trend Reviewer**, **Escalation Owner**, and **Clinical Liaison** — no role may be left unassigned or shared by default.
- Each role must include: (1) concrete responsibility (e.g., 'enters raw BP + time + context daily'), (2) explicit handoff trigger (e.g., 'when 3 consecutive high readings logged'), and (3) defined output artifact (e.g., 'completes doctor summary template').
- Prohibit vague terms: ban 'help with', 'support', 'assist', 'keep an eye on'; require active verbs and deliverables.
- Exclude medical advice, diagnostic language, or clinical interpretation — this is purely a coordination protocol.
- Output as a clean markdown table with columns: Role | Core Duty | Handoff Trigger | Output Artifact.
- Use neutral, respectful, non-hierarchical language — avoid implying expertise or authority based on age/gender/role.
- All placeholders must be de-identified: e.g., `<FAMILY_MEMBER_A>`, `<FAMILY_MEMBER_B>`, not 'Dad', 'sister', 'you'.

# Workflow
None — this is a one-time structural definition, not a recurring operation.

## Triggers

- 明确家庭成员分工
- 血压管理角色分配
- 家人交接节点
- 照护责任划分
- 家庭健康协作机制
