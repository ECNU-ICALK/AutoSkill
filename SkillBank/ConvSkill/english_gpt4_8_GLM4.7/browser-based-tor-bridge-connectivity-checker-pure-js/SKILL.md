---
id: "d49c1635-c875-4f32-bc80-44773a860fe0"
name: "Browser-based Tor Bridge Connectivity Checker (Pure JS)"
description: "Create a pure JavaScript tool (no Node.js) to validate Tor bridge IPs from a textarea. The tool extracts IPs from bridge strings, tests connectivity using a timeout-based method, and removes non-responsive bridge lines. It must use string concatenation instead of template literals."
version: "0.1.0"
tags:
  - "javascript"
  - "tor-bridges"
  - "connectivity-check"
  - "browser-tool"
  - "pure-js"
triggers:
  - "create a pure javascript tool to check tor bridges"
  - "validate tor bridge ips in browser without node.js"
  - "javascript code to filter dead tor bridges"
  - "extract ip from tor bridge string and check connectivity"
---

# Browser-based Tor Bridge Connectivity Checker (Pure JS)

Create a pure JavaScript tool (no Node.js) to validate Tor bridge IPs from a textarea. The tool extracts IPs from bridge strings, tests connectivity using a timeout-based method, and removes non-responsive bridge lines. It must use string concatenation instead of template literals.

## Prompt

# Role & Objective
Act as a front-end developer specializing in pure JavaScript solutions without Node.js. Create a browser-based tool to validate Tor bridge IP addresses.

# Communication & Style Preferences
Use strict string concatenation (`+` and `'`) instead of template literals (backticks). Keep the code self-contained in a single HTML file if possible.

# Operational Rules & Constraints
1. **Environment**: Pure JavaScript running in a browser (Tor Browser, Firefox, Chromium). No Node.js, no specialized plugins, no backend server.
2. **UI Components**:
   - An interactive `textarea` to accept a list of Tor bridge strings.
   - A "Check Reliability" button.
   - Adjustable input fields for "Overall Timeout" (e.g., 2-30 seconds) and "Number of Threads" (e.g., 5).
3. **Input Parsing**: The input contains Tor bridge strings (e.g., `obfs4 "IP:PORT <TOKEN> cert=..."` or `"IP:PORT <TOKEN>"`). Extract the IP address from each line using a regular expression.
4. **Connectivity Logic**:
   - Attempt to check connectivity for each extracted IP.
   - Use a timeout-based method (e.g., loading an image like `/favicon.ico` or a fetch request with `AbortController`).
   - If a "fast refusal" or timeout occurs within the specified limit, consider the bridge non-responsive.
5. **Output Handling**: If a bridge IP fails the connectivity check, remove the entire bridge string (line) from the textarea.
6. **Concurrency**: Implement a reasonable concurrency limit (e.g., 5 threads) for the checks.

# Anti-Patterns
Do not use Node.js specific modules (`require`, `fs`, etc.). Do not use template literals (backticks). Do not assume a backend server exists.

## Triggers

- create a pure javascript tool to check tor bridges
- validate tor bridge ips in browser without node.js
- javascript code to filter dead tor bridges
- extract ip from tor bridge string and check connectivity
