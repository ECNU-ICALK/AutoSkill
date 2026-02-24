---
id: "35a5eaa9-e5de-48ff-a77e-645bb9dd91ef"
name: "formal-report-drafting-with-executable-structure"
description: "Generates formal, policy-ready report drafts that prioritize clarity, restraint, and operational feasibility—avoiding decorative formatting (e.g., tables, markdown-heavy layouts) in favor of linear, prose-based sections with explicit action logic."
version: "0.1.1"
tags:
  - "report-drafting"
  - "policy-writing"
  - "public-service"
  - "executability"
  - "formal-tone"
  - "accountability"
  - "metrics"
triggers:
  - "写一份正式报告草案"
  - "生成可执行的政策报告"
  - "起草克制风格的内部汇报稿"
  - "需要正式、不花哨的方案文档"
  - "避免表格和格式化，只用文字表达"
---

# formal-report-drafting-with-executable-structure

Generates formal, policy-ready report drafts that prioritize clarity, restraint, and operational feasibility—avoiding decorative formatting (e.g., tables, markdown-heavy layouts) in favor of linear, prose-based sections with explicit action logic.

## Prompt

# Goal
Produce a formal, internal-use report draft on a public service or community policy topic, structured for immediate review and implementation planning. Output must be fully self-contained, prose-only, and omit all non-prose elements (no tables, no markdown syntax beyond section headers, no placeholder tokens like <TOKEN> or <NUM>).

# Constraints & Style
- Tone: formal, neutral, and institutionally credible—no rhetorical flourishes, emotive language, speculative claims, metaphors, or narrative framing.
- Structure: use only hierarchical heading levels (###, ####) and plain-paragraph body text; no bullet lists, numbered steps, inline formatting (e.g., bold/italics), or tabular data—replace tables with concise, integrated narrative summaries (e.g., 'X% of users reported Y').
- Content discipline: every claim must be grounded in observable conditions or documented constraints; avoid hypotheticals, analogies, comparative case references (e.g., no 'Tokyo杉并区', 'Shanghai Changning'), or invented policy names, standards, or regulations.
- Executability focus: all recommendations must specify *who does what, by when, and how it is verified*—e.g., 'Revise the service provider evaluation framework to include response time and data integration metrics, effective Q3 2024, validated via quarterly audit reports.' Each measure must include: (1) a named responsible party (e.g., 'Community Service Center', 'Joint Working Group'), (2) a hard deadline (e.g., 'by 2024-09-30' or 'Q3 2024'), and (3) a quantified, observable, time-bound deliverable (e.g., 'completion of baseline assessment for 100% of registered seniors', 'reduce average response time to ≤24 hours').
- Prohibit: tables, charts, appendices, footnotes, citations, version metadata, external URLs, emails, or any content requiring external interpretation or rendering support. Omit citations unless explicitly required; if cited, use only standard identifiers (e.g., 'per MZ/T 039—2019').

# Workflow
1. Identify the core service domain and its current operational gap (e.g., 'community elderly care delivery').
2. State the gap using verifiable indicators (e.g., 'service uptake below 60%', 'response latency exceeding 24 hours').
3. Propose concrete, role-assignable interventions—each tied to an accountable actor, measurable outcome, and verification method.
4. Sequence interventions into a phased rollout with calendar-defined milestones and success criteria.
5. Conclude with a single-sentence statement of implementation readiness—not vision, not values, but confirmation of next-step executability.
6. End with a minimal, standardized attachment note (e.g., 'Attachments (issued separately): [list]') — no inline appendix content.

## Triggers

- 写一份正式报告草案
- 生成可执行的政策报告
- 起草克制风格的内部汇报稿
- 需要正式、不花哨的方案文档
- 避免表格和格式化，只用文字表达
