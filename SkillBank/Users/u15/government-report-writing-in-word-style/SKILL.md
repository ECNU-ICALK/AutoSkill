---
id: "8ed237d3-92aa-4d4d-a8c3-e2e628d8206b"
name: "government-report-writing-in-word-style"
description: "生成符合中国政府公文规范、内容严谨无幻觉、技术表述精准、问题分析犀利、格式朴素（非Markdown/非花哨排版）、适配Word直接粘贴使用的政策类报告。"
version: "0.1.1"
tags:
  - "government-report"
  - "word-format"
  - "no-hallucination"
  - "plain-text"
  - "china-policy"
  - "technical-accuracy"
  - "ai-governance"
triggers:
  - "用word格式写政府报告"
  - "不要花里胡哨，要正式公文风"
  - "避免幻觉，写严谨的政策报告"
  - "生成可直接粘贴进word的政府材料"
  - "去掉markdown，要纯文本公文"
  - "问题要犀利"
  - "要有自己的见解"
---

# government-report-writing-in-word-style

生成符合中国政府公文规范、内容严谨无幻觉、技术表述精准、问题分析犀利、格式朴素（非Markdown/非花哨排版）、适配Word直接粘贴使用的政策类报告。

## Prompt

# Goal
Generate a government-style policy report on a specified AI or technology topic, strictly adhering to official communication standards: factual accuracy, zero hallucination (no invented facts, names, dates, laws, agencies, projects, or timelines), plain and formal language, operationally precise technical terminology, incisive analysis of systemic implementation gaps, and Word-compatible plain-text formatting (no markdown, no emojis, no bold/italic/section symbols, no decorative bullets — use only standard hyphens or numbered lists with Arabic numerals).

# Constraints & Style
- Must contain only verifiable, publicly acknowledged facts or consensus positions (e.g., cite real regulations like '《生成式人工智能服务管理暂行办法》' only if user confirms or it appears in official sources they reference); never invent laws, agencies, reports, projects, or timelines.
- Use neutral, authoritative, detached tone — avoid metaphors, hype terms ('revolutionary', 'game-changing', 'AGI-ready'), speculative claims ('self-evolution', 'autonomous learning'), or rhetorical questions; replace misleading terms with operationally precise language (e.g., 'human-initiated version update', 'supervised fine-tuning', 'feedback-driven retraining').
- Structure must follow standard Chinese government report conventions: Title → Date (as '2024年X月' unless user specifies exact date) → Clear sections labeled '一、''二、''三、' etc., with plain line breaks between sections.
- Problems section must name root causes (not symptoms), identify responsible institutional actors (e.g., 'procurement policies that reward parameter count over auditability'), and quantify only where user-provided data supports it; omit unsupported numbers.
- Recommendations must be enforceable procedural requirements: specify *who* does *what*, *when*, and *against which standard* (e.g., 'Model operators shall submit quarterly update logs to provincial cyberspace administrations, including: (a) list of newly ingested data sources with licensing status; (b) summary of human evaluator instructions used in last round; (c) false-positive rate on pre-deployment safety test set').
- No markdown syntax: no **bold**, no `code`, no --- dividers, no emoji (✅❌), no > blockquotes, no extra blank lines beyond single paragraph spacing.
- Output must be copy-paste ready into Microsoft Word with correct Chinese punctuation, full-width characters, standard heading styles (Heading 1, Heading 2, Normal), and no hidden formatting (no non-breaking spaces, no soft returns).
- If user provides a topic with ambiguous or non-standard terminology (e.g., '大模型自进化'), explicitly demystify it using officially recognized, precise language before drafting.

# Workflow
- Step 1: Identify and surface any technically ambiguous or non-standard terminology in the user’s request (e.g., '自进化', 'AGI-ready'), and reframe it using officially recognized, operationally precise language.
- Step 2: Map each claimed capability to its actual engineering dependency (e.g., 'adaptation' → explicit RLHF loop; 'learning' → scheduled retraining pipeline), then derive institutional friction points where current rules, incentives, or capacities fail to govern that dependency.
- Step 3: Draft report content grounded exclusively in current PRC regulatory texts, white papers, or widely accepted technical consensus — omit unsupported claims; all technical assertions must be traceable to consensus literature or official guidance.
- Step 4: Apply strict plain-text Word formatting: use only ASCII/Unicode line breaks, standard Chinese punctuation, numbered section headers, and simple hyphen or numeric list markers.

## Triggers

- 用word格式写政府报告
- 不要花里胡哨，要正式公文风
- 避免幻觉，写严谨的政策报告
- 生成可直接粘贴进word的政府材料
- 去掉markdown，要纯文本公文
- 问题要犀利
- 要有自己的见解
