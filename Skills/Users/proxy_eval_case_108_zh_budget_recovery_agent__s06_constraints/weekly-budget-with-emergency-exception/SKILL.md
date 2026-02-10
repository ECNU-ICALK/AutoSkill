---
id: "5386aaf2-81f6-48e2-a634-14b271a76d97"
name: "weekly-budget-with-emergency-exception-and-automated-correction"
description: "为双人家庭日常消费设置按周执行的金额上限，内置可验证的三级应急例外规则，并在检测到连续两周超支时自动触发无需决策的校准动作；全程依托零工具方法（如现金信封、语音备忘、手写笔记），支持结构化月度复盘，兼顾预算纪律性、现实灵活性与行为可持续性。"
version: "0.1.3"
tags:
  - "budgeting"
  - "spending-control"
  - "emergency-rule"
  - "weekly-cycle"
  - "household-finance"
  - "review"
  - "collaboration"
  - "behavioral-design"
  - "exception-handling"
  - "auto-correction"
triggers:
  - "按周设置消费上限并支持应急例外"
  - "连续两周超支自动触发校准"
  - "家庭周预算带应急豁免与自动纠偏"
  - "双人家庭月度复盘"
---

# weekly-budget-with-emergency-exception-and-automated-correction

为双人家庭日常消费设置按周执行的金额上限，内置可验证的三级应急例外规则，并在检测到连续两周超支时自动触发无需决策的校准动作；全程依托零工具方法（如现金信封、语音备忘、手写笔记），支持结构化月度复盘，兼顾预算纪律性、现实灵活性与行为可持续性。

## Prompt

# Goal
Enforce a weekly spending cap across all household consumption categories for two-adult households, automatically permit pre-defined emergency exceptions without manual override or external tools, and trigger a calibrated corrective protocol upon detection of two consecutive weeks of overspending. Support a structured, time-boxed monthly review to jointly analyze spending patterns, adjust budget rules, and commit to one high-leverage action — using only universally accessible methods (e.g., cash envelopes, voice notes, handwritten notes, shared messaging).

# Constraints & Style
• Weekly cap is set as a single numeric value per week (e.g., ¥1,200/week), applied cumulatively to all tracked spending — excluding only transactions that meet *all* criteria of a valid emergency exception.
• Emergency exceptions are strictly tiered: L1 (urgent, ≤30% of week’s cap) → voice note to partner + photo receipt within 24h; L2 (planned, ≤60%) → 2-hour group chat consensus; L3 (major life event) → scheduled family meeting + signed agreement. Only three types qualify: (1) urgent medical out-of-pocket costs, (2) essential home/vehicle repairs that impair safety or basic function, (3) verified sudden income loss (e.g., pay stub showing missed salary).
• Each emergency transaction must include: (a) brief justification in plain language, (b) date, and (c) verifiable evidence reference (e.g., 'receipt #ABC123', 'bank statement page 4', 'HR email screenshot').
• Overspending is defined strictly as total tracked outflow exceeding the weekly limit, *excluding* only expenses explicitly tagged and validated under an active emergency exception.
• Consecutive weeks are calendar weeks (Mon–Sun); the two-week overspend counter resets only after *two full weeks* with no overspend.
• Upon detecting two consecutive overspent weeks (neither fully covered by a valid emergency exception), immediately trigger all five actions:
  • Freeze non-essential payments to ¥300/day;
  • Reduce next week’s base limit by 15% (applied before any type-based adjustments);
  • Split the new cap into three labeled cash envelopes (food/transport/flex);
  • Conduct a 3-question anonymous reflection on Wednesday;
  • Auto-generate an 'Overspend Insight Card' listing: (a) category with largest cumulative overage, (b) one high-frequency micro-spend pattern, and (c) one actionable substitution.
• All non-emergency spending — including groceries, transport, dining, subscriptions, and shopping — counts toward the weekly cap.
• Monthly review is strictly time-boxed to ≤45 minutes; if exceeded, unfinished items move to next month’s first week ‘Quick Consensus’ slot.
• Monthly review output must be a single A4-sized document (handwritten or shared digital) with three columns:『Discovery』｜『Decision』｜『Action』 — no PPTs, spreadsheets, or long-form reports.
• All conclusions must be verifiable: deviation attributions require bill/app evidence; rule adjustments specify effective week and exact values; high-leverage actions name owner and deadline.
• Prohibit person-based attribution (e.g., 'you always spend'); only analyze behavioral patterns and system gaps (e.g., 'no cooling-off period for food delivery', 'auto-renewal alerts disabled').
• Use neutral, collaborative language: 'We observed', 'The system prompted', 'Next time we could try' — never moral framing ('should', 'discipline', 'indulgence').
• Output must be plain-text, copy-paste ready — no tables, markdown formatting, code blocks, or references to Excel/PDF/tools.
• Use only universally accessible methods: shared messaging (e.g., WhatsApp/WeChat), cash envelopes, voice notes, handwritten notes, and verbal rituals.
• All rules must be self-contained — no external scripts, apps, or calculations required.
• Language must be warm but precise; avoid judgmental terms (e.g., say “adjustment” not “penalty”, “calibration” not “punishment”).
• Keep each rule under 25 words; use bullet points only when essential for scannability.
• Do not suggest budgeting tools or apps unless explicitly requested; output only rule logic, validation criteria, corrective outputs, and review deliverables.
• Output all responses in plain Markdown (no code blocks, no JSON), fully localized to user’s language.

## Triggers

- 按周设置消费上限并支持应急例外
- 连续两周超支自动触发校准
- 家庭周预算带应急豁免与自动纠偏
- 双人家庭月度复盘
