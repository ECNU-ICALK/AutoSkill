---
id: "5a563c4c-8bec-448d-bbef-d8a6fc590645"
name: "LFSR encrypt decrypt with console table"
description: "Encrypt and decrypt a message using a Linear Feedback Shift Register (LFSR) with user-defined parameters, display a clock/flip-flop table, and show encrypted binary values converted to string."
version: "0.1.0"
tags:
  - "LFSR"
  - "encryption"
  - "decryption"
  - "console table"
  - "binary polynomial"
triggers:
  - "encrypt and decrypt a message using LFSR"
  - "show LFSR clock and flip-flop table"
  - "LFSR encryption decryption with console output"
  - "binary polynomial LFSR example"
  - "LFSR encrypt decrypt with table"
---

# LFSR encrypt decrypt with console table

Encrypt and decrypt a message using a Linear Feedback Shift Register (LFSR) with user-defined parameters, display a clock/flip-flop table, and show encrypted binary values converted to string.

## Prompt

# Role & Objective
Implement a Python program that encrypts and decrypts a message using a Linear Feedback Shift Register (LFSR). The program must accept user inputs for the message, LFSR degree m (max 9), polynomial p(x) in binary form, and initial vector in binary. It must display a console table showing clock cycles and flip-flop states, then show encrypted binary values converted to string, and finally decrypt and output the original message.

# Communication & Style Preferences
- Use clear prompts for user inputs.
- Print the LFSR sequence, encrypted binary values, encrypted string, and decrypted message.
- Display a table of clock cycles and flip-flop states in the console.

# Operational Rules & Constraints
- m value is not fixed; maximum allowed is 9.
- Polynomial p(x) must be provided by the user in binary form (e.g., 1011 for x^3+x+1).
- Initial vector must be provided as a binary string (e.g., 1101).
- Generate the LFSR sequence with length equal to the message length to avoid index errors.
- Use XOR operation for encryption: encrypted_ascii = char_ascii ^ lfsr_sequence[i].
- Use XOR operation for decryption: decrypted_ascii = encrypted_ascii ^ lfsr_sequence[i].
- Convert encrypted binary values to string for display.

# Anti-Patterns
- Do not hardcode the message, m, polynomial, or initial vector.
- Do not assume fixed LFSR sequence length; match it to message length.
- Do not omit the clock/flip-flop table display.

# Interaction Workflow
1. Prompt user to enter the message.
2. Prompt user to enter m (max 9).
3. Prompt user to enter polynomial p(x) in binary.
4. Prompt user to enter initial vector in binary.
5. Generate LFSR sequence.
6. Display table of clock cycles and flip-flop states.
7. Encrypt the message and display encrypted binary values and string.
8. Decrypt the ciphered text and output the result.

## Triggers

- encrypt and decrypt a message using LFSR
- show LFSR clock and flip-flop table
- LFSR encryption decryption with console output
- binary polynomial LFSR example
- LFSR encrypt decrypt with table
