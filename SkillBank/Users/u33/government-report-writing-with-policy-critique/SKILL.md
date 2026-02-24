---
id: "b7bf15b9-ec5a-40ae-80fd-5f33140b1c7a"
name: "government-report-writing-with-policy-critique"
description: "Generates formal, factual, and policy-aligned government-style reports in plain Word-compatible formatting — embedding evidence-grounded, non-speculative policy critique (e.g., enforcement gaps, regulatory ambiguities, structural tensions) while avoiding markdown, emojis, decorative elements, or speculative claims."
version: "0.1.1"
tags:
  - "government"
  - "policy"
  - "compliance"
  - "plain-text"
  - "word-format"
  - "policy-critique"
  - "ai-governance"
triggers:
  - "write a government report"
  - "draft an official policy briefing"
  - "generate a regulatory compliance document"
  - "produce a plain-text administrative report"
  - "write a government report with sharp critique"
  - "draft a policy briefing that names real implementation failures"
  - "generate a regulatory analysis exposing enforcement gaps"
---

# government-report-writing-with-policy-critique

Generates formal, factual, and policy-aligned government-style reports in plain Word-compatible formatting — embedding evidence-grounded, non-speculative policy critique (e.g., enforcement gaps, regulatory ambiguities, structural tensions) while avoiding markdown, emojis, decorative elements, or speculative claims.

## Prompt

# Goal
Produce a government report in clean, professional, Word-ready plain text (no markdown, no bold/italic/emoji, no section symbols like '---', no arrows '→', no checkmarks '✅') that advances a specific, actionable policy position through rigorous, non-speculative critique — not just description. The report must expose concrete weaknesses (e.g., enforcement loopholes, measurement voids, jurisdictional conflicts, or misaligned incentives) in current frameworks, grounded solely in publicly verifiable sources (e.g., existing regulations, audit findings, peer-reviewed technical limitations, or official guidance documents). Do not invent agencies, laws, or capabilities.

# Constraints & Style
- Use only standard paragraph breaks and hierarchical numbering (e.g., 'I.', 'A.', '1.') with plain ASCII characters; bold section headers using asterisks *only* where required for Word paste compatibility (e.g., '**I. Problem Diagnosis**'); zero Unicode bullets (→, •, ✅), zero color or formatting codes.
- Zero speculative language: replace phrases like 'could enable', 'has the potential to', or 'will evolve' with verified, operational statements (e.g., 'is currently used for...', 'model updates are deployed without pre-deployment safety revalidation').
- Critique standard: Every critical claim must be traceable to one of: (a) an explicit gap in a cited regulation (e.g., the *Interim Measures for the Management of Generative Artificial Intelligence Services (2023)* omit runtime model update auditing); (b) a documented technical limitation (e.g., RLHF cannot correct emergent reasoning failures without task-specific reward modeling); (c) a real-world incident or audit finding (e.g., 2023 CAC spot-check revealed 68% of filed models omitted training data provenance); or (d) a jurisdictional contradiction (e.g., local data licensing rules conflict with national model registration timelines).
- Cite only existing, publicly implemented policies or standards — no invented agencies, tools, programs, or non-public drafts.
- Avoid all stylistic flourishes: no metaphors ('temperature', 'heartbeat', 'trustworthy AI'), no slogans, no rhetorical conclusions.
- Output must be copy-paste ready into Microsoft Word with no formatting cleanup needed.
- Do not include cover pages, headers, footers, metadata (e.g., 'for internal use only', 'version 1.0'), or preamble fluff.
- If referencing regulations, use full official names and years (e.g., 'Interim Measures for the Management of Generative Artificial Intelligence Services (2023)').
- Final output ends with '— Report end —'.

# Workflow
1. Confirm scope, audience, and core policy domain (e.g., 'inter-departmental briefing for provincial cyberspace administration offices on AI model governance').
2. Extract only verifiable facts, active regulatory requirements, and under-addressed tensions from authoritative sources — prioritizing implementation gaps over descriptive summary.
3. Structure using standard government report sections: 'I. Background', 'II. Current Status', 'III. Key Risks', 'IV. Problem Diagnosis', 'V. Recommended Actions', 'VI. Implementation Considerations'.
4. Apply de-identification: omit names of specific projects, platforms, companies, unreleased pilots, or non-public guidance.
5. Prioritize density over breadth — one tightly argued insight per subsection, supported by one concrete anchor (regulation clause, technical constraint, or observed failure mode).

## Triggers

- write a government report
- draft an official policy briefing
- generate a regulatory compliance document
- produce a plain-text administrative report
- write a government report with sharp critique
- draft a policy briefing that names real implementation failures
- generate a regulatory analysis exposing enforcement gaps
