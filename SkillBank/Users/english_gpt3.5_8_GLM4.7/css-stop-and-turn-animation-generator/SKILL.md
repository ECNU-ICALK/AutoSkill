---
id: "5b81cb8a-ade1-4778-97ec-236a0ae7fc05"
name: "CSS Stop-and-Turn Animation Generator"
description: "Generates CSS keyframe animations where an object moves in straight lines, stops at turning points to rotate in place, and then continues moving."
version: "0.1.0"
tags:
  - "css"
  - "animation"
  - "keyframes"
  - "movement"
  - "web development"
triggers:
  - "css animation stop and turn"
  - "css keyframes move stop rotate"
  - "emoji running around page css"
  - "css animation with turning points"
---

# CSS Stop-and-Turn Animation Generator

Generates CSS keyframe animations where an object moves in straight lines, stops at turning points to rotate in place, and then continues moving.

## Prompt

# Role & Objective
Create CSS animations for objects (emojis or elements) that follow a specific movement pattern: move straight, stop, turn in place, and move again.

# Operational Rules & Constraints
1. Use `transform: translate(x, y)` for positioning and `transform: rotate(deg)` for orientation.
2. Ensure the top of the emoji/element faces the direction of movement.
3. Implement "stop frames" at turning points: the object must pause movement to rotate in place before proceeding to the next coordinate.
4. Use `alternate-reverse` for the animation direction if specified.
5. Set animation duration (e.g., 20s) as requested.
6. Calculate turning angles to be exact right angles (90-degree increments) or random directions as specified.

# Anti-Patterns
Do not rotate while moving; rotation must happen during the stop phase. Do not use images if an emoji is specified.

## Triggers

- css animation stop and turn
- css keyframes move stop rotate
- emoji running around page css
- css animation with turning points
