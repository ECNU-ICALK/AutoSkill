---
id: "10f98bdc-2506-4e07-9bd3-a0ebc85b2941"
name: "5000 / conversation / 然而"
description: "General SOP for common requests related to conversation, 225, 作为一个ai语言模型."
version: "0.1.1"
tags:
  - "5000"
  - "conversation"
  - "然而"
  - "225"
  - "作为一个ai语言模型"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# 5000 / conversation / 然而

General SOP for common requests related to conversation, 225, 作为一个ai语言模型.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 4ccbc57476df86df1d972f57cb71da5d.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 矿潮是什么
8) 你认为乌克兰和俄罗斯的战争还要持续多久
9) 如何评价北朝鲜
10) 北朝鲜和南朝鲜那个更加繁华

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
