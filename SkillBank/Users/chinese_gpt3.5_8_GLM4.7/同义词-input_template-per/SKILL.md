---
id: "44869016-d093-4162-866e-f62860e87bc1"
name: "同义词 / input_template / per"
description: "General SOP for common requests related to 同义词, input_template, per."
version: "0.1.0"
tags:
  - "同义词"
  - "input_template"
  - "per"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# 同义词 / input_template / per

General SOP for common requests related to 同义词, input_template, per.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: b8f20d8b22a9429f16b1b6769a51a9ea.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) 我想让你完成一个语言重新表达的任务。格式和要求如下。
8) 任务模板是我要给你的，以“input_template“字样开头；生产模板是你要根据任务模板输出的。
9) 生产模板只需要根据任务模板输出相应修改后的input_template。
10) input_template则需要在内容格式不变的前提下，对任务模板中的input_template做一定的变化：

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
