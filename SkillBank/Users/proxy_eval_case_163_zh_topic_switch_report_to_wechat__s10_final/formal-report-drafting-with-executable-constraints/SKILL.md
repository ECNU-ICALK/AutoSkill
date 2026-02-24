---
id: "2e9291d1-78e5-40cf-acc2-987659245282"
name: "formal-report-drafting-with-executable-constraints"
description: "Generates formal, policy-aligned report drafts for public service contexts that are restrained in tone, structurally precise, and operationally actionable — avoiding speculation, visual formatting (e.g., tables, icons), rhetorical language, or unverifiable claims."
version: "0.1.1"
tags:
  - "report-drafting"
  - "policy-writing"
  - "public-sector"
  - "structured-output"
  - "tone-control"
  - "operational-planning"
triggers:
  - "写正式报告草案"
  - "要求正式克制可执行"
  - "不用表格写报告"
  - "生成政策级报告初稿"
  - "内部汇报材料需落地"
---

# formal-report-drafting-with-executable-constraints

Generates formal, policy-aligned report drafts for public service contexts that are restrained in tone, structurally precise, and operationally actionable — avoiding speculation, visual formatting (e.g., tables, icons), rhetorical language, or unverifiable claims.

## Prompt

# Goal
Produce a formal, internal-use report draft on a public-service or community development topic, optimized for clarity, authority, and implementability.

# Constraints & Style
- Tone must be formal and restrained: avoid adjectives implying judgment (e.g., 'urgent', 'critical', 'groundbreaking', 'innovative'), emotive phrasing, advocacy language, metaphors, narrative flourishes, or exclamation points; use neutral, evidence-grounded statements only.
- Structure strictly follows standard official report sections: Title, Header (unit/date/version), Background & Rationale, Current State Summary, Objectives, Actionable Recommendations, Coordination Needs, Conclusion; use only numbered/lettered hierarchical headings (e.g., 'I.', 'A.', '(1)') — no markdown syntax (no **bold**, no `---`, no emoji, no bullet symbols like • or ➤).
- Never use tables, charts, icons (🔹), or markdown-heavy formatting; express all comparisons, timelines, and metrics in prose with explicit units and baselines.
- All recommendations must be phrased as concrete, assignable actions specifying: (a) responsible actor (e.g., 'Community Health Center', 'Street Office'), (b) concrete action verb (e.g., 'launch', 'establish', 'submit'), (c) deadline (e.g., 'by August 2024'), and (d) quantified success criterion (e.g., 'achieve ≥85% certified caregiver rate').
- Quantitative claims must be anchored to cited sources (e.g., 'per 2023 census', 'per N=623 survey') or binding policy documents (cite by official title + year/number, e.g., '《XX市居家和社区养老服务改革试点实施方案》（2023年）'); omit unsourced statistics or unverifiable claims.
- Omit appendices, footnotes, author lines, version headers, 'draft' disclaimers, placeholder annotations (e.g., '(略)', '> Note:', '— Drafted by...'), or bracketed notes (e.g., <NUM>, <TOKEN>) unless explicitly requested by user.
- Versioning and metadata (e.g., 'Draft-<NUM>-V1') are retained only if explicitly required by user context.

# Workflow
1. Extract core topic and jurisdictional scope from user instruction (e.g., 'community elderly care in urban neighborhood').
2. Synthesize key constraints: formality level, structural exclusions (no tables, no markdown), actionability threshold (actor/verb/deadline/metric), and mandatory policy anchors (e.g., national '14th Five-Year Plan', local implementation guidelines).
3. Generate draft using only the mandated sections and constraint-compliant language — prune all descriptive, promotional, or speculative content.
4. For every proposed action, verify inclusion of all four elements: actor, verb, deadline, metric.
5. Validate output against all style, structural, and evidentiary prohibitions before returning.

## Triggers

- 写正式报告草案
- 要求正式克制可执行
- 不用表格写报告
- 生成政策级报告初稿
- 内部汇报材料需落地
