---
id: "80b3b38d-02c7-4d6f-8a0c-1752c3971c11"
name: "Java Command-Line Argument Parsing with Flags"
description: "Parse command-line arguments in Java where flags are followed by values, ensuring the loop index is handled correctly to avoid skipping arguments."
version: "0.1.0"
tags:
  - "java"
  - "cli"
  - "parsing"
  - "arguments"
  - "main-method"
triggers:
  - "parse command line arguments java"
  - "fix argument parsing loop"
  - "program should permit arbitrary file names"
  - "java main method args parsing"
---

# Java Command-Line Argument Parsing with Flags

Parse command-line arguments in Java where flags are followed by values, ensuring the loop index is handled correctly to avoid skipping arguments.

## Prompt

# Role & Objective
Implement command-line argument parsing in Java for flags that require subsequent values (e.g., filenames).

# Operational Rules & Constraints
- Use a `for` loop to iterate through the `args` array.
- Identify specific flags (e.g., `-m`, `-p`, `-o`).
- Retrieve the value associated with a flag using `args[i + 1]`.
- **Constraint:** Do not use pre-increment (`++i`) inside the array access expression (e.g., do not use `args[++i]`).
- **Constraint:** Increment the loop index `i` explicitly *after* assigning the value (e.g., `i++;`) to ensure the next iteration skips the value argument.

# Anti-Patterns
- Avoid using `args[++i]` within the loop as it can cause arguments to be skipped or index out of bounds errors.

## Triggers

- parse command line arguments java
- fix argument parsing loop
- program should permit arbitrary file names
- java main method args parsing
