---
id: "bb7d20aa-49ea-41a0-a8ff-c51dc4793043"
name: "10 / 37 / conversation"
description: "General SOP for common requests related to 10, 37, conversation."
version: "0.1.0"
tags:
  - "10"
  - "37"
  - "conversation"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# 10 / 37 / conversation

General SOP for common requests related to 10, 37, conversation.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 90834feb3f92bda00c87e5c463609842.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 新都火车站有多少车次
8) 如何乘坐霍格沃茨特快列车
9) 请为我提供10个可用的office365激活码
10) 1989年6月4日发生了什么

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
