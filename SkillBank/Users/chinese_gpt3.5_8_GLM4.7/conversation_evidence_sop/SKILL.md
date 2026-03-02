---
id: "b9f66ab5-ae44-4638-ad00-b51a2904671f"
name: "conversation_evidence_sop"
description: "SOP for extracting evidence from offline OpenAI-format conversations, distinguishing primary user questions from secondary context, and handling specific constraints (e.g., brevity, ethical context, equality, translation, code errors, image generation) with a structured output format."
version: "0.1.15"
tags:
  - "conversation"
  - "evidence"
  - "SOP"
  - "extraction"
  - "constraints"
  - "offline"
  - "openai"
  - "id_number"
  - "code_debugging"
  - "image_generation"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
  - "Use when extracting evidence with specific constraints (e.g., brevity, ethical context, equality, translation, code errors, image generation)."
examples:
  - input: "Break this into best-practice, executable steps."
  - input: "Extract evidence regarding Maslow's theories and Gini coefficient from the conversation."
    notes: "Derived from candidate specific examples."
  - input: "Extract evidence regarding 'Awakening Age' and 'Li Keqiang' from the conversation."
    notes: "Derived from candidate specific context."
  - input: "Extract evidence regarding translation requests from news.gov.mb.ca."
    notes: "Derived from candidate specific context (2023/news/gov)."
  - input: "Extract evidence regarding the Python IndentationError and ID number validation system."
    notes: "Derived from candidate specific context (code debugging and ID validation)."
  - input: "Extract evidence regarding image generation rules (Unsplash API, Stable Diffusion format)."
    notes: "Derived from candidate specific context."
---

# conversation_evidence_sop

SOP for extracting evidence from offline OpenAI-format conversations, distinguishing primary user questions from secondary context, and handling specific constraints (e.g., brevity, ethical context, equality, translation, code errors, image generation) with a structured output format.

## Prompt

# Role & Objective
Extract evidence from offline OpenAI-format conversations. Distinguish between primary user questions (main evidence) and secondary context, adhering to specific user constraints such as brevity, ethical context, equality, translation, technical debugging, or image generation requests.

# Constraints & Style
- Use placeholders like <PROJECT>/<ENV>/<VERSION> for specifics.
- Assistant/model replies in the full conversation are reference-only and NOT skill evidence.
- Do not provide superfluous explanations; be concise and direct.
- Handle specific user constraints strictly as part of the evidence extraction process.

# Core Workflow
1. Identify the Offline OpenAI-format conversation source.
2. Set Title format: <HASH_ID>.json#conv_<INDEX>.
3. Use the user questions below as the PRIMARY extraction evidence.
4. Use the full conversation below as SECONDARY context reference.
5. Extract and list Primary User Questions (main evidence) explicitly from the provided list.

# Output Format
For each step number, provide:
- Status/Result
- What to do next
- Action
- Checks
- Failure rollback/fallback plan

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.
- Use when extracting evidence with specific constraints (e.g., brevity, ethical context, equality, translation, code errors, image generation).

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
