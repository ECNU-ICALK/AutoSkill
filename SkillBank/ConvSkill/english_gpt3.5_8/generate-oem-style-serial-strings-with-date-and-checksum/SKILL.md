---
id: "1ba3d986-91f3-473b-a339-843c24ee91e8"
name: "Generate OEM-style serial strings with date and checksum"
description: "Generates serial strings in the format xxxyy-OEM-NNNNNNN-zzzzz with specific date range and checksum constraints."
version: "0.1.0"
tags:
  - "serial generation"
  - "OEM format"
  - "checksum"
  - "date encoding"
  - "string generation"
triggers:
  - "generate OEM serial strings"
  - "create xxxyy-OEM-NNNNNNN-zzzzz strings"
  - "generate serials with date and checksum"
  - "create OEM format keys with divisible sum"
  - "produce serial strings with day-year format"
---

# Generate OEM-style serial strings with date and checksum

Generates serial strings in the format xxxyy-OEM-NNNNNNN-zzzzz with specific date range and checksum constraints.

## Prompt

# Role & Objective
Generate serial strings following a strict format and constraints.

# Operational Rules & Constraints
- Output format: "xxxyy-OEM-NNNNNNN-zzzzz"
- xxx: day of year (001-366)
- yy: two-digit year
- Date range: from first day of specified year to last day of that year
- OEM segment: must remain exactly "OEM"
- NNNNNNN segment: 7 digits, must start with "00"
- The sum of all digits in NNNNNNN must be divisible by 7 with no remainder
- zzzzz segment: 5 random digits
- Generate the requested quantity of strings

# Anti-Patterns
- Do not alter the "OEM" segment
- Do not use digits outside the specified ranges
- Do not generate NNNNNNN where the digit sum is not divisible by 7
- Do not include any explanatory text in the output, only the strings

## Triggers

- generate OEM serial strings
- create xxxyy-OEM-NNNNNNN-zzzzz strings
- generate serials with date and checksum
- create OEM format keys with divisible sum
- produce serial strings with day-year format
