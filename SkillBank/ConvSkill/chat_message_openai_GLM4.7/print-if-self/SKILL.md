---
id: "820eba32-505f-4d81-bd31-b30b98f72900"
name: "print / if / self"
description: "General SOP for common requests related to print, if, self."
version: "0.1.0"
tags:
  - "print"
  - "if"
  - "self"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# print / if / self

General SOP for common requests related to print, if, self.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) The) (noun phrase/answer/output) (is
2) pattern = r'^(the\s+)?(noun\s+phrase|answer|output|result|response)\s*(is)?\s*[:]\s
3) cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE
4) 4. 移除常规句子前缀 (以防正则没兜住
5) prefixes_to_remove
6) This is a ", "This is an ", "The object is a ", "The object is an
7) I see a ", "I see an ", "It appears to be a ", "It appears to be an
8) It is a ", "It is an ", "It's a ", "It's an
9) A ", "An ", "The
10) 循环检查两次以防双重前缀 (e.g. "The object is a traffic light

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
