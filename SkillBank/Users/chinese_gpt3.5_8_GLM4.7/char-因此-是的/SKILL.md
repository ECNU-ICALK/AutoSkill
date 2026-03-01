---
id: "2adf8e6b-8782-4a56-8cc7-dc053a2fb65a"
name: "char / 因此 / 是的"
description: "General SOP for common requests related to char, 因此, 是的."
version: "0.1.0"
tags:
  - "char"
  - "因此"
  - "是的"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# char / 因此 / 是的

General SOP for common requests related to char, 因此, 是的.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 50d6cd23d7f36c9189fd91855170e0a7.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) c++ 引入byte 是否 多此一举
8) 但是会导致很多库有编译和兼容的问题
9) 因为很多基础库都是C编写的, 而去改变第三方库的代码是不现实的
10) 比如使用到的第三方库有100个,  总不可能去修改这些代码吧, 而且有的库可能并没有源码

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
