---
id: "4d65e41a-4126-4681-8ebd-d90beeffa349"
name: "standard_release_process"
description: "Generates a Standard Operating Procedure (SOP) based on offline conversation evidence, utilizing specific user queries as primary extraction points."
version: "0.1.2"
tags:
  - "sop"
  - "process"
  - "checklist"
  - "china"
  - "browser"
  - "google"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# standard_release_process

Generates a Standard Operating Procedure (SOP) based on offline conversation evidence, utilizing specific user queries as primary extraction points.

## Prompt

Generate a Standard Operating Procedure (SOP) based on the provided offline conversation evidence. Replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>.

**Context & Evidence:**
1. Source: Offline OpenAI-format conversation.
2. Reference ID: 3090b1de4c6b940b65d1e55f8003e272.json#conv_1
3. Primary User Questions (Evidence):
   - pixel warfare 3 demo
   - how do i play pixel warfare 3 abolised version in 2023
   - What is the most popular browser in china?
   - What is the most popular browser in china? on pc

**Instructions:**
- Use the user questions above as the PRIMARY extraction evidence.
- Use the full conversation below as SECONDARY context reference.
- In the full conversation section, assistant/model replies are reference-only and not skill evidence.

**Output Requirements:**
- For each step, include: action, checks, and failure rollback/fallback plan.
- Output format: For each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
