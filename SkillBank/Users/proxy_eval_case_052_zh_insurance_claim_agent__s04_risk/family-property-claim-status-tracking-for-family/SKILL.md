---
id: "c89eb9c4-7a49-41ae-8533-a322fe3b03e6"
name: "family-property-claim-status-tracking-for-family"
description: "A reusable, non-technical status tracking table for household property insurance claims, designed to be understood by all family members — no insurance or legal jargon, clear visual cues, and minimal required input."
version: "0.1.0"
tags:
  - "claim-tracking"
  - "family-communication"
  - "accessibility"
  - "simplified-output"
triggers:
  - "给家人看得懂的状态追踪表"
  - "让老人也能看懂的理赔进度表"
  - "家庭成员共享的理赔进展表"
  - "简化版理赔跟踪表"
  - "非专业人士能用的索赔进度表"
---

# family-property-claim-status-tracking-for-family

A reusable, non-technical status tracking table for household property insurance claims, designed to be understood by all family members — no insurance or legal jargon, clear visual cues, and minimal required input.

## Prompt

# Goal
Generate a simple, printable, one-page claim status tracking table that any family member (including elderly or non-insurance-literate members) can read, update, and understand at a glance — showing where the claim stands, what’s done, what’s next, and who’s responsible.

# Constraints & Style
• Language: Plain, conversational Chinese — avoid terms like "定损", "查勘", "复核", "免责条款"; use equivalents like "保险公司来看现场了吗？", "赔多少钱定下来了吗？", "还需要我们做什么？"
• Structure: Table with exactly 5 rows and 4 columns:
  - Row headers (leftmost column): "当前阶段", "已完成", "下一步", "谁来办/截止日";
  - Column headers (top row): "状态", "证据/动作", "待办事项", "负责人 & 时间";
• Visual clarity:
  - Use ✅ for completed items, ⏳ for in-progress, ❌ for blocked, ? for unclear;
  - Highlight urgent deadlines in **bold red** (e.g., "**9月10日前**");
  - No dates without context — always pair with relative phrasing (e.g., "报案后第3天", "收到拒赔通知起30天内");
• Input-agnostic: Accept only minimal inputs — e.g., {"stage": "等待定损", "evidence_uploaded": ["现场照片", "物业说明"], "next_step": "等保险公司发赔偿清单", "owner_deadline": "张女士｜9月12日前"}; do not require policy numbers, legal citations, or insurer names.
• Output: Pure Markdown table only — no explanations, no headers beyond the table, no footnotes.
• De-identify: Never include real names, addresses, phone numbers, policy numbers, or insurer names — use placeholders like <家人姓名>, <出险类型>.

# Workflow
None — this is a single-step table generation. Do not add steps, instructions, or guidance. Output only the table.

## Triggers

- 给家人看得懂的状态追踪表
- 让老人也能看懂的理赔进度表
- 家庭成员共享的理赔进展表
- 简化版理赔跟踪表
- 非专业人士能用的索赔进度表
