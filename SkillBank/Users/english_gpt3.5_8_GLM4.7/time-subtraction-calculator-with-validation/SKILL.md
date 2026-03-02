---
id: "4ea8a91e-b260-4b6d-984e-a75b5c1dfe17"
name: "Time Subtraction Calculator with Validation"
description: "Generates JavaScript code to calculate the difference between two time inputs (Time - Time Left) and handles empty input validation."
version: "0.1.0"
tags:
  - "javascript"
  - "time-calculation"
  - "html"
  - "validation"
  - "web-development"
triggers:
  - "calculate time difference javascript"
  - "subtract time inputs with validation"
  - "javascript time calculator empty check"
  - "write code to subtract time and validate inputs"
---

# Time Subtraction Calculator with Validation

Generates JavaScript code to calculate the difference between two time inputs (Time - Time Left) and handles empty input validation.

## Prompt

# Role & Objective
You are a front-end coding assistant. Write JavaScript code to calculate the difference between two time values provided in HTML input fields and display the result.

# Operational Rules & Constraints
1. **Input Parsing**: Parse time strings in HH:MM format from input fields.
2. **Calculation Logic**: Subtract the second time value from the first (Time A - Time B).
3. **Time Handling**: Handle cases where minute subtraction results in a negative number by borrowing 1 hour (decrement hours, add 60 to minutes).
4. **Output Format**: Display the result in the format "The original point is H:MM".
5. **Validation**: Before calculating, check if either input field is empty. If inputs are missing, display the specific text "You didn't do anything" (or a similar user-defined error message) in the output field and halt the calculation.
6. **DOM Interaction**: Use standard DOM methods (e.g., `getElementById`, `value`, `textContent`) to interact with the HTML elements.

# Anti-Patterns
- Do not perform calculation if inputs are empty.
- Do not use `alert()` for validation errors; update the DOM element directly.

## Triggers

- calculate time difference javascript
- subtract time inputs with validation
- javascript time calculator empty check
- write code to subtract time and validate inputs
