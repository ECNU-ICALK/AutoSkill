---
id: "8074b0dd-99cb-484d-a15a-beebb92e6109"
name: "Generate customizable 'N bottles' song script in Python"
description: "Creates a Python script that prints the 'N bottles of beverage on the wall' song with CLI options for start number, word output, and custom beverage, handling singular/plural correctly."
version: "0.1.0"
tags:
  - "python"
  - "script"
  - "cli"
  - "song"
  - "customizable"
triggers:
  - "create a python script for n bottles song"
  - "generate bottles of beer on the wall script with options"
  - "python script for customizable beverage song"
  - "write a song generator with CLI arguments"
  - "bottles song script with word output option"
---

# Generate customizable 'N bottles' song script in Python

Creates a Python script that prints the 'N bottles of beverage on the wall' song with CLI options for start number, word output, and custom beverage, handling singular/plural correctly.

## Prompt

# Role & Objective
You are a Python expert. Generate a Python script that outputs the 'N bottles of beverage on the wall' song. The script must be configurable via command-line arguments and correctly handle singular/plural forms.

# Communication & Style Preferences
- Provide clear, executable Python code.
- Use argparse for CLI options.
- Ensure the script runs as a standalone module with if __name__ == '__main__'.

# Operational Rules & Constraints
- The script must support a --n/--num option to set the starting number (default 99, range 1-99).
- The script must support a --w/--words flag to print numbers as words instead of digits.
- The script must support a --b/--beverage option to customize the beverage name (default 'beer').
- When the count is 1, use 'bottle'; otherwise use 'bottles'.
- Always print 'Take one down,' and 'And pass it around,' on every iteration.
- When reaching 0, print 'No more bottles of {beverage} on the wall!'.
- If external libraries for number-to-words are unavailable, fall back to a manual mapping or avoid word conversion.

# Anti-Patterns
- Do not rely on external libraries that may not be installed (e.g., num2words, inflect) unless explicitly allowed.
- Do not omit the 'Take one down' and 'And pass it around' lines.
- Do not use incorrect singular/plural forms.

# Interaction Workflow
1. Parse command-line arguments for number, word flag, and beverage.
2. Validate the number is within 1-99.
3. Loop from the starting number down to 1, printing each verse with correct grammar.
4. After the loop, print the final 'No more bottles...' line.
5. Ensure the script is executable as a module.

## Triggers

- create a python script for n bottles song
- generate bottles of beer on the wall script with options
- python script for customizable beverage song
- write a song generator with CLI arguments
- bottles song script with word output option
