---
id: "92a5296d-b15d-4373-9f4d-2066edeaac43"
name: "dynamic-study-plan-adjustment-by-mock-scores"
description: "A reusable skill for adjusting study plans based on biweekly mock exam performance, triggering targeted interventions when progress stalls or objective thresholds are breached, and proactively identifying and mitigating the top three exam-specific risks."
version: "0.1.2"
tags:
  - "exam-prep"
  - "adaptive-planning"
  - "error-analysis"
  - "study-optimization"
  - "data-driven-adjustment"
  - "risk-mitigation"
triggers:
  - "每两周根据模考分数调整重点"
  - "连续停滞时切到错题类型专项"
  - "模考后动态优化学习重点"
  - "补充前三大风险和对应预案"
  - "识别模考暴露的最高危短板"
---

# dynamic-study-plan-adjustment-by-mock-scores

A reusable skill for adjusting study plans based on biweekly mock exam performance, triggering targeted interventions when progress stalls or objective thresholds are breached, and proactively identifying and mitigating the top three exam-specific risks.

## Prompt

# Goal
Adapt a multi-week exam preparation plan in real time by analyzing biweekly mock exam results and applying predefined, evidence-based adjustments to focus areas, task allocation, and practice intensity — while simultaneously identifying the top 3 concrete, observable risks impeding exam success and generating one-sentence, executable mitigation actions for each.

# Constraints & Style
- Must trigger adjustment every two weeks strictly on mock exam results — no ad-hoc changes without score data.
- Use three objective, quantifiable triggers: (1) module score <65%, (2) question-type loss rate >30% of total points, (3) time overrun >15 min/section. When any is met, increase time allocation to the affected area by ≥40% and pair it with a validated intervention (e.g., '错题类型专项攻坚', '记忆-提取双轨训练', '元能力修复包').
- When overall progress stalls (e.g., two consecutive mocks show ≤±3% change in any metric OR ≤2% improvement in total score OR no improvement in ≥2 core modules), automatically shift focus to **error-type专项 (type-specific) remediation**, not topic-based review.
- Error-type specialization means grouping past mistakes by cognitive pattern (e.g., 'misapplied formula', 'misread question stem', 'time-pressure omission', 'concept conflation') — not by subject or chapter.
- Do not introduce new content during stall recovery; restrict activity to reworking *previously attempted* items classified under the dominant error type.
- Preserve all original time budgets (e.g., 90 min workday / 4 hr weekend); redistribute only *within* those blocks to prioritize error-type drills.
- All outputs must be actionable within 30 minutes: include concrete duration shifts, named intervention types, and reference-ready tool names (e.g., '《错题类型作战卡》', '《应试肌肉记忆训练表》').
- In parallel, identify the top 3 observable, domain-agnostic risks (e.g., 'conceptual fragility in X module', 'procedural slowness on Y task', 'metacognitive misalignment in Z context') — never vague or unmeasurable — and generate exactly one concise, behavioral, immediate action per risk (e.g., 'Switch to timed single-problem drills for 5 min/day'), with no explanations, markdown, or external references.
- Never invent thresholds, metrics, tools, or content not explicitly endorsed by user; only reuse those confirmed in dialogue (e.g., '连续停滞', '错题类型专项', '模考分数调整重点').
- Output language must match user’s: Chinese, imperative, concise, no markdown in delivered artifacts.

# Workflow
1. After each biweekly mock exam, compute delta scores per module and error-type frequency distribution from prior attempts; collect raw scores per module and question type, plus timing data.
2. If stagnation is detected (two mocks with ≤±3% metric change OR ≤2% net gain OR no gain in ≥2 modules), activate stall protocol.
3. Identify dominant error type across the last 15–20 incorrect items.
4. Replace next scheduled content-learning block(s) with a fixed-duration, high-density drill targeting that error type.
5. Exit the专项 phase only upon achieving ≥85% accuracy on 10 newly generated items matching the same error pattern.

## Triggers

- 每两周根据模考分数调整重点
- 连续停滞时切到错题类型专项
- 模考后动态优化学习重点
- 补充前三大风险和对应预案
- 识别模考暴露的最高危短板
