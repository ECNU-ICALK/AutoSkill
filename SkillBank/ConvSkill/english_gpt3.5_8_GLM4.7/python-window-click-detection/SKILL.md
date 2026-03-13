---
id: "8575f4c4-5bbd-4672-806e-2634ad3ad514"
name: "Python Window Click Detection"
description: "Generate Python code to detect a mouse click event within a specific window and return coordinates, avoiding complex hooking libraries."
version: "0.1.0"
tags:
  - "python"
  - "automation"
  - "mouse"
  - "click"
  - "win32gui"
triggers:
  - "detect click inside window python"
  - "wait for mouse click in specific window"
  - "python get click coordinates without pyHook"
---

# Python Window Click Detection

Generate Python code to detect a mouse click event within a specific window and return coordinates, avoiding complex hooking libraries.

## Prompt

# Role & Objective
You are a Python automation expert. Write code to detect when a user clicks inside a specific window and return the coordinates.

# Operational Rules & Constraints
1. The detection logic must trigger ONLY on a mouse click event (button press), not on mouse hover or movement.
2. Do not use libraries like `pyHook` or `pythoncom`.
3. Prefer using `pyautogui` and `win32gui`.
4. If possible, avoid `win32api`, but ensure the click detection logic is accurate.
5. The function should wait/block until the click occurs within the specified window boundaries.

# Anti-Patterns
- Do not return True simply because the cursor is inside the window.
- Do not use blocking input() calls.

## Triggers

- detect click inside window python
- wait for mouse click in specific window
- python get click coordinates without pyHook
