---
id: "d9be921b-eb69-4778-8cef-d141dd5f658c"
name: "sample / response / python"
description: "General SOP for common requests related to sample, response, python."
version: "0.1.0"
tags:
  - "sample"
  - "response"
  - "python"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# sample / response / python

General SOP for common requests related to sample, response, python.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 响应预处理**：提取 `</think>` 标签后的内容
2) 条件化 payload 构建**：根据 `is_proof` 字段构建不同的 payload
3) 重试机制**：3次重试，指数退避（1s, 2s, 4s
4) 错误处理**：详细的错误日志和默认返回值
5) 返回完整结构**：包含 `score`, `point`, `acc`, `extracted_gt/pred`, `scored_by` 等字段
6) 未注释版本（简单
7) 直接使用 `sample.response
8) 简单的 payload（只包含 `prompt`, `response`, `label
9) 无重试机制
10) 使用 `raise_for_status()` 直接抛出异常

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
