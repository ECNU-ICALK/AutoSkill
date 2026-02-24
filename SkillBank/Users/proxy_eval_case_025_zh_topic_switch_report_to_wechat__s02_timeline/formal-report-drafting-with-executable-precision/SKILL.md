---
id: "d8ff9d41-3b91-4f1a-9442-92ea08833964"
name: "formal-report-drafting-with-executable-precision"
description: "Generates formal, policy-adjacent report drafts for municipal or frontline governance stakeholders—prioritizing structural clarity, operational specificity, institutional tone, and built-in execution logic: every recommendation must name a responsible actor, specify an observable action, and define a time-bound or measurable outcome."
version: "0.1.1"
tags:
  - "report-drafting"
  - "policy-writing"
  - "government-communication"
  - "operational-clarity"
  - "accountability-design"
  - "metric-driven"
triggers:
  - "写一份正式报告草案"
  - "生成可执行的政策建议报告"
  - "起草克制、无修饰的政务文书"
  - "输出不带表格的正式工作汇报"
  - "撰写面向基层治理部门的行动方案初稿"
---

# formal-report-drafting-with-executable-precision

Generates formal, policy-adjacent report drafts for municipal or frontline governance stakeholders—prioritizing structural clarity, operational specificity, institutional tone, and built-in execution logic: every recommendation must name a responsible actor, specify an observable action, and define a time-bound or measurable outcome.

## Prompt

# Goal
Produce a formal, internally actionable report draft on a public service or community policy topic—structured for review by municipal or frontline governance stakeholders. Output must be self-contained, de-identified, and ready for immediate use in planning or inter-departmental coordination.

# Constraints & Style
- Use only plain paragraph-based structure: sections labeled with bolded Arabic numerals (e.g., **1. Background**), no tables, bullet variants (▪, →), emojis, or markdown syntax beyond minimal bolding for section headers.
- Language must be formal, restrained, and implementation-oriented: avoid adjectives without functional grounding (e.g., 'innovative', 'seamless'), eliminate rhetorical flourishes, and replace vague commitments ('enhance', 'leverage') with concrete verbs ('deploy', 'integrate', 'assign', 'trigger').
- All recommendations must specify: (a) responsible actor (e.g., '<AGENCY>', 'the街道 office', 'contracted provider'), (b) observable action, and (c) time-bound or measurable outcome (e.g., '<DEADLINE>', 'achieve ≥<TARGET_RATE>', 'reduce average processing time to <TIME_THRESHOLD>').
- All claims must be traceable to cited policy documents, verified data sources, or auditable operational facts (e.g., '<NUM_PARTICIPANTS> survey', 'current fiscal framework'); omit speculative benefits, unmeasurable outcomes, or cross-jurisdictional dependencies without named accountable entities.
- De-identify all proper nouns and instance-specific values: replace locations, departments, systems, programs, dates, rates, counts, and deadlines with placeholders (e.g., <STREET_OFFICE>, <CITY_PLATFORM>, <DEADLINE>, <TARGET_RATE>, <NUM_PARTICIPANTS>).
- Never include appendices, references, 'next steps' phrasing, or meta-commentary—the draft must stand as a complete, decision-ready artifact.

# Workflow
1. Infer core objective and scope from user-provided topic (e.g., 'community elderly care optimization').
2. Construct five mandatory sections: **1. Background**, **2. Current Situation**, **3. Guiding Principles**, **4. Actionable Recommendations**, **5. Implementation Safeguards**.
3. In **Background**, explicitly cite the governing policy framework (e.g., national plan, municipal regulation, internal directive).
4. For each recommendation, validate triple specification: actor + action + outcome — and use official role-based assignment language (e.g., 'by <AGENCY>', 'to be completed by <DEADLINE>', 'achieving <TARGET_RATE>').
5. In **Implementation Safeguards**, consolidate policy alignment, funding source specificity, and third-party evaluation design — no inline appendices or references unless required as deliverables.

## Triggers

- 写一份正式报告草案
- 生成可执行的政策建议报告
- 起草克制、无修饰的政务文书
- 输出不带表格的正式工作汇报
- 撰写面向基层治理部门的行动方案初稿
