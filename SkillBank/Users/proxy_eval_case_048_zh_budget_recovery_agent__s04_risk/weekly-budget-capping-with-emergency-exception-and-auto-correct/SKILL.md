---
id: "e4027214-7b0c-4112-9259-1706b0ef2be4"
name: "weekly-budget-capping-with-emergency-exception-and-auto-correct"
description: "Enforces a strict weekly spending cap per expense category (fixed, negotiable, flexible) with a transparent emergency exception rule, automatically triggers predefined corrective actions if over-cap spending occurs in two consecutive weeks, and supports a structured monthly joint review for two-adult households to assess adherence, exception validity, behavioral patterns, and co-sign one concrete adjustment."
version: "0.1.3"
tags:
  - "budgeting"
  - "spending-control"
  - "emergency-rule"
  - "weekly-cycle"
  - "financial-discipline"
  - "automation"
  - "behavioral-accountability"
  - "corrective-action"
  - "budget-review"
  - "two-person-household"
  - "monthly-routine"
  - "joint-decision"
triggers:
  - "按周设置消费上限"
  - "保留应急例外规则"
  - "每周预算封顶"
  - "紧急支出豁免"
  - "预算弹性例外"
  - "连续两周超支"
  - "自动触发纠偏"
  - "双人家庭月度复盘"
  - "月度支出联合检视"
---

# weekly-budget-capping-with-emergency-exception-and-auto-correct

Enforces a strict weekly spending cap per expense category (fixed, negotiable, flexible) with a transparent emergency exception rule, automatically triggers predefined corrective actions if over-cap spending occurs in two consecutive weeks, and supports a structured monthly joint review for two-adult households to assess adherence, exception validity, behavioral patterns, and co-sign one concrete adjustment.

## Prompt

# Goal
Enforce a weekly spending limit per expense category (fixed, negotiable, flexible), allow one-time emergency overrides with documented cause and offset plan, automatically initiate corrective actions upon two consecutive weeks of over-cap spending, and support a time-boxed monthly joint review for two-adult households — all while preserving budget integrity, sustainability, and shared accountability.

# Constraints & Style
- Output only a Markdown table with columns: Category | Weekly Cap (¥) | Emergency Exception Rule | Example Trigger
- Weekly caps must be numeric, realistic, and derived from user-provided or inferred monthly totals (e.g., monthly fixed ¥12,000 → weekly cap ¥2,769, rounded down)
- Emergency Exception Rule must be concrete, behaviorally specific, and require *both*:
  • A documented cause (e.g., 'sudden medical co-pay', 'urgent appliance repair')
  • A post-hoc offset plan (e.g., 'reduce next week’s flexible spending by 2× the amount', or 'add to debt repayment in following month')
- Never invent emergency definitions; if user hasn’t specified qualifying conditions, use placeholder <EMERGENCY_CRITERIA>
- Corrective actions activate *only* after two full, sequential weeks exceed the total weekly cap; single-week overruns do not trigger.
- Corrective actions must be concrete, executable, and non-punitive — e.g., temporary category freeze, vendor renegotiation prompt, or verification step — never vague advice.
- Reuse only the user’s existing three-tiered spending classification (fixed / negotiable / flexible); do not introduce new categories or thresholds.
- All monetary values and timeframes must remain abstracted (e.g., <WEEKLY_CAP>, <CATEGORY_NAME>, <TIER>) for cross-household reusability.
- Monthly review must be executable in ≤45 minutes using only prior week’s tracked data; output format is plain-text markdown table + one bulleted mutual commitment — no explanations, summaries, or advice.
- Language: concise, neutral, second-person plural ('you both', 'your shared account', 'agree to') during review; otherwise third-person in enforcement logic.
- Prohibited: assigning blame, revisiting past exceptions without documentation, introducing new categories/caps, discussing income changes or long-term goals.
- Mandatory inclusion in review: exact weekly cap values used that month and whether each was exceeded ≥2 weeks (triggering auto-correct).
- Behavioral triggers must be phrased as observable actions (e.g., 'swiping checkout after 9 p.m.', not 'feeling stressed').
- Final commitment must be actionable, time-bound, and reversible (e.g., 'For next 30 days, disable one-click purchase on all devices').
- Do not include explanations, summaries, advice, or motivational language — only the structured table, standardized log format when applicable, and the signed commitment.
- Use Chinese language throughout; all monetary values in ¥, no currency symbols elsewhere.
- Category-specific corrective logic:
  • Fixed-tier overrun → require documented cause (e.g., sudden essential repair) AND enforce offset by reducing next week’s flexible budget by 2× the overage amount
  • Negotiable-tier overrun → require verified cause (e.g., medical co-pay, school-required urgent purchase) AND enforce offset by deferring one pre-approved negotiable item to next month
  • Flexible-tier overrun → require self-reflection journal entry confirming emotional crisis context AND enforce a 3-day no-spend challenge with pre-approved free alternatives
- Never allow cumulative or compound offsets across categories; each category’s correction must be isolated and proportional.

## Triggers

- 按周设置消费上限
- 保留应急例外规则
- 每周预算封顶
- 紧急支出豁免
- 预算弹性例外
- 连续两周超支
- 自动触发纠偏
- 双人家庭月度复盘
- 月度支出联合检视
