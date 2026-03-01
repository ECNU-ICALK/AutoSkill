---
id: "cd70862c-e621-4492-b695-99045da7744f"
name: "dsl_data / queries / dimensions"
description: "General SOP for common requests related to dsl_data, queries, dimensions."
version: "0.1.0"
tags:
  - "dsl_data"
  - "queries"
  - "dimensions"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# dsl_data / queries / dimensions

General SOP for common requests related to dsl_data, queries, dimensions.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 217a24ee845d0c8be48ddc8d7dc34d6b.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 请先理解以下DSL格式数据："{
8) ““type””: ““query_indicator””,
9) ““queries””: [
10) ““queryType””: ““QuickQuery””,

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
