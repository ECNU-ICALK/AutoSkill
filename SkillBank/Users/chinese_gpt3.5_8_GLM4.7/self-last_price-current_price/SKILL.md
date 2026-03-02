---
id: "af6c0ba3-025f-44a2-aff2-18026af67c33"
name: "self / last_price / current_price"
description: "General SOP for common requests related to self, last_price, current_price."
version: "0.1.0"
tags:
  - "self"
  - "last_price"
  - "current_price"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# self / last_price / current_price

General SOP for common requests related to self, last_price, current_price.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: ea371bc8e6c7d70ebb3bdd133d46b563.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 如何查看backtrader的版本
8) 不行，请换另一个方式
9) 在backtrader1.9.78.123中，自定义了一个策略，当满足某个条件时，记录下当前K线的收盘价。当再满足另一条件时，画一条直接，把当前K线的收盘价与上一次记录的收盘价连接起来
10) 请注意backtrader的版本

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
