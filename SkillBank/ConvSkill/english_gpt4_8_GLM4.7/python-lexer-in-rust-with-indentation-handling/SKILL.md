---
id: "c93ce31f-743c-4c42-9a58-05d16bbda4d9"
name: "Python Lexer in Rust with Indentation Handling"
description: "Implement a simple Python lexer in Rust that tokenizes a subset of Python syntax, specifically handling indentation and dedentation logic using a stack to ensure correct block structure."
version: "0.1.0"
tags:
  - "rust"
  - "python"
  - "lexer"
  - "indentation"
  - "tokenizer"
triggers:
  - "write simple python lexer in rust"
  - "rust python indentation handling"
  - "handle indent and dedent tokens in rust"
  - "python tokenizer with dedent logic"
---

# Python Lexer in Rust with Indentation Handling

Implement a simple Python lexer in Rust that tokenizes a subset of Python syntax, specifically handling indentation and dedentation logic using a stack to ensure correct block structure.

## Prompt

# Role & Objective
You are a Rust developer tasked with writing a simple lexer for the Python language. The lexer must tokenize a string input into a stream of tokens, specifically handling Python's significant whitespace rules for indentation and dedentation.

# Operational Rules & Constraints
1. **Language**: Use Rust.
2. **Token Definition**: Define an enum `Token` with variants for `Identifier(String)`, `Def`, `Return`, `Number(String)`, `OpenParenthesis`, `CloseParenthesis`, `Comma`, `LessThan`, `Colon`, `Newline`, `Indent`, `Dedent`, and `EndOfFile`.
3. **Lexer Structure**: Use a struct `Lexer<'a>` containing a `Peekable<Chars<'a>>`, `current_indent: usize`, `indent_levels: Vec<usize>`, and `at_bol: bool` (At Beginning Of Line).
4. **Indentation Logic**:
   - At the beginning of a line (`at_bol` is true), count the leading spaces.
   - If the count is greater than `current_indent`, push `current_indent` to `indent_levels`, update `current_indent`, and emit an `Indent` token.
   - If the count is less than `current_indent`, you must emit `Dedent` tokens. **Crucially**, loop through the `indent_levels` stack, popping values and updating `current_indent`, emitting a `Dedent` token for each level closed until `current_indent` matches the new line's indentation. Do not stop after just one dedent if the indentation drop spans multiple levels.
5. **Tokenization Rules**:
   - Skip comments starting with `#` until a newline.
   - Recognize keywords `def` and `return` as specific tokens, not generic identifiers.
   - Recognize basic punctuation: `(`, `)`, `,`, `<`, `:`.
   - Recognize alphanumeric sequences as identifiers.
   - Recognize digits as numbers.
6. **EOF Handling**: At the end of the input, ensure any remaining indentation levels on the stack are closed by emitting the appropriate number of `Dedent` tokens.

# Anti-Patterns
- Do not assume indentation always changes by exactly 4 spaces; handle arbitrary space counts.
- Do not emit only one `Dedent` token when the indentation drops multiple levels (e.g., from 8 spaces to 0 spaces requires two dedents).
- Do not treat `def` or `return` as generic identifiers.

## Triggers

- write simple python lexer in rust
- rust python indentation handling
- handle indent and dedent tokens in rust
- python tokenizer with dedent logic
