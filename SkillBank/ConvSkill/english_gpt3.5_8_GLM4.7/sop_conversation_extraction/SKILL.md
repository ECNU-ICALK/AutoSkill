---
id: "e69c6536-63bb-4da7-847d-7418f6b98206"
name: "sop_conversation_extraction"
description: "Standard Operating Procedure for extracting evidence and defining steps from OpenAI-format conversation sources."
version: "0.1.6"
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

# Role & Objective
Follow this SOP to extract evidence and define steps from OpenAI-format conversation sources. Replace specific identifiers with placeholders like <PROJECT>/<ENV>/<VERSION>.

# Constraints & Style
- Use user questions as the PRIMARY extraction evidence.
- Use the full conversation as SECONDARY context reference.
- Assistant/model replies are reference-only and not skill evidence.

# Core Workflow
1) Identify the Offline OpenAI-format conversation source.
2) Extract the Title (e.g., <HASH_ID>#<CONV_ID>).
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Isolate Primary User Questions (main evidence).
7) [Insert User Question 1]
8) [Insert User Question 2]
...

# Output Format
For each step, include: action, checks, and failure rollback/fallback plan.
For each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
