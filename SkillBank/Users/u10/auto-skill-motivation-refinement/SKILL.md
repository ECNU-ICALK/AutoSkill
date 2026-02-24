---
id: "82db3712-2af8-4f44-805c-dd63bf8f3b7c"
name: "auto-skill-motivation-refinement"
description: "Refines the motivation/introduction section of AutoSkill's official communication (e.g., WeChat official account post, README, pitch deck) by preserving original logic, factual grounding, and technical terminology while enhancing clarity, concision, rhythm, and professional Chinese expression — strictly without introducing new claims, structural changes, or subjective marketing language."
version: "0.1.1"
tags:
  - "motivation"
  - "refinement"
  - "chinese"
  - "technical-writing"
  - "auto-skill"
  - "technical-communication"
triggers:
  - "优化动机介绍"
  - "润色项目引言"
  - "精炼AutoSkill开场段"
  - "保持原意改写介绍"
  - "优化公众号动机介绍"
  - "润色技术产品开场白"
  - "改写项目背景段落"
---

# auto-skill-motivation-refinement

Refines the motivation/introduction section of AutoSkill's official communication (e.g., WeChat official account post, README, pitch deck) by preserving original logic, factual grounding, and technical terminology while enhancing clarity, concision, rhythm, and professional Chinese expression — strictly without introducing new claims, structural changes, or subjective marketing language.

## Prompt

# Goal
Refine the provided motivation/introduction paragraph for AutoSkill’s public-facing materials (e.g., WeChat official account post), keeping all core technical facts, logical flow, and key terminology intact. Improve readability, sentence rhythm, and formal yet natural Chinese expression — *no new information, no conceptual additions, no structural reordering beyond sentence-level polishing*.

# Constraints & Style
- Preserve all original technical content: 'Experience-driven Lifelong Learning (ELL)', 'skill self-evolution', 'dialogue + behavior/interaction as experience source', 'SKILL.md format', 'versioned skills', 'no manual prompt engineering', 'human-readable/machine-parsable/migration-ready'.
- Retain exact constraint examples: '不得虚构信息', '须采用政府公文表述规范', '不要使用过于技术和浮夸的表达'.
- Keep all project-specific terms unchanged: 'AutoSkill', 'XXX联合XXX' (as placeholder — do not replace), 'SKILL.md', 'ELL'.
- First occurrence of acronyms must use full name + parentheses: e.g., '经验驱动终身学习（Experience-driven Lifelong Learning, ELL）'.
- Version identifiers must retain exact format: e.g., 'v0.1.0 → v0.1.1'.
- File names must appear in code font: 'SKILL.md'.
- Remove redundancy (e.g., repeated 'experience'), tighten verbose phrasing (e.g., '高频交互产生的有效经验无法结构化沉淀' → '高频交互中积累的有效经验难以结构化沉淀'), fix minor grammatical hiccups (e.g., subject–verb agreement, punctuation consistency).
- Use formal, concise, natural Chinese; avoid marketing fluff, subjective adjectives ('smart', 'brilliant', 'revolutionary'), or promotional terms ('花哨', '炫技', '亮点', '重磅').
- Do NOT add explanations, analogies, examples, comparative claims, bullet points, emoji, decorative punctuation (——, …, ※), or formatting (bold/italic).
- Output only the refined paragraph — no headings, no markdown, no commentary, no empty lines.
- Maintain original line breaks only where semantically necessary (e.g., before 'Github:' line).

## Triggers

- 优化动机介绍
- 润色项目引言
- 精炼AutoSkill开场段
- 保持原意改写介绍
- 优化公众号动机介绍
- 润色技术产品开场白
- 改写项目背景段落
