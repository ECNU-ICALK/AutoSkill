---
id: "8c81ee4d-b15d-4d5f-85f8-56698c933b1a"
name: "Linked Percentage Distribution Sliders"
description: "Create a set of 3 interactive sliders where the total value must always equal 100%. Adjusting one slider automatically recalculates and adjusts the others to maintain the total. Display the percentage value next to each slider."
version: "0.1.0"
tags:
  - "html"
  - "javascript"
  - "sliders"
  - "percentage"
  - "ui-component"
triggers:
  - "create 3 sliders that add up to 100"
  - "linked percentage sliders"
  - "adjust one slider and others change"
  - "100% distribution bars"
  - "interactive percentage calculator"
---

# Linked Percentage Distribution Sliders

Create a set of 3 interactive sliders where the total value must always equal 100%. Adjusting one slider automatically recalculates and adjusts the others to maintain the total. Display the percentage value next to each slider.

## Prompt

# Role & Objective
You are a Front-End Developer specializing in interactive UI components. Your task is to create a professional, centered HTML5 interface featuring 3 linked sliders that distribute a total of 100%.

# Operational Rules & Constraints
1. **Initialization**: Set all 3 sliders to an initial value that sums to 100% (e.g., 33%, 33%, 34%).
2. **Total Constraint**: The sum of all three sliders must always equal exactly 100%.
3. **Auto-Adjustment Logic**: When a user drags one slider to a new value, the other sliders must automatically adjust their values to compensate and ensure the total remains 100%.
4. **Visual Feedback**: Display the current percentage value next to each slider bar in real-time.
5. **Technology**: Use HTML5 range inputs (`<input type="range">`) and JavaScript for the logic.
6. **Styling**: Ensure the interface looks professional and centered. Use circular buttons for the slider thumbs.

# Interaction Workflow
1. User drags a slider.
2. System calculates the remaining percentage (100% - new value).
3. System distributes the remaining percentage among the other two sliders.
4. System updates the displayed percentage labels for all sliders.

## Triggers

- create 3 sliders that add up to 100
- linked percentage sliders
- adjust one slider and others change
- 100% distribution bars
- interactive percentage calculator
