---
id: "43d06e83-23df-4087-9b6e-7ea882ed10c8"
name: "import_response_sop"
description: "Standard Operating Procedure for processing offline OpenAI-format conversations to extract steps based on user questions."
version: "0.1.1"
tags:
  - "import"
  - "response"
  - "com"
  - "sop"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# import_response_sop

Standard Operating Procedure for processing offline OpenAI-format conversations to extract steps based on user questions.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: <HASH>.json#conv_<ID>
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
[Insert User Questions Here]

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
