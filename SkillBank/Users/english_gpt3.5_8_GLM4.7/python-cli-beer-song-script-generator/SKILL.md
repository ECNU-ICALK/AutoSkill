---
id: "af8c4944-9b63-4133-a958-7aa92da57d35"
name: "Python CLI Beer Song Script Generator"
description: "Create a Python script for the 'N bottles of beverage' song with specific CLI arguments, pluralization logic, and standard-library-only number-to-word conversion."
version: "0.1.0"
tags:
  - "python"
  - "cli"
  - "argparse"
  - "scripting"
  - "beer-song"
triggers:
  - "create a python beer song script"
  - "python script for bottles of beer"
  - "cli beer song generator"
  - "python countdown song with argparse"
---

# Python CLI Beer Song Script Generator

Create a Python script for the 'N bottles of beverage' song with specific CLI arguments, pluralization logic, and standard-library-only number-to-word conversion.

## Prompt

# Role & Objective
Act as a Python expert. Create a Python script that outputs the 'N bottles of beverage on the wall' song sequence based on user-defined parameters.

# Operational Rules & Constraints
1. **Code Structure**: The script must define the main logic within a function (e.g., `beer_song`) and use `if __name__ == '__main__':` to execute it.
2. **CLI Arguments**: Use the `argparse` library to implement the following options:
   - `-n` or `--num`: Integer input for the starting number (default 99, range 1-99).
   - `-w` or `--words`: Boolean flag (store_true) to force the program to print numbers as words (e.g., 99 -> 'ninety-nine').
   - `-b` or `--beverage`: String input to select the beverage (default 'beer').
3. **Dependency Constraint**: Do NOT use external libraries like `num2words` or `inflect`. Use only Python standard libraries to handle number-to-word conversion (e.g., manual mapping or logic).
4. **Pluralization Logic**:
   - Use the singular word 'bottle' when the count is exactly 1.
   - Use the plural word 'bottles' for any other count.
5. **Output Format**: Each verse must follow this structure:
   - "[Count] [bottle/bottles] of [beverage] on the wall!"
   - "[Count] [bottle/bottles] of [beverage]!"
   - "Take one down,"
   - "And pass it around,"
   - "[Next Count] [bottle/bottles] of [beverage] on the wall!" (Handle the transition to 0 appropriately, e.g., "No more bottles...").

# Anti-Patterns
- Do not import `num2words` or `inflect`.
- Do not omit the `if __name__ == '__main__':` block.
- Do not fail to handle the singular 'bottle' case for the count of 1.

## Triggers

- create a python beer song script
- python script for bottles of beer
- cli beer song generator
- python countdown song with argparse
