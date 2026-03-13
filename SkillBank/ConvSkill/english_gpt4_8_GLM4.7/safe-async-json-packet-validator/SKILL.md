---
id: "f8fa70b5-84d0-4e63-b135-ebf1e8913e59"
name: "Safe Async JSON Packet Validator"
description: "Validates if a data packet is valid JSON asynchronously without logging errors to the console."
version: "0.1.0"
tags:
  - "javascript"
  - "json"
  - "validation"
  - "async"
  - "error-handling"
triggers:
  - "validate json packet"
  - "check if json without errors"
  - "safe json parse"
  - "async json validation"
  - "prevent json parse error spam"
---

# Safe Async JSON Packet Validator

Validates if a data packet is valid JSON asynchronously without logging errors to the console.

## Prompt

# Role & Objective
Act as a JSON validation utility. Create a function to check if a provided data packet is valid JSON.

# Operational Rules & Constraints
1. The function must be asynchronous (async/await) as requested.
2. Do not log errors to the console (e.g., no console.log in catch blocks) to prevent spamming.
3. Return an object containing the parsed data (if valid) and a boolean flag indicating validity.
4. Handle parsing errors gracefully by returning the validity flag as false and data as null.

# Output Format
Provide a JavaScript function that accepts data and returns a promise resolving to an object like `{ isValid: boolean, parsedData: any | null }`.

## Triggers

- validate json packet
- check if json without errors
- safe json parse
- async json validation
- prevent json parse error spam
