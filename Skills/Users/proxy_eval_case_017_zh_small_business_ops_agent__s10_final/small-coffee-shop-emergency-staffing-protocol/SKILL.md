---
id: "fcb2bc8f-bd71-4552-b4f5-7c51dd8343bf"
name: "small-coffee-shop-emergency-staffing-protocol"
description: "A reusable, tiered, rule-based emergency staffing protocol for small coffee shops (2–3 staff) that activates upon unexpected staff absence, preserving core operations, safety, quality, and customer experience without adding personnel or compromising observable service guarantees."
version: "0.1.2"
tags:
  - "staffing"
  - "contingency"
  - "coffee-shop"
  - "operations"
  - "small-business"
  - "emergency-response"
triggers:
  - "突发缺人"
  - "应急排班"
  - "员工临时请假"
  - "人手不足应对"
  - "staff shortage protocol"
---

# small-coffee-shop-emergency-staffing-protocol

A reusable, tiered, rule-based emergency staffing protocol for small coffee shops (2–3 staff) that activates upon unexpected staff absence, preserving core operations, safety, quality, and customer experience without adding personnel or compromising observable service guarantees.

## Prompt

# Goal
Generate two distinct, de-identified, executable deliverables for a small independent coffee shop (2–3 total staff) when one or more team members are unexpectedly absent: (1) a concise **Store Manager Dashboard**, showing only the active response level, immediate status, hard service guarantee, and mandatory follow-up; and (2) a clear **Staff Execution Checklist**, listing *only* physical, observable, time-bound tasks the on-site staff must perform in sequence — no explanations, rationale, or policy context.

# Constraints & Style
• Strictly separate outputs: Manager Dashboard (for oversight/decision) and Staff Checklist (for muscle-memory execution). Never merge, cross-reference, or embed one inside the other.
• Use only three defined response levels: 🟢 Level 1 (weekday, 1 staff absent), 🟡 Level 2 (weekend, 1 staff absent), 🔴 Level 3 (any day, ≥2 staff absent OR only 1 staff present).
• For each level, include *exactly*: 
  - Trigger condition (e.g., "Weekday, 1 staff absent <2h before shift")
  - Manager Dashboard: 3 bullet points max — (i) status label, (ii) hard service guarantee (e.g., "≤3:30 min espresso wait"), (iii) mandatory post-event action (e.g., "Log root cause in blue/green log")
  - Staff Checklist: 4–5 numbered, imperative, present-tense steps — only what to *do*, *where*, and *by when* (e.g., "Close hand-drip station NOW", "Place 'Smart Pickup' sign at counter by 07:35")
• Must be triggered *only* by unplanned absence (e.g., illness, transport failure) — not scheduled time off.
• Applies *only* to the current day’s pre-set schedule — do not override or reschedule future days.
• Prioritize non-negotiable hygiene & safety actions:磨豆机刀盘拆洗, steam wand descaling, milk temperature logging, and waste disposal must remain assigned — never omitted or deferred.
• Never assign overlapping high-cognitive-load tasks to one person (e.g., managing live orders + calibrating espresso machine + handling cash reconciliation simultaneously).
• All role swaps must preserve skill alignment: barista with strong espresso skills handles front-line brewing; person with higher emotional bandwidth handles guest-facing moments during peak.
• No markdown tables, no emojis in Staff Checklist, no jargon (e.g., say "cold brew bottles" not "pre-brewed nitrogen-infused cold extraction units").
• All content must be de-identified: omit shop name, location, staff names, specific bean names, exact cup counts, or proprietary tools.
• Output format: Two clearly labeled sections — "### Store Manager Dashboard" and "### Staff Execution Checklist" — with no other headings, commentary, or frontmatter.
• No generic advice (e.g., 'communicate well') — only concrete, observable behaviors.
• Enforce strict separation: weekday actions must not appear in weekend tier, and vice versa.
• Prohibit all explanatory or apologetic language to customers; require only positive, on-brand framing (e.g., 'upgrading your pickup flow', not 'we’re short-staffed').
• Include exactly one immutable red-line rule per tier (e.g., 'If espresso extraction exceeds 28s → void cup + log cause', 'If milk expires >48h → discard + mark red label').
• Must be fully actionable in ≤3 minutes by a single staff member; no training, tools, or external input required.
• Replace vague language: 'optimize' → 'close hand-drip station', 'improve' → 'switch to pre-brewed cold brew only'.
• Use placeholders: <CURRENT_WEEKDAY>, <ABSENT_STAFF_ROLE>, <STAFF_A_SKILL>, <STAFF_B_SKILL>, <OWNER_AVAILABILITY>.

# Workflow
1. Identify the scenario from user input: extract day type (weekday/weekend) and number of missing staff.
2. Map to the correct response level using the fixed logic: Level 1 = weekday + 1 missing; Level 2 = weekend + 1 missing; Level 3 = any day + ≥2 missing OR only 1 staff present.
3. Populate both deliverables *only* with the pre-defined, non-negotiable actions and guarantees for that level — no improvisation, no additions, no omissions.
4. Validate: Ensure Staff Checklist contains zero explanatory text, zero conditional logic (e.g., no "if… then…"), and zero references to manager duties.

## Triggers

- 突发缺人
- 应急排班
- 员工临时请假
- 人手不足应对
- staff shortage protocol
