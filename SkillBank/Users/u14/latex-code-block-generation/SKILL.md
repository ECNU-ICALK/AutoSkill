---
id: "1925bb42-5e0b-4608-8c95-e00a3abc7f96"
name: "latex-code-block-generation"
description: "Generates syntactically correct, language-agnostic LaTeX code blocks for technical content (e.g., algorithms, pseudocode, structured explanations), wrapped in triple-backtick fenced code blocks with explicit 'latex' language identifier."
version: "0.1.0"
tags:
  - "latex"
  - "code-block"
  - "technical-writing"
  - "algorithm"
triggers:
  - "用latex代码块的方式撰写"
  - "生成latex格式的算法描述"
  - "输出可编译的latex代码块"
  - "写成```latex形式"
---

# latex-code-block-generation

Generates syntactically correct, language-agnostic LaTeX code blocks for technical content (e.g., algorithms, pseudocode, structured explanations), wrapped in triple-backtick fenced code blocks with explicit 'latex' language identifier.

## Prompt

# Goal
Generate a syntactically valid LaTeX code block (not rendered output) that expresses the requested technical content — such as sorting logic, mathematical derivation, or algorithmic steps — using standard LaTeX packages (e.g., `algorithm`, `algpseudocode`, `amsmath`). The output must be a raw, copy-pasteable code block delimited by ```latex ... ```.

# Constraints & Style
- Always wrap the LaTeX source in a fenced code block with explicit language identifier: ```latex\n...\n```
- Do NOT render or explain the output; output only the raw LaTeX code block.
- Use only widely supported, standard LaTeX constructs (no custom macros unless explicitly requested).
- Prefer clarity and compilability over stylistic flourishes; avoid fragile or editor-specific extensions.
- If the request implies multi-step logic (e.g., heap sort), structure the LaTeX to reflect key phases (e.g., build-heap → extract-max loop) using `algorithm`/`algorithmic` environments or clear `align`/`enumerate` where appropriate.
- Do NOT include preamble (`\documentclass`, `\usepackage`) unless explicitly asked; assume minimal compatible preamble is provided externally.
- Do NOT include `\begin{document}` or `\end{document}` unless explicitly required for self-containment.

## Triggers

- 用latex代码块的方式撰写
- 生成latex格式的算法描述
- 输出可编译的latex代码块
- 写成```latex形式
