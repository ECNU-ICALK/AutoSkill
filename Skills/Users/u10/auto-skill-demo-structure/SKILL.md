---
id: "705cf559-317a-4b77-92ed-b8b61720dcee"
name: "auto-skill-demo-structure"
description: "A reusable skill that structures AutoSkill documentation into three concise, purpose-driven parts: (1) Skill Extraction, (2) Skill Update, and (3) Skill Reuse — each explained in 2–3 sentences highlighting its functional role and practical advantage."
version: "0.1.0"
tags:
  - "demo"
  - "skill-lifecycle"
  - "documentation"
  - "concise-output"
triggers:
  - "把三部分合成一个简洁版本"
  - "说明每个部分的作用和优势"
  - "写一个AutoSkill演示的精简说明"
  - "三个阶段各用两三句话讲清楚"
---

# auto-skill-demo-structure

A reusable skill that structures AutoSkill documentation into three concise, purpose-driven parts: (1) Skill Extraction, (2) Skill Update, and (3) Skill Reuse — each explained in 2–3 sentences highlighting its functional role and practical advantage.

## Prompt

# Goal
Generate a compact, self-contained AutoSkill demo version that unifies the three core lifecycle phases — extraction, update, and reuse — into one coherent narrative, with each phase described in 2–3 clear, benefit-focused sentences.

# Constraints & Style
- Use plain, professional Chinese (no markdown formatting, no bullet points, no emojis, no code blocks).
- Each part must be exactly 2–3 sentences long.
- Explicitly state *what the part does* and *why it matters* (i.e., its functional purpose and user advantage).
- Do not include implementation details (e.g., `v0.1.0`, `SKILL.md`, CLI commands) or project-specific names (e.g., "ICALK", "华东师范大学").
- Do not use decorative symbols, asterisks, arrows, or numbered lists — strictly avoid all visual flourishes.
- Maintain consistent terminology: use '技能抽取'、'技能更新'、'技能复用' as fixed phase names.
- Never invent new capabilities; reflect only the three-phase logic confirmed by user’s sequential requests.

# Workflow
None — this is a structural summarization task, not a multi-step operation. The output format is purely declarative and linear.

## Triggers

- 把三部分合成一个简洁版本
- 说明每个部分的作用和优势
- 写一个AutoSkill演示的精简说明
- 三个阶段各用两三句话讲清楚
