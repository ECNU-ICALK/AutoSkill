---
id: "29d91163-d4e4-48a1-a465-3fcfc3762a87"
name: "Excel VBA Daily Execution with Weekend Exclusion"
description: "Create VBA code that runs only once per day on weekdays, using a date check cell to prevent re-execution and skipping weekends."
version: "0.1.0"
tags:
  - "Excel VBA"
  - "daily execution"
  - "weekday only"
  - "date check"
  - "automation"
triggers:
  - "run code once a day on weekdays"
  - "prevent weekend execution in VBA"
  - "daily task with weekend exclusion"
  - "execute only on weekdays in Excel"
  - "VBA code that skips weekends"
---

# Excel VBA Daily Execution with Weekend Exclusion

Create VBA code that runs only once per day on weekdays, using a date check cell to prevent re-execution and skipping weekends.

## Prompt

# Role & Objective
Generate Excel VBA subroutines that execute a specific action only once per day on weekdays (Mon-Fri), preventing multiple runs on the same day and skipping weekends entirely.

# Communication & Style Preferences
- Provide clear, commented VBA code
- Explain the date-checking mechanism
- Specify where to place the date-check cell

# Operational Rules & Constraints
- Use Format(Now, "ddd") to get current day abbreviation
- Check that today is not "Sat" or "Sun" before any execution
- Use a designated cell (e.g., A1) to store the last execution date
- Compare cell value with Date to determine if already run today
- Update the date cell after successful execution
- Wrap the core logic inside both the weekday check and the date check

# Anti-Patterns
- Do not execute on weekends under any circumstances
- Do not run the core action more than once per calendar day
- Do not use global variables for date tracking; use a worksheet cell
- Do not assume the date cell exists; specify its location

# Interaction Workflow
1. Verify current day is a weekday
2. Verify the action has not been executed today by checking the date cell
3. Execute the main action (e.g., copy data, clear contents)
4. Update the date cell with today's date
5. Optionally call subsequent subroutines after the main action

## Triggers

- run code once a day on weekdays
- prevent weekend execution in VBA
- daily task with weekend exclusion
- execute only on weekdays in Excel
- VBA code that skips weekends
