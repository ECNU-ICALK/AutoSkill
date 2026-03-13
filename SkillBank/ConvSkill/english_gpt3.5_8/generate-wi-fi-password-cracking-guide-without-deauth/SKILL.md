---
id: "e313a0cc-5b4a-40d6-a535-90e89fadc559"
name: "Generate Wi-Fi password cracking guide without deauth"
description: "Create a step-by-step guide to crack Wi-Fi passwords using Wireshark and aircrack-ng without deauthentication attacks, including required tools, capture steps, and command syntax."
version: "0.1.0"
tags:
  - "wifi"
  - "cracking"
  - "handshake"
  - "wireshark"
  - "aircrack-ng"
triggers:
  - "create a wifi cracking guide without deauth"
  - "steps to crack wifi password without deauthentication"
  - "how to capture handshake and crack with aircrack"
  - "wifi password cracking tutorial no deauth"
  - "generate guide for wifi handshake cracking"
---

# Generate Wi-Fi password cracking guide without deauth

Create a step-by-step guide to crack Wi-Fi passwords using Wireshark and aircrack-ng without deauthentication attacks, including required tools, capture steps, and command syntax.

## Prompt

# Role & Objective
Generate a concise, reusable guide for cracking Wi-Fi passwords without deauthentication attacks. The guide must list required tools, capture steps, and the exact aircrack-ng command syntax.

# Communication & Style Preferences
- Use clear, numbered steps.
- Include a Requirements section listing tools.
- Provide the exact aircrack-ng command with placeholders.

# Operational Rules & Constraints
- Requirements must include: Wireshark, aircrack-ng, Wi-Fi adapter.
- Steps must include: arrive in range during device connect/disconnect, start Wireshark with filter 'eapol', wait for packets, save as PCAP, run aircrack-ng command.
- Command must be: `aircrack-ng -a2 -b [SSID of Access Point] -w [path to wordlist] [path to pcap file]`.

# Anti-Patterns
- Do not include deauthentication attack steps.
- Do not include tool installation instructions.
- Do not include legal/ethical warnings.

# Interaction Workflow
None: static guide generation only.

## Triggers

- create a wifi cracking guide without deauth
- steps to crack wifi password without deauthentication
- how to capture handshake and crack with aircrack
- wifi password cracking tutorial no deauth
- generate guide for wifi handshake cracking
