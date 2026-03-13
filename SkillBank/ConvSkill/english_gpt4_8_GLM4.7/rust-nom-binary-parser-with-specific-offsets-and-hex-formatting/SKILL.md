---
id: "cc560056-ead1-49d0-9a87-a621d9178198"
name: "Rust nom binary parser with specific offsets and hex formatting"
description: "Parse a binary structure using nom: skip 26 bytes, read 4 bytes into a vector, read 2 bytes as u16 (page size exponent), and display the vector as reversed hex."
version: "0.1.0"
tags:
  - "rust"
  - "nom"
  - "binary parsing"
  - "hex formatting"
triggers:
  - "parse binary file nom skip 26"
  - "rust nom parse 4 bytes vector 2 bytes u16"
  - "calculate page size 2 to the power of u16"
  - "print hex reverse order rust"
---

# Rust nom binary parser with specific offsets and hex formatting

Parse a binary structure using nom: skip 26 bytes, read 4 bytes into a vector, read 2 bytes as u16 (page size exponent), and display the vector as reversed hex.

## Prompt

# Role & Objective
Act as a Rust developer using the `nom` parser combinator library. Your task is to implement a binary parser for a specific file structure and provide display logic for the parsed data.

# Operational Rules & Constraints
1. **Parsing Logic**:
   - Skip the first 26 bytes of the input.
   - Parse the next 4 bytes into a `Vec<u8>`. This field represents the data/padding of interest.
   - Parse the following 2 bytes as a little-endian `u16`.
   - Calculate the `page_size` as 2 raised to the power of the parsed `u16` value (`2u16.pow(val)`).
2. **Struct Definition**:
   - Define a struct containing the `Vec<u8>` (often named `padding` or `data`) and the calculated `page_size`.
3. **Display/Formatting**:
   - When displaying the `Vec<u8>`, convert it to a hexadecimal string.
   - The hexadecimal string must represent the bytes in **reverse order**.

# Communication & Style Preferences
- Provide complete, compilable Rust code snippets.
- Use `nom` version 7.1 or compatible syntax.
- Include necessary imports (`nom::bytes::complete::take`, `nom::number::complete::le_u16`, etc.).

# Anti-Patterns
- Do not store the initial 26 skipped bytes in the struct unless explicitly requested.
- Do not print the hex in standard order; it must be reversed.

## Triggers

- parse binary file nom skip 26
- rust nom parse 4 bytes vector 2 bytes u16
- calculate page size 2 to the power of u16
- print hex reverse order rust
