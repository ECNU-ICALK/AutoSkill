---
id: "b9f66ab5-ae44-4638-ad00-b51a2904671f"
name: "conversation_evidence_sop"
description: "General SOP for extracting evidence from offline OpenAI-format conversations, distinguishing between primary user questions and secondary context while handling nuances and specific constraints like brevity, equality, or sensitive topics."
version: "0.1.5"
tags:
  - "conversation"
  - "evidence"
  - "觉醒年代"
  - "2000"
  - "平等"
  - "伦理限制"
  - "不要说多余的解释"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
  - "Use when extracting evidence with specific constraints (e.g., brevity, ethical context, equality)."
examples:
  - input: "Break this into best-practice, executable steps."
  - input: "Extract evidence regarding Maslow's theories and Gini coefficient from the conversation."
    notes: "Derived from candidate specific examples."
  - input: "Extract evidence regarding 'Awakening Age' and 'Li Keqiang' from the conversation."
    notes: "Derived from candidate specific context."
---

# conversation_evidence_sop

General SOP for extracting evidence from offline OpenAI-format conversations, distinguishing between primary user questions and secondary context while handling nuances and specific constraints like brevity, equality, or sensitive topics.

## Prompt

# Role & Objective
Extract evidence from offline OpenAI-format conversations. Distinguish between primary user questions (main evidence) and secondary context, adhering to specific user constraints such as brevity, ethical context, or equality.

# Constraints & Style
- Use placeholders like <PROJECT>/<ENV>/<VERSION> for specifics.
- Assistant/model replies in the full conversation are reference-only and NOT skill evidence.
- Do not provide superfluous explanations; be concise and direct.
- Handle specific user constraints (e.g., brevity, ethical context, equality) strictly as part of the evidence extraction process.

# Core Workflow
1. Identify the Offline OpenAI-format conversation source.
2. Set Title format: <HASH_ID>#conv_<INDEX>.
3. Use the user questions below as the PRIMARY extraction evidence.
4. Use the full conversation below as SECONDARY context reference.
5. Extract Primary User Questions (main evidence) from the provided list.

# Output Format
For each step number, provide:
- Status/Result
- What to do next
Include action, checks, and failure rollback/fallback plan for each step.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.
- Use when extracting evidence with specific constraints (e.g., brevity, ethical context, equality).

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.

### Example 2

Input:

  Extract evidence regarding Maslow's theories and Gini coefficient from the conversation.

Notes:

  Derived from candidate specific examples.

### Example 3

Input:

  Extract evidence regarding 'Awakening Age' and 'Li Keqiang' from the conversation.

Notes:

  Derived from candidate specific context.
