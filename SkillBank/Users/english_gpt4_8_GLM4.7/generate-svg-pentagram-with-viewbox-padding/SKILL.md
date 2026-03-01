---
id: "8bed4869-204d-4953-ad00-0c9d15180a4e"
name: "Generate SVG Pentagram with ViewBox Padding"
description: "Generates a precise SVG pentagram inscribed in a circle, handling padding by expanding the viewBox rather than scaling the path, and outputting a raw single-line string."
version: "0.1.0"
tags:
  - "svg"
  - "pentagram"
  - "geometry"
  - "viewbox"
  - "padding"
triggers:
  - "draw pentagram inside circle"
  - "svg pentagram with padding"
  - "generate svg code for pentagram"
  - "perfect pentagram star"
---

# Generate SVG Pentagram with ViewBox Padding

Generates a precise SVG pentagram inscribed in a circle, handling padding by expanding the viewBox rather than scaling the path, and outputting a raw single-line string.

## Prompt

# Role & Objective
Generate SVG code for a pentagram star inscribed within a circle. The task requires precise geometric calculation and specific handling of padding via viewBox adjustments.

# Operational Rules & Constraints
1. **Padding Strategy**: To add padding to a path of dimension D with padding P, set the SVG `viewBox` to `0 0 (D+P) (D+P)`. Keep the actual path coordinates centered within the original D dimension. Do not scale the path coordinates; use the viewBox to create the visual margin.
2. **Geometric Precision**: Calculate the pentagram vertices using trigonometry (72-degree intervals) to ensure they perfectly touch the circumscribed circle.
3. **Output Contract**: Output the SVG code as a single, continuous string starting from the very first character.
4. **Formatting Restrictions**: Absolutely no newlines, no backticks, no markdown code blocks, and no explanatory text or descriptions.

# Anti-Patterns
- Do not provide explanations or conversational filler.
- Do not wrap the output in markdown.
- Do not scale the path coordinates to fit padding; use viewBox expansion.

## Triggers

- draw pentagram inside circle
- svg pentagram with padding
- generate svg code for pentagram
- perfect pentagram star
