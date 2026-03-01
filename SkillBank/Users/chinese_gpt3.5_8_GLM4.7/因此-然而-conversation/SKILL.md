---
id: "c75c51cc-5b59-47cb-8bde-98abbb8815bd"
name: "因此 / 然而 / conversation"
description: "General SOP for common requests related to 因此, 然而, conversation."
version: "0.1.0"
tags:
  - "因此"
  - "然而"
  - "conversation"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# 因此 / 然而 / conversation

General SOP for common requests related to 因此, 然而, conversation.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 83b35598fa1ff4a44b537d775a3a7756.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 请问我做翻译，应该一次会议我一个人只需要翻译一门母语加上一门外语吧，听说要翻译三门甚至更多语言，不知道是不是真的
8) 请问日本压抑吗？排外吗？封建皇权思想严重吗？可以骂天皇或者政府吗？女性地位怎么样
9) 侵华战争话题在日本是不是违法
10) 日本的上下级观念是不是很严重，必须使用敬语吗

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
