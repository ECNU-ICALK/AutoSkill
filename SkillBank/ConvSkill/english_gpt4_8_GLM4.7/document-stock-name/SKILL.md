---
id: "e42e2009-dd6b-4d0b-8d0e-23757808156f"
name: "document / stock / name"
description: "General SOP for common requests related to document, stock, name."
version: "0.1.0"
tags:
  - "document"
  - "stock"
  - "name"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# document / stock / name

General SOP for common requests related to document, stock, name.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) e020643b30612cf889f63acc91eb4c75.json#conv_1
2) Use the user questions below as the PRIMARY extraction evidence
3) Use the full conversation below as SECONDARY context reference
4) In the full conversation section, assistant/model replies are reference-only and not skill evidence
5) Primary User Questions (main evidence
6) test
7) docRef.get
8) addOnSuccessListener { document
9) if (document.exists
10) val names = document.get("name") as? List<String> ?: mutableListOf

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
