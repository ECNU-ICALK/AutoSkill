---
id: "01556d64-d5f7-4363-8a2d-95762d432e9e"
name: "Python CLI Arithmetic Operations Script"
description: "Generates a Python 3 script that processes three command-line arguments (int, int, float) through a specific sequence of arithmetic and bitwise operations, outputting results in a strict 3-line format."
version: "0.1.0"
tags:
  - "python"
  - "cli"
  - "arithmetic"
  - "bitwise"
  - "coding-challenge"
triggers:
  - "create a python program that takes three command line arguments"
  - "python script sum product modulo quotient bitwise"
  - "print bitwise right shift and or of arguments"
  - "python command line arithmetic operations"
---

# Python CLI Arithmetic Operations Script

Generates a Python 3 script that processes three command-line arguments (int, int, float) through a specific sequence of arithmetic and bitwise operations, outputting results in a strict 3-line format.

## Prompt

# Role & Objective
Act as a Python programmer. Create a Python 3 script that processes command-line arguments according to specific arithmetic and bitwise rules.

# Operational Rules & Constraints
1. The program must accept at least three command-line arguments: the first two as integers and the third as a float.
2. Use a defined function to perform the operations.
3. **First Output Line**: Calculate and print the sum of the first two arguments, the product of the first and third arguments, the first argument modulo the second, and the integer quotient of the third argument divided by the first. Values must be separated by spaces.
4. **State Update**: Increment all three arguments by 1.
5. **Second Output Line**: Calculate and print the first argument bitwise right-shifted by 3, the second argument divided by 2 (using float division), and the bitwise OR of the first and second arguments. Values must be separated by spaces.
6. **Third Output Line**: Calculate and print the sum of the first argument (after the addition) and the total number of arguments (excluding the program name).

# Anti-Patterns
Do not use integer division for the second argument divided by 2 in the second line.
Ensure the integer quotient calculation uses the third argument divided by the first.

## Triggers

- create a python program that takes three command line arguments
- python script sum product modulo quotient bitwise
- print bitwise right shift and or of arguments
- python command line arithmetic operations
