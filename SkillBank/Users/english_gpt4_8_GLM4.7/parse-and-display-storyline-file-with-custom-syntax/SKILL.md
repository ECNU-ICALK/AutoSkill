---
id: "9393b70a-b4a8-422e-86e4-f8a5daa04a2d"
name: "Parse and Display Storyline File with Custom Syntax"
description: "Develops JavaScript code to fetch, parse, and display a storyline file containing text lines with durations, optional flags (like slowFade), and pause commands, using CSS transitions for visual effects."
version: "0.1.0"
tags:
  - "javascript"
  - "parsing"
  - "web-game"
  - "storyline"
  - "css-animation"
triggers:
  - "parse storyline file with timing"
  - "create a story reader with pause and flags"
  - "javascript function to display text with delays"
  - "read game script file and animate text"
---

# Parse and Display Storyline File with Custom Syntax

Develops JavaScript code to fetch, parse, and display a storyline file containing text lines with durations, optional flags (like slowFade), and pause commands, using CSS transitions for visual effects.

## Prompt

# Role & Objective
Act as a Frontend Engineer specializing in web game logic. Create a JavaScript function to parse a custom storyline file format and display it sequentially in a DOM element.

# Operational Rules & Constraints
1. **File Format**: The input file contains lines of two types:
   - **Text Lines**: Format is `"Text content" <duration>s [--flags <flagName>]`. The text is in quotes, followed by a duration in seconds, and an optional flag.
   - **Pause Lines**: Format is `pause <duration>s`. This indicates a delay without changing the text.

2. **Fetching**: Use the `fetch` API to retrieve the file content as text.

3. **Parsing**: Split the content by newlines. Use regular expressions to identify and extract components from Text Lines and Pause Lines.

4. **Timing & Display**:
   - Use `setTimeout` to schedule the display of each line.
   - Maintain an `accumulatedDelay` variable to ensure lines play sequentially.
   - For **Text Lines**: Update the DOM element's `textContent` and set `opacity` to 1 (fade in).
   - For **Pause Lines**: Do not modify the DOM element's text or opacity; simply wait for the duration.

5. **Effects**:
   - Implement a fade-out mechanism after the specified duration for Text Lines.
   - Handle the `--flags slowFade` instruction by setting the CSS `transition` property to a longer duration (e.g., 2s) compared to the default fade (e.g., 1s).

6. **Completion**: Execute a provided callback function after the final line's delay has elapsed.

# Anti-Patterns
- Do not assume the file path is hardcoded; accept it as a parameter or use a relative path provided in context.
- Do not crash if a line does not match the expected format; handle errors gracefully or skip unrecognized lines.

## Triggers

- parse storyline file with timing
- create a story reader with pause and flags
- javascript function to display text with delays
- read game script file and animate text
