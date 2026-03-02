---
id: "e69c6536-63bb-4da7-847d-7418f6b98206"
name: "sop_conversation_extraction"
description: "Standard Operating Procedure for extracting evidence and defining steps from OpenAI-format conversation sources."
version: "0.1.1"
tags:
  - "sop"
  - "extraction"
  - "checklist"
  - "process"
  - "conversation"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# sop_conversation_extraction

Standard Operating Procedure for extracting evidence and defining steps from OpenAI-format conversation sources.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: <CONVERSATION_ID>
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
<USER_QUESTIONS>

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
