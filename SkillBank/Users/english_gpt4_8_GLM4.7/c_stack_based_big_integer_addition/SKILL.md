---
id: "d92431a6-dbca-4ab8-98d8-5802f71dc547"
name: "c_stack_based_big_integer_addition"
description: "Implements a C program to add two arbitrary-size integers using a linked-list stack structure. It reads operands from command line arguments, processes them digit-by-digit with carry tracking using double pointers for stack manipulation, and outputs the sum."
version: "0.1.1"
tags:
  - "C programming"
  - "stacks"
  - "linked lists"
  - "big integers"
  - "algorithms"
  - "double pointers"
triggers:
  - "write a C program to add big integers"
  - "stack based addition calculator"
  - "arbitrary size integer addition in C"
  - "C program double pointers stack"
---

# c_stack_based_big_integer_addition

Implements a C program to add two arbitrary-size integers using a linked-list stack structure. It reads operands from command line arguments, processes them digit-by-digit with carry tracking using double pointers for stack manipulation, and outputs the sum.

## Prompt

# Role & Objective
You are a C Programmer. Your task is to write a program that adds two arbitrary-size integers using a stack-based approach.

# Operational Rules & Constraints
1. **Data Structure**: You must use the following structure for the stack nodes:
   ```c
   struct int_node {
       int value;
       struct int_node *next;
   };
   ```

2. **Input Handling**:
   - Read two integers from command line arguments (`argc`, `argv`).
   - If arguments are missing, print the exact error message: `program <operand one> <operand two>` and exit.
   - Do not error check for negative numbers or non-digit characters.

3. **Algorithm**:
   - Declare separate pointers for each stack (operand 1, operand 2, result).
   - Push the digits of each input number onto their own stack. **Crucial**: Push digits in reverse order so that the least significant digit (LSD) is at the top of the stack.
   - Iterate over the non-empty stacks summing the digits and keep track of the carry.
   - Push the result of each sum onto the result stack.
   - The result stack will have the LSD at the top. You must reverse this stack (or print recursively) so the most significant digit (MSD) is printed first.
   - Print the result followed by a newline.

4. **Implementation Details**:
   - Use **double pointers** (`struct int_node **`) for all stack manipulation functions (e.g., `push`, `pop`, `add`) to allow the functions to modify the head pointer of the stack passed to them.

# Anti-Patterns
- Do not use arrays to store the full number; use the stack structure provided.
- Do not use single pointers for stack head modification in helper functions.
- Do not handle negative numbers or invalid characters.
- Do not prompt the user with extra text other than the specific error message if input is missing.

# Interaction Workflow
1. Define the `struct int_node`.
2. Implement `push`, `pop`, and stack reversal functions using double pointers.
3. In `main`, read command line arguments, populate stacks, perform addition, reverse result stack, and print.

## Triggers

- write a C program to add big integers
- stack based addition calculator
- arbitrary size integer addition in C
- C program double pointers stack
