---
id: "c61a3b96-e6f1-4e9b-9be5-7e6d160c3efc"
name: "formal-report-drafting-with-executable-structure"
description: "Generates formal, policy-ready report drafts for internal or inter-agency use that prioritize clarity, restraint, and operational feasibility—structured linearly in prose, with every recommendation specifying who does what, by when, and how success is verified."
version: "0.1.1"
tags:
  - "reporting"
  - "policy-drafting"
  - "public-sector"
  - "executability"
  - "accountability"
  - "quantitative"
triggers:
  - "写一份正式报告草案"
  - "生成可执行的政策报告初稿"
  - "起草内部审议用的正式文稿"
  - "输出克制、无修饰的政务类报告"
  - "需要线性结构、禁用表格的正式文档"
---

# formal-report-drafting-with-executable-structure

Generates formal, policy-ready report drafts for internal or inter-agency use that prioritize clarity, restraint, and operational feasibility—structured linearly in prose, with every recommendation specifying who does what, by when, and how success is verified.

## Prompt

# Goal
Produce a formal, policy-ready draft report intended for internal review, inter-departmental coordination, or official submission. Output must be immediately actionable: every measure must specify *who* is responsible, *what* is delivered, *by when*, and *how success is verified*.

# Constraints & Style
- Tone: formal, neutral, and restrained—no rhetorical flourishes, emotive language, colloquialisms, or value-laden adjectives (e.g., avoid 'seamless', 'enhance', 'leverage', 'world-class'); use precise, evidence-grounded terms and concrete verbs (e.g., 'install', 'train', 'verify', 'audit').
- Structure: linear section flow only—no tables, no bullet clusters, no markdown syntax (e.g., no `|`, `-`, `**`, `###`); use plain paragraph breaks and numbered/lettered headings (e.g., '1.', '2.', 'a)', 'b)') for hierarchy. Avoid generic section labels like 'Background' or 'Conclusion' unless mandated; prioritize functional sequencing (e.g., 'Principles → Tasks → Accountability → Verification').
- Content discipline: every claim must be grounded in observable or measurable conditions (e.g., 'response time exceeds SLA by 42%' not 'service is slow'); omit speculative benefits, aspirational vision statements, or unverifiable impact claims.
- Executability focus: all recommendations must specify *who does what*, *by when* (using calendar dates like '2024-09-30' or event-relative timing like 'within 1 working day of receipt'), and *what changes operationally*—with at least one quantified metric (e.g., 'within 7 working days', '≤3-minute response time', '≥95% compliance rate') and an explicitly named accountable party (e.g., 'Community Health Service Center', 'Contractor X').
- No attachments, footnotes, appendix references, placeholder tokens (e.g., <NUM>, <TOKEN>), or ungrounded statistics—integrate essential data context directly into narrative.

# Workflow
1. Identify the core service domain and governance level (e.g., municipal community program, county health initiative) and extract the core mandate from user instruction.
2. Summarize current state using only quantified or verifiable operational facts (capacity, coverage, latency, compliance gaps).
3. Derive recommendations as concrete, role-assignable actions—not principles or frameworks—embedding accountability dimensions (responsible entity, deadline, output artifact, verification method, numeric threshold) fused within each sentence.
4. Sequence implementation steps chronologically or by dependency, naming responsible actors and success indicators where possible.
5. Conclude with a single-sentence statement of purpose—not vision, not values—stating the report’s functional intent (e.g., 'This draft supports internal alignment on Phase 1 service redesign priorities.').
6. Validate that no sentence lacks at least one quantified metric and one named accountable actor.

## Triggers

- 写一份正式报告草案
- 生成可执行的政策报告初稿
- 起草内部审议用的正式文稿
- 输出克制、无修饰的政务类报告
- 需要线性结构、禁用表格的正式文档
