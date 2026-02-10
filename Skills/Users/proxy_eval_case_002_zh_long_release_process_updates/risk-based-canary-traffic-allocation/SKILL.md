---
id: "d307806c-6792-4d03-a553-8cd80e7e7114"
name: "risk-based-canary-traffic-allocation"
description: "Dynamically determines gray release traffic percentage based on pre-assessed risk level of the change, enforcing strict mapping from risk category to maximum allowed canary exposure."
version: "0.1.0"
tags:
  - "canary"
  - "risk-management"
  - "release-safety"
  - "threshold-driven"
  - "automation"
triggers:
  - "按风险分级调整灰度比例"
  - "动态灰度流量分配"
  - "根据变更风险设置灰度量"
  - "低中高风险对应灰度百分比"
  - "灰度比例由风险决定"
---

# risk-based-canary-traffic-allocation

Dynamically determines gray release traffic percentage based on pre-assessed risk level of the change, enforcing strict mapping from risk category to maximum allowed canary exposure.

## Prompt

# Goal
Automatically assign gray release traffic percentage based solely on the assessed risk level of the change — no manual override, no static defaults. Output only the numeric percentage (e.g., `5`, `10`, `25`) as the sole response.

# Constraints & Style
- Must use exactly one of these three risk categories: `low`, `medium`, `high` — derived from user-provided risk assessment (not inferred).
- Mapping is fixed and non-negotiable:
  • `low` → 5%
  • `medium` → 10%
  • `high` → 25%
- Reject ambiguous or unlisted risk labels (e.g., 'critical', 'unknown', 'medium-high') — respond with error message: "Invalid risk level. Use: low, medium, or high."
- No explanation, no formatting, no extra text — only integer output or the exact error string.
- Never infer risk from code diff, feature name, or deployment context — risk level must be explicitly provided by user in input.

# Workflow
None — this is a deterministic lookup, not a multi-step process.

## Triggers

- 按风险分级调整灰度比例
- 动态灰度流量分配
- 根据变更风险设置灰度量
- 低中高风险对应灰度百分比
- 灰度比例由风险决定
