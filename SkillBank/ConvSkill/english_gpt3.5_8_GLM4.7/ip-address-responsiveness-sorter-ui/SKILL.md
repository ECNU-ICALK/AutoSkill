---
id: "cd221762-517e-4ab2-aa60-b48f8bcc9c95"
name: "IP Address Responsiveness Sorter UI"
description: "Create a web-based UI to filter IP addresses based on HTTP/HTTPS connectivity using a sequential queue and adjustable timeout."
version: "0.1.0"
tags:
  - "ip-sorter"
  - "javascript"
  - "web-ui"
  - "network-check"
  - "timeout-filter"
triggers:
  - "create ip sorter ui"
  - "sort ips by http response"
  - "check ip connectivity sequentially"
  - "filter active ips with timeout"
  - "web based ip checker"
---

# IP Address Responsiveness Sorter UI

Create a web-based UI to filter IP addresses based on HTTP/HTTPS connectivity using a sequential queue and adjustable timeout.

## Prompt

# Role & Objective
Act as a Front-End Developer. Create a web-based UI using HTML, CSS, and JavaScript to sort a list of IP addresses based on their responsiveness.

# Operational Rules & Constraints
1. **Connectivity Check**: For each IP in the list, attempt to connect via HTTP first, then attempt a secure version via HTTPS.
2. **Filtering Logic**: Remove all IPs from the list that reach a timeout. Keep all IPs that return any HTTP or HTTPS response (response content or status code is irrelevant; only the existence of a response matters).
3. **Timeout Configuration**: Set an adjustable default timeout of 5 seconds for each IP check.
4. **Queue Management**: Process all IPs sequentially (one by one) to avoid overflowing the stack or overwhelming the system.
5. **UI Components**: Include an input field for the IP list, an input for the timeout value (default 5s), a button to start the process, and a container to display the sorted/filtered results.

# Anti-Patterns
- Do not perform packet inspection or analyze ACK flags.
- Do not process IPs in parallel; strictly use a sequential queue.
- Do not filter based on response content or specific status codes.

## Triggers

- create ip sorter ui
- sort ips by http response
- check ip connectivity sequentially
- filter active ips with timeout
- web based ip checker
