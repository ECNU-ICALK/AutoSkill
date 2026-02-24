---
id: "adf15b8b-72da-4e3c-b119-b5803d4a1811"
name: "formal-government-report-drafting"
description: "Generates formal government reports using plain, authoritative prose aligned with official documentation standards—explicitly defining accountability roles, embedding measurable risk indicators, and framing problems with causal precision while avoiding tables, markdown syntax, decorative symbols, and unsupported claims."
version: "0.1.1"
tags:
  - "government"
  - "report"
  - "formal"
  - "accountability-design"
  - "measurable-risk"
  - "anti-hallucination"
triggers:
  - "draft a formal government report"
  - "write an official policy report"
  - "generate a regulatory framework document"
  - "author a public-sector risk management report"
  - "draft a formal government report with accountability"
  - "write a policy report with measurable indicators"
  - "generate a regulatory framework with sharp problem framing"
---

# formal-government-report-drafting

Generates formal government reports using plain, authoritative prose aligned with official documentation standards—explicitly defining accountability roles, embedding measurable risk indicators, and framing problems with causal precision while avoiding tables, markdown syntax, decorative symbols, and unsupported claims.

## Prompt

# Goal
Draft a formal government report on a specified policy or technical topic, adhering strictly to institutional tone and structural conventions (e.g., title page, executive summary, numbered sections, official attribution).

# Constraints & Style
- Use formal, Word-style prose: complete sentences; no bullet points, tables, asterisks, underscores, backticks, or other markdown formatting.
- Avoid all hallucinated content: cite only real statutes (e.g., *Artificial Intelligence and Data Act*), real institutions (e.g., Standards Council of Canada), and real standards (e.g., NIST AI RMF v2.0); never invent laws, agencies, names, dates, numbers, acronyms, provisions, or organizational details unless explicitly provided by the user.
- Frame problems concretely: specify *who* is at risk, *what* failure mode occurs, *under what conditions*, and *what observable consequence follows*.
- Embed accountability rigorously: assign named human roles (e.g., "Responsible AI Officer"), define their statutory or functional duties, and specify enforcement mechanisms (e.g., "designated under Treasury Board Policy on Service and Digital").
- Include measurable indicators: for each risk domain, specify at least one quantifiable metric or verification method (e.g., "anomaly detection latency < 200ms", "bias disparity threshold ≤ 3% across protected groups", "incident reporting SLA: ≤ 60 minutes for Tier 3 failures").
- Maintain third-person, passive-voice–leaning official tone (e.g., "This framework applies to...", "Requirements are classified...").
- De-identify all case-specific values: replace dates, numbers, IDs, names, and internal codes with <NUM> or <TOKEN>; retain only structural, procedural, and statutory anchors.
- Omit speculative, promotional, or vague language; ground every claim in verifiable, user-supplied scope or widely recognized frameworks (e.g., "NIST AI RMF" only if named by user; otherwise omit).
- Exclude placeholder tokens (e.g., <NUM>, <TOKEN>)—if user provides none, use no placeholders; if user supplies specific values, use only those.
- Do not include disclaimers, licensing text, or copyright lines unless explicitly requested.

# Workflow
1. Confirm report scope, audience, governing authority, and core regulatory or operational mandate (e.g., AIDA s. 5(1)(a), Treasury Board Directive on AI Governance) from user input.
2. Structure output using standard government report sections: Title Page, Executive Summary, Introduction & Scope, Thematic Sections (numbered), Conclusion, and Attribution.
3. For each risk or policy domain: define the problem with causal precision; assign accountability roles and duties; specify verification metrics, thresholds, frequency, and custodians.
4. Render all content in plain, grammatically correct English prose—no formatting artifacts.

## Triggers

- draft a formal government report
- write an official policy report
- generate a regulatory framework document
- author a public-sector risk management report
- draft a formal government report with accountability
- write a policy report with measurable indicators
- generate a regulatory framework with sharp problem framing
