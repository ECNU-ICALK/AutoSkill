---
id: "87bcc493-d7f3-4701-b40c-f99e36c470d8"
name: "policy-to-public-and-executive-communication-transformation"
description: "Transforms formal policy documents into two parallel, fact-accurate outputs: (1) an accessible public version for general audiences (e.g., families, older adults), and (2) a concise execution version for frontline staff — both preserving all original commitments, timelines, eligibility criteria, service parameters, and verification requirements without addition, omission, inference, or speculation."
version: "0.1.1"
tags:
  - "policy"
  - "audience-adaptation"
  - "fact-preserving"
  - "operational-fidelity"
  - "accessibility"
  - "public-facing"
triggers:
  - "rewrite for general public and staff"
  - "convert policy to public + execution versions"
  - "generate family-friendly and frontline-staff versions"
  - "make it accessible and actionable for two audiences"
  - "output resident version and operator checklist"
---

# policy-to-public-and-executive-communication-transformation

Transforms formal policy documents into two parallel, fact-accurate outputs: (1) an accessible public version for general audiences (e.g., families, older adults), and (2) a concise execution version for frontline staff — both preserving all original commitments, timelines, eligibility criteria, service parameters, and verification requirements without addition, omission, inference, or speculation.

## Prompt

# Goal
Convert a formal policy or implementation document into two strictly faithful, parallel outputs:
- **Public Version**: Clear, warm, and actionable content for non-specialist readers (e.g., adult children, older adults), using plain language, active voice, and relatable framing (e.g., 'you can…', 'your parent may…') — preserving all factual constraints: who is eligible, what services are offered, when they start/end, where to access them, how to apply, and all quantified metrics (e.g., 'within 7 working days', '50 households', '80+ years old').
- **Execution Version**: Ultra-concise internal reference for staff; each sentence follows the pattern: '[Role] [does X] by [date], verified by [metric]', listing only binding actions, responsible roles, hard deadlines, and objective verification criteria (e.g., '100% completion', '≤3-day response', 'system-logged').

# Constraints & Style
- Both versions must be factually identical to the source: no dates, numbers, scopes, thresholds, procedures, or verification methods may be altered, omitted, implied, or approximated beyond verbatim or minimally simplified equivalents (e.g., 'about 320 seniors' only if source says '317').
- Ban all markdown formatting (no bold, headers, lists, tables, icons, dividers, emojis) in both versions.
- Public Version: use short sentences, concrete nouns, and direct address; cite timing as 'starting [date]' or 'by [date]'; avoid metaphors, disclaimers, footnotes, external references, or internal governance details (e.g., 'led by X office', 'per Section 2.3') unless directly tied to user action; include only contact points or channels explicitly named in the source.
- Execution Version: one imperative sentence per binding action; omit explanations, context, rationale, or descriptive language; if source lacks a required element (e.g., no stated deadline or role), omit that sentence entirely — never invent or prompt.
- Replace bureaucratic terms ('utilize', 'leverage', 'stakeholder') with everyday equivalents ('use', 'get help from', 'neighbors', 'families'); never invent new services, benefits, exceptions, or eligibility rules.

# Workflow
1. Parse the source document to extract all concrete, time-bound, eligibility-gated, and quantified service commitments — including actors, actions, deadlines, metrics, scopes, channels, and verification criteria.
2. Generate Public Version: map each commitment to reader-relevant questions (Who qualifies? What do they get? When does it start? How do they access it? What’s required?); rewrite using scenario-based phrasing (e.g., 'If your parent lives alone and is 80+…') and group under intuitive thematic headings (e.g., 'Help at home', 'Getting meals', 'Staying safe').
3. Generate Execution Version: distill each binding fact into a single sentence matching the four-element pattern; ensure every sentence traces to an explicit statement in the source.
4. Output both versions as adjacent plain-text blocks, labeled 'Public Version' and 'Execution Version', with no preamble, summary, or formatting.

## Triggers

- rewrite for general public and staff
- convert policy to public + execution versions
- generate family-friendly and frontline-staff versions
- make it accessible and actionable for two audiences
- output resident version and operator checklist
