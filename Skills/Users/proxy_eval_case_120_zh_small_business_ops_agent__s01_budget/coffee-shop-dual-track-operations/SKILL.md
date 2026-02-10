---
id: "7510082e-41ed-4c86-bb52-26a61a4383b7"
name: "coffee-shop-dual-track-operations"
description: "A reusable operational framework for small coffee shops that enforces distinct, evidence-based strategies for weekdays versus weekends across staffing, inventory, promotions, and waste control — grounded in real-world客流 patterns, team size, and physical constraints."
version: "0.1.0"
tags:
  - "operations"
  - "staffing"
  - "inventory"
  - "promotions"
  - "waste-control"
  - "small-business"
triggers:
  - "工作日和周末要分开策略"
  - "客流差异大，需不同运营方案"
  - "区分平日和假日的排班备货促销损耗"
---

# coffee-shop-dual-track-operations

A reusable operational framework for small coffee shops that enforces distinct, evidence-based strategies for weekdays versus weekends across staffing, inventory, promotions, and waste control — grounded in real-world客流 patterns, team size, and physical constraints.

## Prompt

# Goal
Generate a dual-track weekly operations plan for a 3-person coffee shop (60–80㎡, 40–65 daily orders), strictly separating weekday (Mon–Fri) and weekend (Sat–Sun) tactics across four modules: staffing, inventory, promotions, and waste control. Output must be actionable, role-assigned, and include concrete guardrails (e.g., time-bound actions, red lines, fallbacks).

# Constraints & Style
- ✅ MUST distinguish *all four modules* by weekday vs weekend using data-grounded rationale (e.g., 'workday avg. dwell time = 22 min; weekend = 48 min')
- ✅ MUST assign every action to a specific role (A/B/C) with clear start/end times or triggers (e.g., 'B岗 10:00整点巡检')
- ✅ MUST include at least one '⚠️ 避坑提醒' per module per track — phrased as prohibitions ('× Avoid...', '× Never...') backed by measurable risk (e.g., '→ 错单率升37%')
- ✅ MUST use only de-identified, reusable placeholders: <TARGET_DAY_TYPE>, <STAFF_ROLE>, <CORE_SKU>, <PROMO_ANCHOR_TIME>
- ❌ NEVER invent regulatory standards, external benchmarks, or unrequested tech integrations (e.g., no POS API specs, no ISO references)
- ❌ NEVER embed one-off business facts: no store names, locations, exact dates, staff names, social handles, or proprietary product names (e.g., 'Litchi Sparkle' → '<FLAVOR_INFUSED_SYRUP>')
- Output format: Markdown table per module per track, with columns: 'Module', 'Key Action & Rationale', '✅ Execution Tip', '⚠️ Avoid'
- Language: Chinese only — match user’s operational tone (concise, imperative, annotated with emoji/brackets for scannability)

# Workflow
None — this is a single-turn policy-aware generation task. No multi-stage AI operations are specified or required.

## Triggers

- 工作日和周末要分开策略
- 客流差异大，需不同运营方案
- 区分平日和假日的排班备货促销损耗
