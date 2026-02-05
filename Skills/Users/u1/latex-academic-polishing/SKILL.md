---
id: "ea079b3e-7e00-41da-84be-8bc57b00a413"
name: "latex-academic-polishing"
description: "This skill produces publication-ready LaTeX academic text by enforcing typographic correctness, citation integrity, formal tone, and grammatical precision; it should be used when preparing manuscripts for peer-reviewed venues requiring strict LaTeX source compliance."
version: "0.1.2"
tags:
  - "latex"
  - "academic-writing"
  - "editing"
  - "citation-integrity"
  - "typography"
triggers:
  - "This skill should be used when preparing LaTeX manuscripts for peer-reviewed submission."
  - "This skill should be used when converting draft text with em-dashes, straight quotes, or stacked adjectives into publication-ready LaTeX."
  - "This skill should be used when cleaning AI-generated LaTeX that violates typographic, citation, or formal stylistic conventions."
examples:
  - input: "使用latex格式进行撰写，风格简洁有力，不要破折号。"
    output: "To overcome these limitations, researchers have introduced ``slow thinking'' to AI. This human-inspired paradigm favors meticulous, step-by-step reasoning \\cite{<KEY>} over rapid, heuristic-driven responses."
  - input: "This is an example — with an em-dash \\cite{smith2020} and ``quoted text''."
    output: "```latex\nThis is an example, with an em-dash \\cite{smith2020} and ``quoted text''.\n```"
  - input: "This is an example — with an em-dash \\cite{smith2020} and \"quoted text\"."
    output: "```latex\nThis is an example, with an em-dash \\cite{smith2020} and ``quoted text''.\n```"
  - input: "Using ``slow thinking'' improves robustness \\cite{lee2022,chen2023} — especially under distribution shift."
    output: "```latex\nUsing ``slow thinking'' improves robustness \\cite{lee2022,chen2023}, especially under distribution shift.\n```"
  - input: "Using \"slow thinking\" improves robustness \\cite{lee2022,chen2023} — especially under distribution shift."
    output: "```latex\nUsing ``slow thinking'' improves robustness \\cite{lee2022,chen2023}, especially under distribution shift.\n```"
  - input: "Our framework is robust, auditable, and compositionally sound."
    output: "```latex\nOur framework is auditable and compositionally robust.\n```"
---

# latex-academic-polishing

This skill produces publication-ready LaTeX academic text by enforcing typographic correctness, citation integrity, formal tone, and grammatical precision; it should be used when preparing manuscripts for peer-reviewed venues requiring strict LaTeX source compliance.

## Prompt

Edit academic English text into clean, compilable LaTeX source adhering to publishing standards:

1. **Citations**: Preserve every \cite{<KEY>} exactly as given — no reordering, adding, removing, or modifying keys, braces, or internal spacing.
2. **Quotation Marks**: Replace straight ASCII double quotes ("") with LaTeX curly quotes: `` for opening and '' for closing; preserve nesting and context.
3. **Punctuation & Clauses**: Replace em-dashes (—) with commas (,) for appositives or non-restrictive clauses; if en-dash (–) is semantically required (e.g., ranges), use \textendash{} or -- only where conventional (e.g., "pp.~10--15"); never retain standalone em-dashes.
4. **Emphasis & Formatting**: Preserve all semantic markup (e.g., \emph{...}, \textbf{...}, \texttt{...}) unchanged.
5. **Stylistic Precision**: Eliminate stacked adjectives (e.g., "robust, auditable, and compositionally") by rephrasing for clarity and concision (e.g., "auditable and compositionally robust" or splitting into separate clauses); avoid contractions, colloquialisms, and vague intensifiers (e.g., "very", "really").
6. **Whitespace & Formatting**: Remove trailing whitespace; do not auto-wrap lines — only wrap manually at ~80 characters if explicitly present in input.
7. **Output**: Return *only* the edited LaTeX source inside a fenced code block labeled ```latex\n...\n``` — no explanations, commentary, preamble, or extra text before or after.

Bundled resources (optional):
- references/latex-typography-guide.md: explains dash usage, quote styles, Oxford comma conventions, and style-specific rules (APA, Chicago, LNCS) for CS/ML venues.
- scripts/latex-lint-check.py: validates \cite{} balance and brace nesting.
- assets/stacked-adjective-patterns.txt: grep-friendly list of common redundant adjective sequences in technical papers.

## Triggers

- This skill should be used when preparing LaTeX manuscripts for peer-reviewed submission.
- This skill should be used when converting draft text with em-dashes, straight quotes, or stacked adjectives into publication-ready LaTeX.
- This skill should be used when cleaning AI-generated LaTeX that violates typographic, citation, or formal stylistic conventions.

## Examples

### Example 1

Input:

  使用latex格式进行撰写，风格简洁有力，不要破折号。

Output:

  To overcome these limitations, researchers have introduced ``slow thinking'' to AI. This human-inspired paradigm favors meticulous, step-by-step reasoning \cite{<KEY>} over rapid, heuristic-driven responses.

### Example 2

Input:

  This is an example — with an em-dash \cite{smith2020} and ``quoted text''.

Output:

  ```latex
  This is an example, with an em-dash \cite{smith2020} and ``quoted text''.
  ```

### Example 3

Input:

  This is an example — with an em-dash \cite{smith2020} and "quoted text".

Output:

  ```latex
  This is an example, with an em-dash \cite{smith2020} and ``quoted text''.
  ```
