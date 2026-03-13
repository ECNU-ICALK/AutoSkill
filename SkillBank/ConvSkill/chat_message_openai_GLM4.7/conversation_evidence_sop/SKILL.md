---
id: "c8e810ce-b050-4d38-84ad-49a1e4c0d065"
name: "conversation_evidence_sop"
description: "Standard operating procedure for extracting and structuring evidence from OpenAI-format conversations, distinguishing primary user intent from secondary context, including handling code snippets and multilingual queries."
version: "0.1.3"
tags:
  - "conversation"
  - "evidence"
  - "sop"
  - "extraction"
  - "openai-format"
  - "code"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
  - "Extract steps from a conversation log."
examples:
  - input: "Break this into best-practice, executable steps."
---

# conversation_evidence_sop

Standard operating procedure for extracting and structuring evidence from OpenAI-format conversations, distinguishing primary user intent from secondary context, including handling code snippets and multilingual queries.

## Prompt

# Role & Objective
Follow this SOP to process OpenAI-format conversation sources. Replace specific details with placeholders like <PROJECT>/<ENV>/<VERSION>.

# Constraints & Style
- **Primary Evidence**: Use the user questions below as the PRIMARY extraction evidence.
- **Secondary Context**: Use the full conversation below as SECONDARY context reference.
- **Reference Only**: In the full conversation section, assistant/model replies are reference-only and not skill evidence.
- **Step Detail**: For each step, include: action, checks, and failure rollback/fallback plan.

# Core Workflow
1) Identify the Offline OpenAI-format conversation source.
2) Extract the Title (e.g., <UUID>.json#conv_1).
3) Extract Primary User Questions (main evidence).
4) Review Full Conversation (context reference).

# Output Format
For each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.
- Extract steps from a conversation log.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
