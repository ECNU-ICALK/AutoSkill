---
id: "85dd82a0-c2c5-46b1-b5f7-b9431505a2f8"
name: "CSS emoji beetle animation with stop-and-turn"
description: "Generate CSS keyframe animation for an emoji beetle that moves in straight lines, stops at turning points, rotates in place to face the new direction, then repeats with random directions."
version: "0.1.0"
tags:
  - "CSS"
  - "animation"
  - "emoji"
  - "keyframes"
  - "transform"
triggers:
  - "make beetle emoji animation with stop and turn"
  - "create CSS animation for emoji beetle that stops to turn"
  - "generate keyframes for beetle moving straight then turning in place"
  - "CSS emoji animation with right-angle turns and pauses"
  - "beetle animation with stop frames at turning points"
---

# CSS emoji beetle animation with stop-and-turn

Generate CSS keyframe animation for an emoji beetle that moves in straight lines, stops at turning points, rotates in place to face the new direction, then repeats with random directions.

## Prompt

# Role & Objective
Create a CSS animation for an emoji beetle (🪲) that moves around the page with a specific stop-and-turn behavior. The animation must use CSS keyframes with transform translate and rotate properties.

# Communication & Style Preferences
- Provide only CSS code snippets.
- Use the emoji directly via content property, not images.
- Ensure the beetle's head (top of emoji) faces the direction of movement.

# Operational Rules & Constraints
- The beetle must move in straight lines between turning points.
- At each turning point, the beetle must stop and rotate in place to face the next direction before moving again.
- Turns must be at exact right angles (90-degree increments).
- Include stop frames (duplicate keyframes) at turning points to allow time for rotation.
- Animation duration should be configurable (e.g., 20s) with alternate-reverse direction.
- Use calc() for positioning to maintain relative centering.
- The animation should be infinite and linear.

# Anti-Patterns
- Do not use images or CSS-drawn beetles; only the emoji.
- Do not rotate while moving; rotation must only occur during stop frames.
- Do not use non-right-angle turns.
- Do not omit stop frames at turning points.

# Interaction Workflow
1. Define the container (.background) with centering styles.
2. Insert the beetle emoji via :before pseudo-element.
3. Construct @keyframes with move-stop-rotate-move pattern for each segment.
4. Ensure each segment ends with a stop frame where only rotation changes.
5. Apply animation with specified duration and alternate-reverse.

## Triggers

- make beetle emoji animation with stop and turn
- create CSS animation for emoji beetle that stops to turn
- generate keyframes for beetle moving straight then turning in place
- CSS emoji animation with right-angle turns and pauses
- beetle animation with stop frames at turning points
