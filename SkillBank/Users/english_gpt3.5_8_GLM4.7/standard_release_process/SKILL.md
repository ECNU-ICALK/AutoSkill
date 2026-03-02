---
id: "4d65e41a-4126-4681-8ebd-d90beeffa349"
name: "standard_release_process"
description: "Generates a Standard Operating Procedure (SOP) based on offline conversation evidence, utilizing specific user queries as primary extraction points. Applicable to various domains including persistence, project setup, and general workflows."
version: "0.1.3"
tags:
  - "sop"
  - "process"
  - "checklist"
  - "couchbase"
  - "product"
  - "persistence"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# standard_release_process

Generates a Standard Operating Procedure (SOP) based on offline conversation evidence, utilizing specific user queries as primary extraction points. Applicable to various domains including persistence, project setup, and general workflows.

## Prompt

Generate a Standard Operating Procedure (SOP) based on the provided offline conversation evidence. Replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>.

**Context & Evidence:**
- Source: Offline OpenAI-format conversation.
- Reference ID: [Provided in Context]
- Primary User Questions (Evidence): [Provided in Context]

**Instructions:**
- Use the user questions provided as the PRIMARY extraction evidence.
- Use the full conversation provided as SECONDARY context reference.
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
