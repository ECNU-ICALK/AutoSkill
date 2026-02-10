---
id: "9f9a1fe8-f75c-45d7-a9da-950120689824"
name: "family-claim-role-allocation"
description: "Generates a clear, concise role-and-handoff map for home insurance claims, assigning responsibilities to family members or stakeholders and defining explicit交接 points between them."
version: "0.1.0"
tags:
  - "role-allocation"
  - "family-claim"
  - "handoff"
  - "non-technical"
triggers:
  - "明确家庭成员/参与者分工和交接节点"
  - "家人分工表"
  - "理赔角色分配"
  - "谁负责什么、什么时候交接"
---

# family-claim-role-allocation

Generates a clear, concise role-and-handoff map for home insurance claims, assigning responsibilities to family members or stakeholders and defining explicit交接 points between them.

## Prompt

# Goal
Produce a minimal, scannable role allocation table for a home property insurance claim, specifying who does what and exactly when responsibility transfers — optimized for non-expert family users.

# Constraints & Style
- Use only plain, non-technical language (e.g., 'calls the insurer' not 'initiates contact with claims handler')
- Assign roles to generic family labels: 'Primary Contact', 'Document Keeper', 'On-Site Coordinator', 'Escalation Lead'
- Each role must have: (1) 1-sentence duty, (2) 1 concrete handoff trigger (e.g., 'when first inspection is scheduled'), (3) max 3 bullet actions
- No dates, names, policy numbers, or case-specific facts — use placeholders like <REPORT_DATE> or <INSURER_NAME>
- Output only the table — no intro, no explanation, no examples
- Total length ≤ 15 lines

# Workflow
None — this is a single-output capability: generate the table directly from the input context.

## Triggers

- 明确家庭成员/参与者分工和交接节点
- 家人分工表
- 理赔角色分配
- 谁负责什么、什么时候交接
