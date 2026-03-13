---
id: "fea5a748-fc01-43d6-a9e6-549387b59de1"
name: "Parse and display timed storyline with flags"
description: "Parses a storyline file with quoted text, duration, and optional flags to display each line with timed fades and pauses."
version: "0.1.0"
tags:
  - "storyline"
  - "parser"
  - "timing"
  - "fade"
  - "javascript"
triggers:
  - "parse storyline file with timing"
  - "display timed text with fade effects"
  - "read and animate story lines"
  - "handle pause commands in script"
  - "create timed text display with flags"
---

# Parse and display timed storyline with flags

Parses a storyline file with quoted text, duration, and optional flags to display each line with timed fades and pauses.

## Prompt

# Role & Objective
Parse a storyline file and display each line with specified timing and effects. Handle quoted text lines with durations and optional flags, and pause commands without text.

# Communication & Style Preferences
- Use JavaScript fetch to read the storyline file.
- Use CSS opacity transitions for fade effects.
- Log errors for unrecognized line formats.

# Operational Rules & Constraints
- File format per line: "<text>" <duration>s [--flags <flagName>]
- Pause command format: pause <duration>s
- Convert seconds to milliseconds for setTimeout.
- For slowFade flag, use 2s transition; otherwise use 1s.
- Accumulate delays sequentially; add fade-out time only for text lines, not pauses.
- Execute optional callback after the entire storyline completes.

# Anti-Patterns
- Do not assume all lines have quotes; handle pause lines separately.
- Do not ignore flags; apply slowFade when present.
- Do not skip lines; process each line in order.

# Interaction Workflow
1. Fetch storyline file content.
2. Split content into lines.
3. For each line, match either quoted text with duration/flags or pause command.
4. Schedule display with setTimeout using accumulated delay.
5. Apply fade-in/out with CSS transitions.
6. After all lines, invoke callback if provided.

## Triggers

- parse storyline file with timing
- display timed text with fade effects
- read and animate story lines
- handle pause commands in script
- create timed text display with flags
