---
id: "c1fd1ba6-8a15-4919-8455-0e4f81257190"
name: "weekly-budget-overspending-auto-correct"
description: "Automatically triggers corrective actions when a household budget exceeds weekly limits for two consecutive weeks, ensuring sustained budget discipline through immediate automated responses."
version: "0.1.0"
tags:
  - "budget"
  - "finance"
  - "automation"
  - "overspending"
  - "corrective"
  - "household"
triggers:
  - "连续两周超支自动纠偏"
  - "budget overspending consecutive weeks"
  - "two weeks in a row over budget"
  - "automatic budget correction trigger"
---

# weekly-budget-overspending-auto-correct

Automatically triggers corrective actions when a household budget exceeds weekly limits for two consecutive weeks, ensuring sustained budget discipline through immediate automated responses.

## Prompt

# Goal
Implement an automated system that detects two consecutive weeks of budget overspending and executes predefined corrective actions to restore financial discipline without manual intervention.

# Constraints & Style
- Must trigger exactly after two consecutive weeks of overspending (not sooner or later)
- Corrective actions must be automatic and immediate upon the second week's detection
- Actions should include: budget reallocation, spending freeze warnings, automatic fund transfers, and escalation to primary budget manager
- Must preserve emergency exception rules (medical, vehicle repair, unemployment) as non-triggering events
- Should apply to all flexible spending categories and negotiable expenses
- Cannot override fixed mandatory payments
- Must log all triggers and corrective actions for audit purposes
- Should provide clear notification to all budget stakeholders

# Workflow
1. Monitor weekly spending data against predefined limits for fixed, negotiable, and flexible categories
2. When Week 1 overspending detected: flag for monitoring but take no action
3. When Week 2 consecutive overspending confirmed: immediately execute corrective sequence
4. Automatic corrective actions: freeze 30% of flexible budget, transfer funds from savings to cover gap, send alerts to all household members
5. Document trigger conditions, amounts overspent, and actions taken
6. Generate weekly compliance report showing trigger history and corrections applied

## Triggers

- 连续两周超支自动纠偏
- budget overspending consecutive weeks
- two weeks in a row over budget
- automatic budget correction trigger
