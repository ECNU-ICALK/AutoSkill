---
id: "c22ee8d7-bb78-4682-938c-39bb36fbcea8"
name: "print / steps / statistics"
description: "General SOP for common requests related to print, steps, statistics."
version: "0.1.0"
tags:
  - "print"
  - "steps"
  - "statistics"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# print / steps / statistics

General SOP for common requests related to print, steps, statistics.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Selector提出的 ∪ Verifier验证过的（set自动保证唯一性）_
2) key_steps_indices = selector_steps.union(verifier_steps
3) return key_steps_indices
4) def analyze_key_steps(base_path
5) 分析所有文件的key_step统计
6) compact_files, log_files = find_json_files(base_path
7) statistics
8) invalid_steps_log = []  _# 记录被过滤的无效步骤_
9) for compact_file, log_file in zip(compact_files, log_files
10) try

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
