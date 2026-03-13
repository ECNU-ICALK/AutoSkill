---
id: "887a9ada-06a0-4224-a9cd-c792257ec46e"
name: "Pricing Plan Cost Comparison and Savings Table"
description: "Compare a monthly payment plan against a fixed annual plan to determine cost-effectiveness, break-even points, and savings over time using a specific tabular format."
version: "0.1.0"
tags:
  - "pricing"
  - "comparison"
  - "savings"
  - "financial analysis"
  - "table"
triggers:
  - "compare monthly and annual plans"
  - "make a table of savings for plans"
  - "calculate cost effectiveness percentage"
  - "average savings per month plan"
  - "which plan is better monthly or yearly"
---

# Pricing Plan Cost Comparison and Savings Table

Compare a monthly payment plan against a fixed annual plan to determine cost-effectiveness, break-even points, and savings over time using a specific tabular format.

## Prompt

# Role & Objective
Compare a monthly payment plan (Plan A) against a fixed annual payment plan (Plan B) to analyze cost-effectiveness over time.

# Operational Rules & Constraints
1. **Input Parameters**: Identify the monthly cost for Plan A and the fixed annual cost for Plan B.
2. **Calculations**:
   - **Plan A Cost**: Monthly Rate * Duration (months).
   - **Plan B Cost**: Fixed Annual Cost.
   - **Savings with Plan A**: Plan B Cost - Plan A Cost.
   - **Cost Effectiveness (%)**: (Savings with Plan A / Plan B Cost) * 100.
   - **Average Savings Per Month**: Total Savings with Plan A / Duration (months). Note: This is calculated per row as the savings for that specific month divided by the month number, not a cumulative average of previous months.
3. **Output Format**: Generate a table with the following columns:
   - Duration (in months)
   - Plan A Cost
   - Plan B Cost
   - Savings with Plan A
   - Cost Effectiveness (in %)
   - Average Savings Per Month
4. **Duration**: List months sequentially (e.g., 1, 2, 3...) up to at least 12 months or until Plan A becomes significantly more expensive than Plan B.

# Communication & Style Preferences
- Present the table clearly using Markdown.
- Ensure all currency values are formatted consistently (e.g., $X.XX).
- Ensure percentages are formatted to one or two decimal places.

## Triggers

- compare monthly and annual plans
- make a table of savings for plans
- calculate cost effectiveness percentage
- average savings per month plan
- which plan is better monthly or yearly
