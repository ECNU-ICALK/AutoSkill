---
id: "d28c3a67-6705-4ae5-bf00-913bfc5c476d"
name: "c-sorting-pseudocode-generator"
description: "Generates clean, readable C-style pseudocode for classic sorting algorithms (bubble, selection, insertion), accompanied by minimal, plain-text test cases — no decorative symbols, markdown formatting, or visual embellishments."
version: "0.1.0"
tags:
  - "pseudocode"
  - "sorting"
  - "c-language"
  - "testing"
  - "plain-text"
triggers:
  - "用C写排序伪代码"
  - "生成C风格排序伪代码"
  - "给我冒泡排序的C伪代码加测试样例"
  - "不要用符号，只用纯文本写排序伪代码"
---

# c-sorting-pseudocode-generator

Generates clean, readable C-style pseudocode for classic sorting algorithms (bubble, selection, insertion), accompanied by minimal, plain-text test cases — no decorative symbols, markdown formatting, or visual embellishments.

## Prompt

# Goal
Generate C-style pseudocode for a specified sorting algorithm (e.g., bubble, selection, insertion), followed by plain-text test cases in tabular form — using only ASCII characters, no emojis, no bold/italic/markdown syntax, no Unicode box-drawing or arrows.

# Constraints & Style
- Use only plain English and standard C-like syntax (e.g., `for i = 0 to n-1`, `if arr[j] > arr[j+1]`, `swap(a, b)`).
- Do not use any decorative symbols: no ✅, ❌, 🟢, ➡️, →, 🔹, etc.
- Do not use markdown tables, headers (`###`), or code fences (```c`). Instead, format pseudocode as indented plain text with consistent spacing.
- Present test cases as simple aligned columns using only spaces and ASCII punctuation (e.g., `[64,34,25] -> [25,34,64]`).
- Omit all explanatory asides, tips, or commentary unless explicitly requested; keep output strictly algorithm + test cases.
- Assume input is an integer array `arr[]` of length `n`; do not generate full C code (no `#include`, `main`, pointers, or memory management) unless asked.
- If multiple algorithms are requested, separate them with a blank line — no section labels or icons.

## Triggers

- 用C写排序伪代码
- 生成C风格排序伪代码
- 给我冒泡排序的C伪代码加测试样例
- 不要用符号，只用纯文本写排序伪代码
