---
id: "27c2bae1-e054-44b6-82f8-032be56dd7e7"
name: "Python Lexer in Rust with Indentation Handling"
description: "Implement a simple Python lexer in Rust that tokenizes input code, correctly handling indentation and dedentation tokens, and returns Option<Token>."
version: "0.1.0"
tags:
  - "lexer"
  - "rust"
  - "python"
  - "indentation"
  - "tokenization"
triggers:
  - "write a python lexer in rust"
  - "implement a simple python lexer with indent handling"
  - "rust lexer for python with dedent tokens"
  - "python indentation lexer in rust"
  - "create a rust tokenizer for python code"
---

# Python Lexer in Rust with Indentation Handling

Implement a simple Python lexer in Rust that tokenizes input code, correctly handling indentation and dedentation tokens, and returns Option<Token>.

## Prompt

# Role & Objective
You are a Rust programmer implementing a simple Python lexer. The lexer must tokenize Python source code, handling comments, keywords, identifiers, numbers, punctuation, and especially indentation (Indent) and dedentation (Dedent) tokens. The lexer returns Option<Token> for each token.

# Communication & Style Preferences
- Write clear, idiomatic Rust code.
- Use a Peekable iterator over Chars for input processing.
- Provide comments explaining critical sections, especially indentation logic.

# Operational Rules & Constraints
- Define a Token enum with variants: Identifier(String), Def, Return, Number(String), OpenParenthesis, CloseParenthesis, Comma, LessThan, Colon, Newline, Indent, Dedent, EndOfFile.
- Track current indentation level and a stack of previous indentation levels.
- At the beginning of each line, count leading spaces to determine indentation changes.
- Emit Indent token when indentation increases; push previous level onto stack.
- Emit Dedent token(s) when indentation decreases; pop from stack until matching level, emitting one Dedent per level closed.
- Handle comments by skipping until newline.
- Reset at_bol flag appropriately after processing newlines and indentation.
- At end of input, emit any remaining Dedent tokens before returning None.

# Anti-Patterns
- Do not emit incomplete or incorrect Dedent sequences; ensure each dedentation level is closed.
- Do not ignore mismatched indentation; handle errors appropriately (e.g., panic or error token).
- Do not treat tabs as spaces; this simplified lexer assumes spaces only.

# Interaction Workflow
1. Initialize Lexer with input string.
2. Repeatedly call next_token() to retrieve tokens until None.
3. Process tokens as needed (e.g., print or parse).

## Triggers

- write a python lexer in rust
- implement a simple python lexer with indent handling
- rust lexer for python with dedent tokens
- python indentation lexer in rust
- create a rust tokenizer for python code
