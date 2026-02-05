---
id: "ea079b3e-7e00-41da-84be-8bc57b00a413"
name: "latex-academic-polishing"
description: "当用户需要撰写或润色 LaTeX 格式的学术文本，且要求风格简洁有力、避免使用破折号（以避免 AI 生成痕迹）时使用此技能。"
version: "0.1.0"
tags:
  - "latex"
  - "academic-writing"
  - "formatting"
  - "style-guide"
triggers:
  - "This skill should be used when the user requests writing or polishing text in LaTeX format."
  - "This skill should be used when the user specifies a concise and powerful academic style."
  - "This skill should be used when the user explicitly requests to avoid dashes or AI-like phrasing."
  - "This skill should be used when the user needs correct LaTeX syntax for quotes and citations."
examples:
  - input: "使用latex格式进行撰写，风格简洁有力，不要破折号。"
    output: "To overcome these limitations, researchers have introduced ``slow thinking'' to AI. This human-inspired paradigm favors meticulous, step-by-step reasoning \\cite{<KEY>} over rapid, heuristic-driven responses."
---

# latex-academic-polishing

当用户需要撰写或润色 LaTeX 格式的学术文本，且要求风格简洁有力、避免使用破折号（以避免 AI 生成痕迹）时使用此技能。

## Prompt

Write or polish academic text in LaTeX format adhering to the following constraints:

1. **LaTeX Syntax**:
   - Use standard LaTeX quotation marks: `` (left double quote) and '' (right double quote).
   - Ensure citations are formatted correctly using \cite{<KEY>}.

2. **Style & Tone**:
   - **No Em-Dashes**: Do not use em-dashes (---). To avoid an "AI-generated" feel, use commas or split sentences into shorter, clearer statements instead.
   - **Conciseness**: Maintain a concise, powerful, and academic tone.

3. **Output**:
   - Provide the final result as a LaTeX code block.
   - If multiple variations are possible, prioritize the most concise and natural option.

## Triggers

- This skill should be used when the user requests writing or polishing text in LaTeX format.
- This skill should be used when the user specifies a concise and powerful academic style.
- This skill should be used when the user explicitly requests to avoid dashes or AI-like phrasing.
- This skill should be used when the user needs correct LaTeX syntax for quotes and citations.

## Examples

### Example 1

Input:

  使用latex格式进行撰写，风格简洁有力，不要破折号。

Output:

  To overcome these limitations, researchers have introduced ``slow thinking'' to AI. This human-inspired paradigm favors meticulous, step-by-step reasoning \cite{<KEY>} over rapid, heuristic-driven responses.
