---
id: "14cb752b-b621-41d5-90c0-9bfc8b9fdfae"
name: "Standard release process"
description: "General SOP for common requests related to self, if, return."
version: "0.1.0"
tags:
  - "self"
  - "if"
  - "return"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# Standard release process

General SOP for common requests related to self, if, return.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) V1: 文本级判等，使用 verify_math_equal
2) V2: sympy_obj 级判等，使用 EqualityChecker + EED 软匹配
3) 模块结构
4) math_equal.py: 无状态工具函数 (verify_math_equal, dedup_entities
5) entity_verifier.py: EntityVerifier 类
6) verification_strategy.py: 策略类 (V1, V2
7) 首先从 math_equal 导入，避免循环引用
8) from .math_equal import verify_math_equal, dedup_entities
9) 然后导入主类
10) from .entity_verifier import EntityVerifier

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
