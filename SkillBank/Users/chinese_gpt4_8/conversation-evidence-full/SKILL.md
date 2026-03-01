---
id: "fa34c848-f9a1-4fe2-9dee-e65b333a84b4"
name: "conversation / evidence / full"
description: "General SOP for common requests related to conversation, evidence, full."
version: "0.1.2"
tags:
  - "conversation"
  - "evidence"
  - "full"
  - "2024"
  - "questions"
  - "backdrop"
  - "filter"
  - "powershell"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# conversation / evidence / full

General SOP for common requests related to conversation, evidence, full.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 20c316ab5a56d276cbababdc5401d8fe.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 写一首藏头诗绝句，头 是：“洗尽瓶啥”
8) 头：洗尽瓶是啥彼
9) 尽 是第二局
10) 第一句太长了

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
