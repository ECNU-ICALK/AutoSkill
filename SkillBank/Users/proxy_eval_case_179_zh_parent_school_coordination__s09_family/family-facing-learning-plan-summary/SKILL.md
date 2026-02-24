---
id: "6c8a347f-9c28-4a02-860b-98dd27027d77"
name: "family-facing-learning-plan-summary"
description: "Generates a concise, non-technical summary of a multi-week learning plan for family members who support the learner, prioritizing clarity, emotional safety, and actionable roles over academic detail."
version: "0.1.0"
tags:
  - "family-communication"
  - "simplification"
  - "caregiver-support"
triggers:
  - "给家人看的简版计划"
  - "让爸妈/爷爷奶奶也能看懂的版本"
  - "不讲方法只讲作用的说明"
  - "去掉专业词，说人话"
---

# family-facing-learning-plan-summary

Generates a concise, non-technical summary of a multi-week learning plan for family members who support the learner, prioritizing clarity, emotional safety, and actionable roles over academic detail.

## Prompt

# Goal
Produce a one-page, plain-language overview of a structured learning plan — designed for caregivers (not educators) — that explains: what the plan is for, why those three focus areas matter, what the child does each week in simple terms, what the caregiver’s role is (with time bounds), and how progress is noticed — all without jargon, metrics, or instructional detail.

# Constraints & Style
- Use only everyday vocabulary; avoid terms like "metacognition", "scaffolding", "B1 level", "differentiation".
- Never mention time allocations (e.g., "1.5h/day") or technical tools (e.g., "three-color pen", "graded reading pack").
- Replace all subject-specific strategies with their *human purpose*: e.g., "math breathing card" → "a quick, calming math moment"; "sound map" → "listening game to wake up thinking".
- Omit all references to teachers, classrooms, or school systems — frame everything as home-based support.
- Keep total length under 250 words; use bullet points and emoji sparingly for visual anchoring only.
- Do not include examples, templates, or attachments — this is a standalone explanatory note.
- Output in the same language as the user’s request (here: Chinese).

## Triggers

- 给家人看的简版计划
- 让爸妈/爷爷奶奶也能看懂的版本
- 不讲方法只讲作用的说明
- 去掉专业词，说人话
