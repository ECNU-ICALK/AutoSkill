---
id: "e5b163ca-8f81-4f87-a769-0c688f669b1c"
name: "np / if / probs"
description: "General SOP for common requests related to np, if, probs."
version: "0.1.0"
tags:
  - "np"
  - "if"
  - "probs"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# np / if / probs

General SOP for common requests related to np, if, probs.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 使用numpy和预计算减少循环
2) token_ids = encoding['input_ids
3) offset_mapping = encoding['offset_mapping
4) num_tokens = len(token_ids
5) if num_tokens == 0
6) return [text], [-1.0
7) 优化1：使用numpy数组代替字典（内存连续访问
8) offset_array = np.array(offset_mapping, dtype=np.int32
9) start_chars = offset_array[:, 0
10) end_chars = offset_array[:, 1

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
