---
id: "5d8029de-4f83-4e81-bacf-72cc45da0f18"
name: "self / torch / hidden_states"
description: "General SOP for common requests related to self, torch, hidden_states."
version: "0.1.0"
tags:
  - "self"
  - "torch"
  - "hidden_states"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# self / torch / hidden_states

General SOP for common requests related to self, torch, hidden_states.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) python
2) del self.transformer.residual_dict
3) 或者
4) delattr(self.transformer, "residual_dict
5) 如果你不确定它是否存在，避免抛 `AttributeError`，可以这样写
6) python
7) if hasattr(self.transformer, "residual_dict
8) delattr(self.transformer, "residual_dict
9) 补充两点常见情况
10) 1) 如果 `residual_dict` 其实是某个 dict 里的键（而不是属性），比如 `self.transformer` 自己是 dict 或包含 dict，那么应当用

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
