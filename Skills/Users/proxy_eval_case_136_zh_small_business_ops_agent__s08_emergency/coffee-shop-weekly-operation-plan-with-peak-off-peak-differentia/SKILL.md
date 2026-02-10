---
id: "d1141813-e988-4de0-9af6-9be6c8bd92a7"
name: "coffee-shop-weekly-operation-plan-with-peak-off-peak-differentiation-and-emergency-staffing-protocol"
description: "A reusable weekly operational planning and execution skill for small coffee shops that enforces distinct, role-specific, day-type-aware tactics for weekdays versus weekends across staffing, inventory, promotions, and waste control—and embeds a pre-defined, executable emergency staffing protocol with built-in fatigue safeguards and real-time activation logic."
version: "0.1.2"
tags:
  - "coffee-shop"
  - "operational-planning"
  - "peak-off-peak"
  - "small-business"
  - "resource-allocation"
  - "contingency"
  - "execution"
  - "role-based"
  - "dual-track"
  - "checklist"
triggers:
  - "工作日和周末客流差异大，要分开策略"
  - "客流分峰谷运营"
  - "平日周末不同排班"
  - "突发缺人时要有应急排班方案"
  - "员工临时请假怎么安排"
  - "紧急调班规则"
  - "最后给店长看板和店员执行清单"
  - "生成店长和员工的每日行动清单"
  - "双轨策略落地到岗位动作"
  - "让排班备货促销损耗变成每天要做的事"
  - "店长和店员各做什么"
---

# coffee-shop-weekly-operation-plan-with-peak-off-peak-differentiation-and-emergency-staffing-protocol

A reusable weekly operational planning and execution skill for small coffee shops that enforces distinct, role-specific, day-type-aware tactics for weekdays versus weekends across staffing, inventory, promotions, and waste control—and embeds a pre-defined, executable emergency staffing protocol with built-in fatigue safeguards and real-time activation logic.

## Prompt

# Goal
Generate a weekly operational plan for a small independent coffee shop (15–25㎡, 2–4 staff, 40–70 daily cups) that explicitly differentiates tactics between **weekdays (Mon–Fri)** and **weekends (Sat–Sun)** across four core dimensions: staffing/scheduling, procurement/stock management, promotion execution, and loss/waste control — and includes an integrated, actionable emergency staffing protocol triggered by last-minute staff absences. Output must include two parallel, role-specific execution checklists: one for the store manager (店长) and one for frontline staff (店员), each containing only time-bound, imperative actions labeled by day type or emergency context.

# Constraints & Style
- Must separate all recommendations into two clearly labeled sections: "Weekdays (Mon–Fri)" and "Weekends (Sat–Sun)" — no blended or generic advice.
- For each dimension, specify: (a) the *why* (traffic pattern rationale), (b) one concrete, time-bound action (≤30 min to execute), (c) clear ownership (e.g., "Store Manager", "Barista on Duty"), and (d) a lightweight verification method (e.g., photo log, shared sheet update, timestamped message).
- Emergency staffing protocol must adapt to day type: weekday minimum safe coverage = 2 staff; weekend minimum = 3 staff. If coverage falls below minimum during peak hours (weekday 7:30–9:30 & 11:30–14:00; weekend 10:00–18:00), activate "Pause Protocol": post digital notice (QR + 3-sentence message), pause new orders for 20 min, fulfill only in-progress tickets, and dispatch manager to assist.
- Never assign >6 consecutive working days or >5 consecutive days without a full 24h rest period — if emergency coverage would breach this, escalate to owner for paid overtime or cancellation.
- Prohibit solo operation during peak hours. Prohibit assumptions about digital systems: all tools must be free, mobile-accessible, and require ≤5 min setup (e.g., shared spreadsheet, group chat, printed checklist). No ERP/POS integrations unless user specifies.
- Exclude all one-off business facts: no real names, locations, dates, product SKUs, supplier names, or financial figures beyond illustrative ranges (e.g., "≤4.5%" is allowed; "$2.87" is not).
- Never prescribe fixed hours — use relative anchors like "pre-peak", "mid-afternoon lull", or "last 90 minutes before closing".
- All promotional logic must include cost-awareness: explicitly note whether the tactic consumes surplus stock, targets high-margin items, or protects baseline gross margin (≥60%).
- All waste controls must include a human-centered accountability loop (e.g., daily log + same-day feedback, weekly recognition ritual).
- Emergency fallback actions must use only existing tools: shared doc, pre-approved substitute list (max 3 names), and pre-written customer comms templates.
- Output must be action-scannable: use bullet points, bold headers, and time-bound steps — no explanations or rationale outside the "why" clause in the main plan.
- Add two dedicated, tool-agnostic execution sections at the end: "【店长看板】" and "【店员执行清单】", each containing 5–8 imperative, present-tense, shift-contained bullet points. Label all items by context: "[工作日]", "[周末]", or "[应急]". No rationale, metrics, brand names, or UI references. No tables or nested formatting — only top-level bullets under each header.
- Language: Simplified Chinese for all role-specific execution content; English retained for structural headers and cross-dimensional planning logic to preserve interoperability and de-identification.

# Workflow
1. Infer weekday vs weekend traffic profile from user input (e.g., "workday客流低 but weekend busy", "students Mon–Fri, families Sat–Sun"). If not specified, default to: Weekdays = steady but lower volume, higher repeat rate; Weekends = 2–3× volume spike, more first-time/impulse customers.
2. For each of the four dimensions (staffing, procurement, promotion, waste), generate parallel weekday and weekend rows using the structure in # Constraints & Style.
3. Embed the emergency staffing protocol as a standalone, scannable section titled "Emergency Staffing Protocol", activated when ≥1 scheduled staff cancel with <24h notice — including day-type-specific minimums, fatigue buffers (e.g., no barista does >2 hrs continuous pulling shots), substitute contact workflow, and incident logging.
4. Generate "【店长看板】" and "【店员执行清单】" by distilling only physically executable, shift-contained actions per role — filtered through weekday/weekend and emergency awareness — and deduplicating overlapping items in favor of the most contextually specific version.
5. Output only the plan table, supporting rationale, embedded protocol, and the two execution checklists — no intros, offers, or tool-upgrade prompts unless user explicitly requests them.

## Triggers

- 工作日和周末客流差异大，要分开策略
- 客流分峰谷运营
- 平日周末不同排班
- 突发缺人时要有应急排班方案
- 员工临时请假怎么安排
- 紧急调班规则
- 最后给店长看板和店员执行清单
- 生成店长和员工的每日行动清单
- 双轨策略落地到岗位动作
- 让排班备货促销损耗变成每天要做的事
