---
id: "7241342f-6279-49af-921f-031732fc5ded"
name: "small-coffee-shop-emergency-staffing-protocol"
description: "A reusable, time-bound, tiered protocol for small independent coffee shops (2–3 staff) to activate during sudden staffing shortages, ensuring minimal service disruption while preserving safety compliance, labor legality, food safety, and brand-consistent service — all within a strict 7-day operational window."
version: "0.1.2"
tags:
  - "staffing"
  - "contingency"
  - "compliance"
  - "small-business"
  - "coffee-shop"
  - "emergency-response"
  - "time-bound"
  - "safety-critical"
triggers:
  - "突发缺人时要有应急排班方案"
  - "员工临时请假怎么顶上"
  - "没人上班的应急办法"
  - "小咖啡店突然少一个人怎么办"
  - "应急排班模板"
  - "把时间压缩一周"
  - "哪些步骤不能删"
  - "突发缺人时一周内必须做完什么"
---

# small-coffee-shop-emergency-staffing-protocol

A reusable, time-bound, tiered protocol for small independent coffee shops (2–3 staff) to activate during sudden staffing shortages, ensuring minimal service disruption while preserving safety compliance, labor legality, food safety, and brand-consistent service — all within a strict 7-day operational window.

## Prompt

# Goal
Generate an immediate, executable emergency staffing plan for a small independent coffee shop (2–3 employees, daily客流 30–80) when one or more staff cancel with <24h notice — maintaining safety, legal compliance, and minimum viable service across all shifts. Output **exactly two sections**, labeled "### Store Manager Dashboard" and "### Staff Execution Checklist", both strictly aligned with the three-tiered emergency levels (Level 1: missing 1 person; Level 2: only 1 person present; Level 3: zero staff on-site).

# Constraints & Style
- Must be triggered *only* by unscheduled absence (sick leave, emergency, no-show), not planned time off.
- Never require any employee to work >10 consecutive hours or violate mandatory rest intervals (≥10h between shifts).
- Prioritize: (1) food safety compliance, (2) equipment safety, (3) core customer touchpoints (order intake, payment, handoff), (4) brand-consistent minimum service level.
- Explicitly prohibit: assigning untrained staff to espresso machine operation, milk steaming, or cash handling without prior documented competency check.
- **Dashboard must include**: (1) real-time trigger assessment prompts (e.g., 'Check today’s pre-orders + weather + confirmed absences'), (2) level-determination logic (explicit if/then rules), (3) comms templates (one-line announcement + one-line customer compensation promise with clear time-bound delivery, e.g., '12-minute guarantee'), and (4) post-event accountability step (e.g., 'Record root cause in [shared log] before closing' and 'Complete mandatory 10-minute voice-based review same day').
- **Checklist must be**: (1) strictly sequential (numbered 1–5), (2) verb-led and time-bound where possible (e.g., 'At shift start, switch menu board to “Today’s 3 Fixed Options”'), (3) limited to ≤5 items per level, and (4) omit all explanations, rationale, or tool names — only observable actions.
- Preserve non-deletable time-critical steps: '1看2拆3补位' triage sequence executed within 10 minutes of vacancy confirmation; Level activation based on headcount *at shift start*; mandatory same-day 10-minute voice review; weekly verification of pre-staged 'emergency drawer' (pre-packed meals, printed SOPs, flash-contact info); and all customer-facing messaging must include explicit compensation (e.g., 'free drink voucher') and time-bound delivery promise.
- Never invent new levels, roles, thresholds, or compensation mechanics beyond those user-confirmed: Level 1/2/3 definitions, 'pre-order priority', 'fixed套餐', and mandatory compensation.
- De-identify all specifics: replace location names, brand names, exact times (use relative offsets like 'at shift start'), monetary values (use '<COST_UNIT>'), and personal identifiers with placeholders.
- Use plain, imperative English. No markdown tables, no emojis, no bold/italics.
- Output must include: (a) role consolidation rules, (b) non-negotiable coverage thresholds per shift, (c) auto-downgraded service modes (e.g., 'no customizations', 'pre-set combos only'), and (d) real-time communication script for informing customers.

# Workflow
1. Assess gap: Identify which shift(s) and role(s) are missing (e.g., 'Saturday 12:00–20:00全能岗 absent').
2. Activate role merge: Apply pre-approved consolidation rules (e.g., 'If全能岗 missing on weekend, shift all drink prep to早班主力出品岗; suspend hand-pour service and limit milk options to oat/whole only').
3. Enforce service downgrade: Automatically disable non-core menu items and customization options in POS or ordering board; display physical 'Today’s Simplified Menu' sign.
4. Deploy comms: Deliver exact customer-facing script (e.g., 'Hi there — today we’re running a lean, focused service to keep things smooth! You’ll get your favorite drinks faster, and we’ve prepped our top 3 combos for quick pickup.') including explicit compensation and time-bound delivery promise.
5. Log & trigger follow-up: Record incident in shared 'Staff Gap Log'; auto-send alert to backup contact list if gap persists >2 shifts; complete mandatory 10-minute voice review same day; verify 'emergency drawer' contents weekly; conduct full dry-run of highest-risk level on Day 7.

## Triggers

- 突发缺人时要有应急排班方案
- 员工临时请假怎么顶上
- 没人上班的应急办法
- 小咖啡店突然少一个人怎么办
- 应急排班模板
- 把时间压缩一周
- 哪些步骤不能删
- 突发缺人时一周内必须做完什么
