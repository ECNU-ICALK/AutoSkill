---
id: "e93dfd2f-d5d2-49d4-adf5-6940a95998df"
name: "family-property-claim-status-tracking-for-family"
description: "Generates a simplified, non-technical claim status tracking table designed for family members with no insurance expertise, using plain language, visual cues, and minimal jargon."
version: "0.1.0"
tags:
  - "insurance"
  - "accessibility"
  - "family"
  - "status-tracking"
  - "plain-language"
triggers:
  - "给家人看得懂的状态追踪表"
  - "理赔进度表家人版"
  - "老人能看懂的保险进度表"
  - "简单明了的理赔状态表"
---

# family-property-claim-status-tracking-for-family

Generates a simplified, non-technical claim status tracking table designed for family members with no insurance expertise, using plain language, visual cues, and minimal jargon.

## Prompt

# Goal
Generate a printable, family-friendly claim status tracking table that shows the current stage of a home property insurance claim — using only everyday language, clear icons, and zero insurance terminology (e.g., no 'subrogation', 'indemnity', or 'deductible').

# Constraints & Style
- Output must be a single Markdown table (no explanations, no headers beyond the table itself).
- Columns: **Stage**, **What It Means (in 1 short sentence)**, **Who’s Doing It**, **Last Updated**, **Next Step You Can Help With**.
- Rows limited to exactly these 5 stages: (1) Claim Reported, (2) Inspector Visited, (3) Estimate Sent, (4) Decision Made, (5) Money Arrived.
- All text must be understandable by a teenager or elderly relative — e.g., 'Inspector Visited' → 'Someone from the insurance company came to look at the damage'; 'Decision Made' → 'They said YES, NO, or PARTLY to paying for repairs'.
- Use only these status indicators: ✅ Done | ⏳ Waiting | ❓ Not Sure | 🚨 Needs Action.
- Never include dates, names, policy numbers, or case IDs — use placeholders like <DATE>, <NAME>, or omit entirely.
- No markdown formatting beyond basic table syntax; no bold/italics inside cells.
- Do not generate any accompanying instructions, tips, or footnotes — only the table.

# Workflow
None — this is a single-output transformation. Input is implicit: a home property insurance claim in progress.

## Triggers

- 给家人看得懂的状态追踪表
- 理赔进度表家人版
- 老人能看懂的保险进度表
- 简单明了的理赔状态表
