---
id: "6bb627f7-15d6-4190-9979-31f76cffc421"
name: "wedding-budget-tracking-plan"
description: "A reusable skill for generating a wedding budget tracking plan that enforces a hard cap (e.g., ¥300,000), maps all major expense categories to concrete payment deadlines aligned with vendor milestones, and flags critical 'pay-or-lose' contractual nodes."
version: "0.1.0"
tags:
  - "budget"
  - "payment"
  - "wedding"
  - "timeline"
  - "vendor"
triggers:
  - "track wedding payments"
  - "budget deadline plan"
  - "wedding payment schedule"
  - "vendor payment timeline"
  - "¥300k wedding budget"
---

# wedding-budget-tracking-plan

A reusable skill for generating a wedding budget tracking plan that enforces a hard cap (e.g., ¥300,000), maps all major expense categories to concrete payment deadlines aligned with vendor milestones, and flags critical 'pay-or-lose' contractual nodes.

## Prompt

# Goal
Generate a wedding budget tracking plan for a 120-person wedding with a strict total cap of ¥300,000. The plan must map each major vendor category (venue, catering, photography/videography, stationery, attire, decor, transport, officiant, contingency) to its typical budget share, define exact payment deadlines tied to contractual milestones (e.g., '50% venue deposit due within 7 days of contract signing'), and highlight non-negotiable 'pay-or-lose' dates where failure triggers cancellation or penalty.

# Constraints & Style
- Output only in Markdown; no explanations, no assistant commentary.
- Use ¥ symbol and integers only (no decimals or 'approx').
- All deadlines must be expressed as relative days before wedding day (e.g., 'D-98', 'D-65', 'D-30') — never calendar dates or vague terms like 'early month'.
- For each category: list exactly (1) budget allocation %, (2) absolute ¥ amount (calculated from ¥300,000 cap), (3) required payment schedule (with amounts and D-X deadlines), (4) one-sentence 'why this deadline matters' (e.g., 'Venue requires non-refundable deposit to hold date').
- Exclude any line item exceeding the ¥300,000 total — do not add 'miscellaneous' or 'overrun buffer' as separate line items; treat contingency as an explicit line (min. 10%).
- Do not include vendor selection advice, negotiation tips, or quality guidance — only financial timing and enforcement logic.
- Never invent payment terms; if standard industry practice is ambiguous, omit that category rather than assume.

# Workflow
1. Calculate fixed allocations: venue (35%), catering (25%), photography/videography (15%), attire (10%), stationery (3%), decor (5%), transport (2%), officiant (1%), contingency (4%).
2. For each category, assign payment milestones strictly based on widely documented vendor norms for mid-size weddings (e.g., venue: 50% D-98, 50% D-30; catering: 30% D-90, 40% D-65, 30% D-15).
3. Validate sum of all allocations = ¥300,000; adjust contingency last to absorb rounding.
4. Output table with columns: Category | % | ¥ Amount | Payment Schedule | Why This Deadline Matters.

## Triggers

- track wedding payments
- budget deadline plan
- wedding payment schedule
- vendor payment timeline
- ¥300k wedding budget
