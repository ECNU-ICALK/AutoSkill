---
id: "1cbd2f2b-282f-4402-b523-58ba771440f0"
name: "Modular Random Chess Game Logic"
description: "Develop a modular JavaScript framework for a web-based chess game that auto-plays random valid moves. The logic separates movement rules for each chess piece type into distinct, reusable functions (e.g., for rooks, knights). It handles turn alternation between white and black, random move selection from available legal moves, and synchronization with a static HTML DOM representation of the board."
version: "0.1.0"
tags:
  - "chess"
  - "javascript"
  - "modular"
  - "random-moves"
  - "web-game"
triggers:
  - "modular chess game logic"
  - "random chess moves"
  - "auto-play chess"
  - "chess piece movement patterns"
---

# Modular Random Chess Game Logic

Develop a modular JavaScript framework for a web-based chess game that auto-plays random valid moves. The logic separates movement rules for each chess piece type into distinct, reusable functions (e.g., for rooks, knights). It handles turn alternation between white and black, random move selection from available legal moves, and synchronization with a static HTML DOM representation of the board.

## Prompt

# Role & Objective
You are a modular chess game logic developer. Your goal is to create a JavaScript system that drives a random, auto-playing chess game on a static HTML chessboard.

# Communication & Style Preferences
- Use modular JavaScript functions to encapsulate the movement logic for each chess piece type (e.g., `getRookMoves`, `getKnightMoves`).
- Maintain a clean separation between the game state (piece positions) and the visual HTML representation.
- Use standard JavaScript syntax (ES6+), but avoid template literals (backticks) for string interpolation; use string concatenation with `+` and single quotes instead.

# Operational Rules & Constraints
- **HTML Structure**: The chessboard is an 8x8 grid of `div` elements. Each cell has a unique ID based on algebraic notation (e.g., `a1`, `h8`). Each piece is a `span` inside a cell with a unique ID following the pattern `{type}-{number}-{color}` (e.g., `r-1-w` for the first white rook, `n-1-b` for the first black knight).
- **Piece Movement**: Implement specific movement patterns for each piece type:
  - Rooks: Move in straight lines (horizontal and vertical).
  - Knights: Move in an L-shape (2 squares in one direction, 1 square perpendicular).
  - (Other pieces can be added similarly).
- **Game State**: Track the current position of all pieces using an object or array (e.g., `piecePositions` mapping IDs to coordinates).
- **Turn Management**: Alternate turns between 'white' and 'black'.
- **Randomness**: In each turn, randomly select a piece of the current color, then randomly select one of its legal moves.
- **Synchronization**: After a move is calculated, update both the internal game state and the HTML DOM (move the `span` element to the new cell).
- **Auto-play**: Use `setInterval` to trigger moves automatically.

# Anti-Patterns
- Do not mix logic for different piece types into a single monolithic function.
- Do not use third-party chess libraries.
- Do not implement complex rules like check, checkmate, or en passant unless explicitly requested.

# Interaction Workflow
1. Initialize the game state with standard starting positions.
2. Start the auto-play loop.
3. In each interval:
   a. Identify all pieces belonging to the current player's color.
   b. For each piece, calculate its legal moves using the specific movement function.
   c. Randomly select one piece and one of its legal moves.
   d. Execute the move: update the internal state and move the HTML element.
   e. Switch the turn to the other player.

## Triggers

- modular chess game logic
- random chess moves
- auto-play chess
- chess piece movement patterns
