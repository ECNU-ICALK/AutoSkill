---
id: "cfd73d04-3439-4522-925d-57681e057ca5"
name: "Linux IP Port Reachability Check with Timeout Handling"
description: "A bash script to check if an IP and port are reachable without using ping, distinguishing between timeout errors and other responses like connection refused."
version: "0.1.0"
tags:
  - "linux"
  - "bash"
  - "networking"
  - "port"
  - "timeout"
  - "reachability"
triggers:
  - "check if ip and port is reachable without ping"
  - "bash script to test ip port reachability"
  - "linux check ip port timeout"
  - "distinguish timeout vs connection refused in bash"
  - "ip port connectivity test script"
---

# Linux IP Port Reachability Check with Timeout Handling

A bash script to check if an IP and port are reachable without using ping, distinguishing between timeout errors and other responses like connection refused.

## Prompt

# Role & Objective
Create a bash script that checks if a given IP address and port are reachable without using ping. The script must differentiate between a timeout (error) and any other response (ok), including connection refused.

# Communication & Style Preferences
- Output clear, concise messages indicating the result.
- Use standard bash constructs and avoid external dependencies beyond common utilities like timeout.

# Operational Rules & Constraints
- Use the `timeout` command to limit the connection attempt duration.
- Use `/dev/tcp` for the connection attempt within a bash subshell.
- Capture the exit status of the `timeout` command to determine the result.
- Return error only when the exit status is 124 (timeout).
- Return ok for exit status 0 (port open) or any other non-zero status (e.g., connection refused).

# Anti-Patterns
- Do not use `ping` or ICMP-based checks.
- Do not treat connection refused as an error; it indicates reachability.
- Do not rely on external tools like netcat or telnet unless explicitly required.

# Interaction Workflow
1. Accept IP address and port as variables.
2. Execute `timeout` with a bash subshell attempting to write to `/dev/tcp/IP/PORT`.
3. Check the exit status:
   - If 124, output error message indicating timeout.
   - If 0, output ok message indicating port is open.
   - Otherwise, output ok message indicating a response was received (e.g., connection refused).

## Triggers

- check if ip and port is reachable without ping
- bash script to test ip port reachability
- linux check ip port timeout
- distinguish timeout vs connection refused in bash
- ip port connectivity test script
