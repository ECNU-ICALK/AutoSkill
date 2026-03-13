---
id: "33ce52c8-a634-4e9f-870d-c9d630886438"
name: "npm / err / claude"
description: "General SOP for common requests related to npm, err, claude."
version: "0.1.0"
tags:
  - "npm"
  - "err"
  - "claude"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# npm / err / claude

General SOP for common requests related to npm, err, claude.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 6ef35338-a10f-4e85-9e94-b9967b7bcd77.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) (base) ids@ids-System-Product-Name:~/workspace$ npm install -g @anthropic-ai/claude-code
8) npm WARN EBADENGINE Unsupported engine {
9) npm WARN EBADENGINE   package: '@anthropic-ai/claude-code@2.1.31',
10) npm WARN EBADENGINE   required: { node: '>=18.0.0' },

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
