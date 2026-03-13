---
id: "7c467274-57b5-4170-9c4d-b7140d95076e"
name: "Implement Session-Based Image Viewer Timer"
description: "Implement a dual-mode timer logic for an image viewer that switches between a standard fixed interval and a session-based interval iterating through a list of image counts and durations."
version: "0.1.0"
tags:
  - "python"
  - "tkinter"
  - "timer"
  - "session-management"
  - "image-viewer"
triggers:
  - "implement session timer logic"
  - "switch between standard and session mode timer"
  - "timer based on image count list"
  - "pause timer after session list ends"
---

# Implement Session-Based Image Viewer Timer

Implement a dual-mode timer logic for an image viewer that switches between a standard fixed interval and a session-based interval iterating through a list of image counts and durations.

## Prompt

# Role & Objective
You are a Python/Tkinter developer implementing a dual-mode timer for an image viewer. The timer must support a standard fixed interval mode and a session-based mode where intervals change based on a predefined list of configurations.

# Operational Rules & Constraints
1. **Mode Toggle**: Use a boolean flag (e.g., `self.togsess_mode`) to determine the active mode.
2. **Standard Mode**:
   - Calculate the interval in seconds from `minutes` and `seconds` inputs.
   - Store the result as an integer.
3. **Session Mode**:
   - Parse a list of strings (e.g., `['5 pics for 30s', '5 pics for 1m']`) into a list of tuples `(num_pics, duration_seconds)`.
   - Initialize `session_index` to 0 and `session_image_count` to the first item's count.
   - Set the initial `timer_interval` to the first item's duration.
4. **Timer Update Logic (`update_timer`)**:
   - If `session_active` is True:
     - Decrement `session_image_count`.
     - If `session_image_count` <= 0:
       - Increment `session_index`.
       - If `session_index` >= length of the session list: Call `pause_timer()` to stop and reset.
       - Else: Update `timer_interval` to the new session's duration and reset `session_image_count`.
   - Else: Use the standard fixed interval.
5. **Pause Logic (`pause_timer`)**:
   - Cancel any scheduled timer event (e.g., `root.after_cancel`).
   - Set `timer_running = False`.
   - If `session_active`: Reset `session_index` to 0 and `session_image_count` to the first session's count.
6. **Initialization**: Ensure `timer_running`, `timer_id`, `session_active`, `session_index`, and `session_image_count` are initialized in `__init__` to prevent AttributeErrors.
7. **Type Safety**: Ensure `dialog.result` is handled as an integer in standard mode and as a list in session mode to avoid TypeErrors/ValueErrors.

## Triggers

- implement session timer logic
- switch between standard and session mode timer
- timer based on image count list
- pause timer after session list ends
