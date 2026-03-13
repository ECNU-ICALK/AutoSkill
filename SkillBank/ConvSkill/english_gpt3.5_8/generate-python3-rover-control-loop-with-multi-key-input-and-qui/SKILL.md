---
id: "71516da4-e8c8-430a-b90c-87590014aebb"
name: "Generate Python3 rover control loop with multi-key input and quit option"
description: "Creates a Python3 while loop for a rover control program that accepts single and double-character direction keys, prompts for movement duration, and includes a quit option."
version: "0.1.0"
tags:
  - "python3"
  - "rover control"
  - "while loop"
  - "input handling"
  - "quit option"
triggers:
  - "create a rover control loop in python"
  - "python while loop for rover movement with duration"
  - "add quit option to rover control code"
  - "handle multiple keys for rover commands python"
  - "piRover control script with input validation"
---

# Generate Python3 rover control loop with multi-key input and quit option

Creates a Python3 while loop for a rover control program that accepts single and double-character direction keys, prompts for movement duration, and includes a quit option.

## Prompt

# Role & Objective
Generate a Python3 control loop for a rover that processes user input for movement commands with configurable duration and a quit option.

# Communication & Style Preferences
- Provide clear, runnable Python3 code.
- Use uppercase conversion for direction input to handle case-insensitivity.
- Include comments for key sections.

# Operational Rules & Constraints
- Use a while loop controlled by a boolean flag 'go'.
- Prompt for direction input and convert to uppercase.
- Prompt for movement duration and convert to integer.
- Map single keys: 'W' to forward(duration), 'S' to backward(duration), 'D' to right_turn(duration), 'A' to left_turn(duration).
- Map double keys: 'AA' to right_rotate(duration), 'DD' to left_rotate(duration).
- Include a quit option: 'Q' to print stop message, call stop(), and set go = False.
- After each movement command, include time.sleep(2).
- For invalid keys, print an error message and continue the loop.

# Anti-Patterns
- Do not exit the loop on invalid input; only on 'Q'.
- Do not hardcode duration; always prompt for it.
- Do not omit the time.sleep(2) after movement actions.

# Interaction Workflow
1. Initialize with init().
2. Start while go loop.
3. Prompt for direction input.
4. If input is 'Q', handle quit.
5. Otherwise, prompt for duration.
6. Execute corresponding movement function with duration.
7. Sleep for 2 seconds.
8. Loop back to prompt.

## Triggers

- create a rover control loop in python
- python while loop for rover movement with duration
- add quit option to rover control code
- handle multiple keys for rover commands python
- piRover control script with input validation
