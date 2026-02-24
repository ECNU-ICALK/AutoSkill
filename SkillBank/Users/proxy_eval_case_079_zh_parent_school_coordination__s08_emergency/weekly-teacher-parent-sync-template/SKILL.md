---
id: "8fb54497-f4c1-4ff9-9bd6-3d0e1c9c9c97"
name: "weekly-teacher-parent-sync-template"
description: "A reusable, concise, and action-oriented communication template for weekly synchronization between parents and homeroom teachers—focused on observable progress, shared insights, and next-step alignment."
version: "0.1.0"
tags:
  - "communication"
  - "parent-teacher"
  - "progress-tracking"
  - "collaboration"
triggers:
  - "weekly teacher sync"
  - "parent-teacher update template"
  - "how to report home practice to teacher"
  - "share progress with班主任"
  - "coordinated feedback to homeroom teacher"
---

# weekly-teacher-parent-sync-template

A reusable, concise, and action-oriented communication template for weekly synchronization between parents and homeroom teachers—focused on observable progress, shared insights, and next-step alignment.

## Prompt

# Goal
Generate a brief (≤120-word), structured weekly sync message from parent to homeroom teacher that reports on the child’s home-based practice across three targeted areas (math foundation, reading fluency, English oral use), highlights one concrete observation per area, notes one collaborative insight or question, and ends with a clear, low-effort ask or confirmation.

# Constraints & Style
- Use neutral, strengths-based, non-diagnostic language (e.g., 'noticing more self-correction' not 'still struggling with regrouping')
- Avoid subjective labels ('lazy', 'shy', 'bad at'), vague praise ('tried hard'), or unsolicited advice
- Never include personal identifiers (child’s full name, school ID, classroom number) — use placeholders like <CHILD> or omit entirely
- Keep all examples de-identified: e.g., 'a grocery pricing task' not 'the apple juice at Safeway'
- Output only the message body — no greeting, signature, or metadata
- Maintain consistent 3-area framing: Math | Reading | English

# Workflow
1. Extract the three focus domains from user context (math薄弱 → 'math foundation'; 阅读慢 → 'reading fluency'; 英语口语需保持 → 'English oral use')
2. For each domain, generate one specific, time-bound, behaviorally anchored observation (e.g., 'used finger counting less this week when solving 2-digit + 1-digit sums')
3. Synthesize one cross-domain insight or open question (e.g., 'Noticed <CHILD> applies the same 'pause-and-repeat' strategy in English sentences and reading passages')
4. Close with one actionable, teacher-supported request (e.g., 'Could we align on one visual cue for 'check your work' both at home and in class?')

## Triggers

- weekly teacher sync
- parent-teacher update template
- how to report home practice to teacher
- share progress with班主任
- coordinated feedback to homeroom teacher
