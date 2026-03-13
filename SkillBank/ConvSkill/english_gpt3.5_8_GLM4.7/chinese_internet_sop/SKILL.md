---
id: "019aec84-073d-40d7-acd9-20817baf9de2"
name: "chinese_internet_sop"
description: "SOP for analyzing offline conversation logs to answer queries about Chinese internet accessibility, blocked sites, and browser popularity."
version: "0.1.1"
tags:
  - "http"
  - "com"
  - "browser"
  - "tencent"
  - "chinese"
  - "sop"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# chinese_internet_sop

SOP for analyzing offline conversation logs to answer queries about Chinese internet accessibility, blocked sites, and browser popularity.

## Prompt

Follow this SOP for analyzing offline OpenAI conversation sources (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION> or <SOURCE_ID>):
1) Identify the Offline OpenAI-format conversation source.
2) Title: Use the specific source ID (e.g., <SOURCE_ID>).
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (Evidence Scope):
   - Links and names blocked in China (e.g., YouTube).
   - Requests for more information ("give me more").
   - Specific browser inquiries (e.g., Tencent Browser, QQ Browser).
   - Origin verification (e.g., "is this from Taiwan?").
   - Popularity and ranking in China.

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
