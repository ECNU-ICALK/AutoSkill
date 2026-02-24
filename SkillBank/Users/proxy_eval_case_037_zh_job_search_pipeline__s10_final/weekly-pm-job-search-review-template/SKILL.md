---
id: "18e4da5f-9bbe-4e17-ae46-9eb762b01ef3"
name: "weekly-pm-job-search-review-template"
description: "A lightweight, time-boxed weekly review template for PM job seekers, designed to track reply rate, optimize outreach messaging, and build authentic professional relationships — with built-in red-flag detection and concrete next-step actions."
version: "0.1.0"
tags:
  - "pm-job-search"
  - "outreach-analytics"
  - "lightweight-review"
  - "action-oriented"
triggers:
  - "每周复盘模板"
  - "PM求职复盘"
  - "内推效果追踪"
  - "reply rate review"
  - "job search weekly check"
---

# weekly-pm-job-search-review-template

A lightweight, time-boxed weekly review template for PM job seekers, designed to track reply rate, optimize outreach messaging, and build authentic professional relationships — with built-in red-flag detection and concrete next-step actions.

## Prompt

# Goal
Generate a weekly PM job search review template that enables the user to assess progress in three critical dimensions — reply rate, message effectiveness, and relationship depth — and derive ≤3 executable next actions. Output must be strictly fill-in-the-blank (numbers/short keywords only), include automatic reply-rate calculation, and trigger diagnostic workflow when reply rate < 8%.

# Constraints & Style
- Format: Markdown table with exactly three rows: '📌 Reply Rate Tracking', '💬 Message Optimization', '🤝 Relationship Building'
- Each row has three columns: 'This Week', 'Key Insight (1 sentence)', 'Next Actions (≤3 items, each ≤10 words, imperative verb, no fluff)'
- All numeric fields use blank underscores (e.g., '______') — no explanations or units in blanks
- Reply rate calculation must be explicit: `已回复 ÷ 发送总数 × 100%`
- Red-flag behavior: if calculated reply rate < 8%, the entire '📌 Reply Rate Tracking' row must be marked for diagnostic workflow activation (no description needed — just enable downstream logic)
- No prose, no examples, no instructions — only the template itself
- Language: Chinese

# Workflow
None — this is a static, reusable template; no AI execution steps required.

## Triggers

- 每周复盘模板
- PM求职复盘
- 内推效果追踪
- reply rate review
- job search weekly check
