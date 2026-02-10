---
id: "50091841-d761-457d-b532-a2efcadd2a74"
name: "small-cafe-weekly-operation-plan-with-weekday-weekend-differentiation"
description: "A reusable weekly operational planning and revision framework for small independent coffee shops that explicitly separates and dynamically adjusts weekday and weekend strategies across staffing, inventory, promotions, and waste control — grounded in observed traffic pattern divergence and validated by comparative KPI analysis."
version: "0.1.1"
tags:
  - "coffee-shop"
  - "operational-planning"
  - "traffic-differentiation"
  - "waste-control"
  - "staffing-optimization"
  - "operational-review"
  - "kpi-driven-adjustment"
triggers:
  - "工作日和周末客流差异大"
  - "要分开策略"
  - "区分平日和周末运营"
  - "客流不均衡怎么排班"
  - "周末爆单怎么备货"
  - "每周复盘"
  - "双轨策略怎么调整"
  - "工作日周末数据对比后怎么改"
  - "损耗率差异大怎么优化"
  - "促销核销率不一致怎么办"
---

# small-cafe-weekly-operation-plan-with-weekday-weekend-differentiation

A reusable weekly operational planning and revision framework for small independent coffee shops that explicitly separates and dynamically adjusts weekday and weekend strategies across staffing, inventory, promotions, and waste control — grounded in observed traffic pattern divergence and validated by comparative KPI analysis.

## Prompt

# Goal
Generate a weekly operational plan for a small independent coffee shop (2–3 staff, 15–30㎡, mixed dine-in/takeaway) that applies distinct, evidence-based strategies for weekdays (Mon–Fri) versus weekends (Sat–Sun), grounded in differential customer traffic volume and behavior — and revise it using last week’s actual performance data against four paired KPIs.

# Constraints & Style
- MUST separate all four core modules — staffing (排班), inventory prep (备货), promotions (促销), and waste control (损耗控制) — into clearly labeled weekday-specific and weekend-specific actions.
- MUST quantify traffic assumptions: weekdays = stable but lower volume (e.g., 30–50 daily orders); weekends = peak, volatile, and time-clustered (e.g., Sat 10–12 & 16–18, Sun 10–13).
- MUST assign concrete, executable tactics per day — no vague advice. Each tactic must include at least one of: time bound (e.g., "within 30 min"), ownership (e.g., "lead by barista A"), threshold (e.g., "if wait > 3 min, activate backup station"), or verification step (e.g., "photo log required").
- MUST embed cross-module coordination: e.g., weekend promotion must use high-risk-perishable stock identified during weekday inventory review; weekday staff training must prepare for weekend peak SOPs.
- MUST support post-cycle revision: after plan execution, compare exactly four paired metrics — (1) weekday vs. weekend single-order waste rate (%), (2) weekday vs. weekend average out-the-door time (seconds), (3) weekday vs. weekend promotion redemption rate (%), (4) weekday vs. weekend external platform cancellation rate (%) — and apply at most one adjustment per metric where delta > ±15%: (a) tighten threshold, (b) shift timing, or (c) cross-pollinate roles/tactics between tracks.
- NEVER invent new roles, tools, thresholds, or business logic — only modify or reuse existing elements from the dual-track framework.
- Output in clear markdown table + bullet format for the plan; revision log must be plain-text, bullet-point only — no tables, no markdown, no explanations beyond change and trigger condition.
- Use Chinese. No markdown code blocks or placeholders like <TOKEN>. De-identify all people, locations, dates, systems (e.g., 'main barista', 'POS system', 'morning shift').
- Exclude generic business advice (e.g., "listen to customers"), theoretical models, or unvalidated best practices. Only include tactics proven effective in ≤3-person café contexts.
- Do not invent tools, software names, or external references unless user previously adopted them (e.g., Tencent Docs is allowed only if confirmed). If uncertain, omit.

# Workflow
1. Infer baseline traffic pattern: confirm weekday vs weekend divergence is the primary driver (not seasonality, events, or staffing shortage).
2. For each of the four modules, define:
   a) Weekday strategy: optimized for consistency, skill development, and proactive stock/waste management.
   b) Weekend strategy: optimized for throughput, real-time adjustment, and loss mitigation under pressure.
3. Enforce linkage: e.g., Thursday’s waste analysis must directly inform Saturday’s promotion; Friday’s pre-stock must reflect Sunday’s forecasted drop-off.
4. After execution, collect last week’s four paired KPIs from point-of-sale and manual logs; compute weekday–weekend absolute delta; for each delta > ±15%, apply exactly one pre-defined adjustment type to the underperforming track.
5. Output only the plan or revision log — no offers, no follow-up questions, no tool generation prompts.

## Triggers

- 工作日和周末客流差异大
- 要分开策略
- 区分平日和周末运营
- 客流不均衡怎么排班
- 周末爆单怎么备货
- 每周复盘
- 双轨策略怎么调整
- 工作日周末数据对比后怎么改
- 损耗率差异大怎么优化
- 促销核销率不一致怎么办
