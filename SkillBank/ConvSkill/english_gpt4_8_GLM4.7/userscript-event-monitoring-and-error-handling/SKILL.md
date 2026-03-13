---
id: "a38ddcee-2398-4e1b-afe3-050471c54bb4"
name: "Userscript Event Monitoring and Error Handling"
description: "A reusable pattern for monitoring page events (AJAX, DOM, visibility) with per-event-type throttling, and safely extracting/parsing error messages using XPath with conditional logic."
version: "0.1.0"
tags:
  - "userscript"
  - "event-monitoring"
  - "error-handling"
  - "xpath"
  - "throttling"
triggers:
  - "monitor page events userscript"
  - "throttle event logging per type"
  - "extract error message xpath safely"
  - "handle error messages with conditional logic"
  - "userscript event listener"
---

# Userscript Event Monitoring and Error Handling

A reusable pattern for monitoring page events (AJAX, DOM, visibility) with per-event-type throttling, and safely extracting/parsing error messages using XPath with conditional logic.

## Prompt

# Role & Objective
Act as a Userscript Developer. Create a script to monitor page events and handle error messages safely.

# Operational Rules & Constraints
1. **Event Monitoring**: Monitor XMLHttpRequest (loadstart, progress, load, error, abort), DOM mutations (MutationObserver), page visibility (visibilitychange), and page unload (beforeunload).
2. **Throttling**: Implement per-event-type throttling. Use a dictionary/object to track the last log time for each event type separately. Do not use a global timestamp that blocks all events.
3. **Error Extraction**: Create a function to extract text content using XPath. Wrap `document.evaluate` in a try-catch block. Return `null` if the node does not exist or an error occurs.
4. **Error Matching**: Use `String.prototype.includes()` to check if the error message contains specific text fragments. Implement conditional logic (if/else) to perform different actions based on the matched text.
5. **Variable Safety**: When incrementing numeric variables (e.g., counters, retries), explicitly cast them to `Number()` before addition to prevent string concatenation.

# Anti-Patterns
- Do not use a global throttle variable that blocks all event types.
- Do not assume XPath nodes always exist; always handle missing nodes gracefully.
- Do not perform arithmetic on variables without ensuring they are numbers.

## Triggers

- monitor page events userscript
- throttle event logging per type
- extract error message xpath safely
- handle error messages with conditional logic
- userscript event listener
