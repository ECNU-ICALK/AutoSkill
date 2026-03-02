---
id: "b0a6fceb-f193-4dc1-b738-5136461ed67c"
name: "Find first non-repeating character with case preservation"
description: "Create a Python function named 'first' that identifies the first character in a string which does not repeat. It performs case-insensitive counting to determine uniqueness but returns the character in its original case."
version: "0.1.0"
tags:
  - "python"
  - "string"
  - "algorithm"
  - "case-sensitivity"
  - "coding"
triggers:
  - "find first non-repeating character"
  - "first unique character in string"
  - "case insensitive count case sensitive return"
  - "function named first python"
---

# Find first non-repeating character with case preservation

Create a Python function named 'first' that identifies the first character in a string which does not repeat. It performs case-insensitive counting to determine uniqueness but returns the character in its original case.

## Prompt

# Role & Objective
You are a Python programmer tasked with creating a specific string analysis function. Write a program that defines a function named `first` which takes a string as an argument and returns the first character that is not repeated anywhere in the string.

# Operational Rules & Constraints
1. **Case-Insensitive Comparison**: When determining if a character is repeated, treat uppercase and lowercase letters as the same character (e.g., 'A' and 'a' are considered identical).
2. **Case-Sensitive Return**: The function must return the character exactly as it appears in the original input string (preserving the initial letter's case).
3. **Empty String Handling**: If the string contains all repeating characters, return an empty string `""`.
4. **Input Method**: Use `import sys` to read the input string from command line arguments.
5. **Simplification**: Keep the implementation simple and efficient, avoiding unnecessary complexity.

# Anti-Patterns
Do not return the lowercase version of the character. Do not use complex external libraries if standard loops suffice. Do not treat 'A' and 'a' as different characters when checking for repetition.

## Triggers

- find first non-repeating character
- first unique character in string
- case insensitive count case sensitive return
- function named first python
