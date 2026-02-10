---
id: "f7be2418-cc45-4f59-aba2-dabb03092232"
name: "skill-reuse-on-intent-match"
description: "Automatically retrieve and apply the latest version of a standardized skill when a new user request matches its documented intent, ensuring consistent, up-to-date behavior without manual selection."
version: "0.1.0"
tags:
  - "skill-reuse"
  - "version-aware-execution"
  - "intent-matching"
  - "auto-invocation"
triggers:
  - "调用最新版技能处理类似请求"
  - "复用已有的标准化技能"
  - "根据意图自动匹配并执行技能"
  - "使用vN.N.N版本技能生成响应"
  - "技能自动加载"
---

# skill-reuse-on-intent-match

Automatically retrieve and apply the latest version of a standardized skill when a new user request matches its documented intent, ensuring consistent, up-to-date behavior without manual selection.

## Prompt

# Goal
Given a new user request that semantically matches an existing skill’s documented intent (e.g., 'write a science communication article for parents'), automatically invoke the most recent version of that skill (e.g., `科普写作技巧/v0.1.1`) to generate the response — preserving all its constraints, structure rules, and versioned logic.

# Constraints & Style
- Must match intent *only* — not surface keywords; rely on semantic alignment with the skill’s documented purpose, audience, and output contract (e.g., '面向中学生家长的科普公众号文章').
- Must always select the **latest non-deprecated version** (e.g., `v0.1.1`, not `v0.1.0`) unless explicitly overridden by user instruction.
- Must not re-extract or re-generate the skill; must load and execute the pre-validated, versioned `SKILL.md` module as-is.
- Output must reflect *all* constraints in the invoked skill: e.g., if `v0.1.1` requires 'no technical terms + life analogies + real case + action suggestion', all four must appear.
- Must not invent new constraints, examples, or structure beyond what is declared in the loaded skill’s metadata and description.
- Must preserve human-readable fidelity: avoid markdown artifacts, placeholder syntax, or machine-only formatting (e.g., no `<!-- v0.1.1 -->` comments in output).

# Workflow
- Step 1: Parse user request to infer high-level task intent and target audience.
- Step 2: Query local skill registry for skills whose documented purpose semantically aligns with that intent.
- Step 3: Among matching skills, select the one with the highest non-deprecated version number.
- Step 4: Load its `SKILL.md` content, extract constraints, structure rules, and validation criteria.
- Step 5: Generate response strictly adhering to the loaded skill’s specification — no deviation, no interpolation, no fallback to generic behavior.

## Triggers

- 调用最新版技能处理类似请求
- 复用已有的标准化技能
- 根据意图自动匹配并执行技能
- 使用vN.N.N版本技能生成响应
- 技能自动加载
