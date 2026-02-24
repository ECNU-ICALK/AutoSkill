---
id: "f3427333-97e3-42c7-8b43-fbdd5a21d050"
name: "formal-report-drafting-with-executable-precision"
description: "Generates formal, policy-aligned report drafts for public service or community governance contexts, prioritizing operational feasibility, explicit accountability, and measurable outcomes—excluding speculative content, decorative formatting, tables, or non-executable elements."
version: "0.1.1"
tags:
  - "report-drafting"
  - "public-sector"
  - "executability"
  - "accountability"
  - "metrics-driven"
  - "de-identification"
triggers:
  - "写一份正式报告草案"
  - "生成可执行的正式报告"
  - "加责任分工和量化指标"
  - "保持克制中立的公文风格"
  - "输出政策落地导向的初稿"
---

# formal-report-drafting-with-executable-precision

Generates formal, policy-aligned report drafts for public service or community governance contexts, prioritizing operational feasibility, explicit accountability, and measurable outcomes—excluding speculative content, decorative formatting, tables, or non-executable elements.

## Prompt

# Goal
Produce a formal, executable draft report on a public-service or community development topic, structured for real-world implementation review, interdepartmental coordination, and stakeholder action.

# Constraints & Style
- Tone: Formal, neutral, and institutionally appropriate—no colloquialisms, rhetorical flourishes, advocacy language, or subjective framing (e.g., avoid 'urgent need', 'critical gap', 'crucial', 'vital', 'groundbreaking'; use 'required', 'targeted', 'aligned with policy').
- Structure: Use only hierarchical heading levels (###, ####); no tables, markdown lists with icons/indentation, bulletless paragraphs, bold/italics for emphasis, or decorative formatting.
- Content discipline: Every claim must be traceable to verified data or observable conditions; omit projections, assumptions, unattributed statistics, placeholder tokens (e.g., `<TOKEN>`, `X月X日`, `XX社区`), and replace proper nouns with de-identified placeholders (e.g., `<COMMUNITY_NAME>`, `<LEAD_AGENCY>`, `<TIMELINE>`).
- Executability focus: Every recommendation must imply clear ownership, timeline, and measurable outcome—no vague aspirations (e.g., avoid 'enhance collaboration'; instead: 'Community Health Center to deploy X by Y date'). Embed quantified targets directly in narrative: baseline, target value, unit, and deadline (e.g., 'increase family doctor sign-up rate from 51.3% to ≥85% by Q3 2025').
- Must not: Include appendices references, draft signatures, 'next steps' phrased as instructions to others (e.g., 'please convene a meeting'), project-specific attachments, raw data references, or implementation artifacts—those belong in cover memos or separate deliverables, not the report body.

# Workflow
1. Extract core objective and scope from user’s topic phrase (e.g., 'community elderly care optimization' or 'community养老服务优化').
2. Synthesize key findings into declarative, evidence-grounded paragraphs—prioritizing observed gaps over general trends.
3. Translate goals and initiatives into sequential, agent-oriented actions with assigned lead agency/responsible unit, start/end deadlines, and minimum verifiable output (e.g., 'install 120 handrails across 3 neighborhoods by Dec 2024').
4. Validate all claims against implied feasibility: remove any element requiring unstated authority, budget, or external approval unless explicitly scoped as 'recommended'.
5. Consolidate all metrics into narrative form—never tabular—and finalize with clear next-step protocol (e.g., 'submit for cross-departmental review within 5 working days').

## Triggers

- 写一份正式报告草案
- 生成可执行的正式报告
- 加责任分工和量化指标
- 保持克制中立的公文风格
- 输出政策落地导向的初稿
