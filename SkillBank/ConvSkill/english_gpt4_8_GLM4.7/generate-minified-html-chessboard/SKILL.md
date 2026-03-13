---
id: "984294d1-ed80-44ee-8889-5e8af3841d0d"
name: "Generate Minified HTML Chessboard"
description: "Generates a highly minified HTML/CSS representation of a chessboard position using specific Unicode characters and short tag names to stay under a strict character limit."
version: "0.1.0"
tags:
  - "html"
  - "css"
  - "chess"
  - "minification"
  - "unicode"
triggers:
  - "generate minified chessboard"
  - "arrange pieces famous game"
  - "leet chessboard html"
  - "minify chess code"
---

# Generate Minified HTML Chessboard

Generates a highly minified HTML/CSS representation of a chessboard position using specific Unicode characters and short tag names to stay under a strict character limit.

## Prompt

# Role & Objective
Generate a minified HTML/CSS string representing a chessboard position based on user requests (e.g., specific games or setups).

# Operational Rules & Constraints
1. Use `<p>` as the container tag and `<b>` for chess pieces to minimize character count.
2. Use the CSS: `<style>p{color:#862}b{position:absolute}</style>`.
3. Represent black squares with `⬛` and white squares with `⬜`.
4. Use standard Unicode chess symbols for pieces (e.g., ♜, ♞, ♝, ♛, ♚, ♟, ♖, ♘, ♗, ♕, ♔, ♙).
5. Structure the board as 8 rows of 8 cells.
6. Separate rows using `<br>`.
7. Place piece tags (`<b>...</b>`) immediately *before* the square character they occupy in the HTML stream.
8. Ensure the total character count is minimized (aim for ~409 characters or less).
9. Maintain the integrity of the 8x8 grid (alternating colors).

## Triggers

- generate minified chessboard
- arrange pieces famous game
- leet chessboard html
- minify chess code
