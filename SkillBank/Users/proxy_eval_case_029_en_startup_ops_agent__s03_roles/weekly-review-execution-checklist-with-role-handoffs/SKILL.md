---
id: "20191d1e-e6d8-49e0-afd0-41a910f697fe"
name: "weekly-review-execution-checklist-with-role-handoffs"
description: "A concise, role-anchored execution checklist for weekly leadership reviews, enforcing explicit ownership and handoff points between functional leads to prevent gaps in accountability."
version: "0.1.0"
tags:
  - "leadership"
  - "accountability"
  - "checklist"
  - "handoff"
  - "role-ownership"
triggers:
  - "add role ownership and handoffs to weekly checklist"
  - "make weekly review checklist role-specific"
  - "define handoff points for leadership checklists"
  - "concise owner-and-handoff checklist"
  - "explicit ownership weekly review"
---

# weekly-review-execution-checklist-with-role-handoffs

A concise, role-anchored execution checklist for weekly leadership reviews, enforcing explicit ownership and handoff points between functional leads to prevent gaps in accountability.

## Prompt

# Goal
Generate a concise, actionable weekly execution checklist for leadership reviews that assigns unambiguous role ownership for each action and defines clear handoff checkpoints (i.e., where one owner’s output becomes the next owner’s input).

# Constraints & Style
- Output must be strictly tabular (Markdown table), with columns: #, Action, Owner, Handoff Checkpoint, Done?
- "Handoff Checkpoint" must specify *exactly what artifact or signal* triggers the next step — e.g., "Pipeline table posted in Notion", "Runway <5.0 → Cost-Control Branch activated", "Top Issue mapped to release in Product backlog"
- No explanatory paragraphs, no bullet lists, no commentary — only the table
- Max 5 rows; prioritize actions that cross functional boundaries or carry escalation risk
- Use placeholder syntax for dynamic values: <RUNWAY_VALUE>, <NOTION_PAGE_LINK>, <RELEASE_BACKLOG_LINK>
- All roles must be generic leadership titles (e.g., 'CEO', 'Finance Lead', 'Product Lead') — no names, no team-specific titles like 'Talent Lead'
- Never invent new roles or responsibilities beyond those explicitly referenced in user feedback

# Workflow
None — this is a static, reusable checklist template. Do not add steps, automation logic, or conditional branches unless explicitly requested.

## Triggers

- add role ownership and handoffs to weekly checklist
- make weekly review checklist role-specific
- define handoff points for leadership checklists
- concise owner-and-handoff checklist
- explicit ownership weekly review
