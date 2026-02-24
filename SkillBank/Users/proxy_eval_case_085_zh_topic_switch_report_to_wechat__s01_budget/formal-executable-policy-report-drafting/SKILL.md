---
id: "cbea058f-8044-4bef-bafd-a874b887ad81"
name: "formal-executable-policy-report-drafting"
description: "Generates formal, policy-grade draft reports that prioritize executable language, explicit responsibility assignment, and quantifiable success metrics — avoiding tables, narrative flourishes, or unverifiable claims."
version: "0.1.0"
tags:
  - "policy"
  - "reporting"
  - "accountability"
  - "metrics"
  - "public-sector"
  - "service-design"
triggers:
  - "write formal policy report"
  - "draft executable service plan"
  - "add responsibility and metrics"
  - "convert proposal to accountable language"
  - "make report audit-ready"
---

# formal-executable-policy-report-drafting

Generates formal, policy-grade draft reports that prioritize executable language, explicit responsibility assignment, and quantifiable success metrics — avoiding tables, narrative flourishes, or unverifiable claims.

## Prompt

# Goal
Produce a formal, actionable draft report for public-sector or community service policy proposals, where every recommendation specifies: (1) accountable entity/role, (2) concrete deadline or timeframe, (3) measurable output or performance threshold, and (4) verification mechanism or data source.

# Constraints & Style
- Use formal, restrained civil-service register: no adjectives without functional purpose (e.g., avoid "innovative", "robust", "seamless"); prefer verbs like "establish", "revise", "require", "assign", "verify".
- Never use tables, bullet clusters, or decorative formatting; present all information in declarative sentences with embedded structure (e.g., "By [date], [entity] shall [action], achieving [metric] as verified by [source]".
- All deadlines must be calendar-specific (e.g., "2024 Q3", "by 2024-10-15") or phase-bound (e.g., "within 60 days of approval").
- All metrics must be quantified and verifiable: include unit (%, #, minutes, km, etc.), baseline (if known), and target (e.g., "increase coverage from 38% to 65%", "reduce average response time from 12.6 to ≤5 minutes").
- Assign responsibility unambiguously: name institutional actors (e.g., "Community Health Service Center", "Street Public Service Office", "District Civil Affairs Bureau") — never vague terms like "stakeholders" or "relevant departments".
- Omit background context unless directly tied to a policy requirement or statutory basis (e.g., cite "per Article 7 of the 'XX Regulation'" only if user specifies it matters).
- Exclude appendices, footnotes, or supplementary commentary unless explicitly requested as deliverables.

# Workflow
1. Extract from user input: (a) core policy domain (e.g., community elder care), (b) required accountability level (e.g., municipal, street-level, facility-level), and (c) any mandated metrics or deadlines.
2. For each proposed action, generate one sentence containing: responsible actor + deadline + action verb + quantified outcome + verification method.
3. Group sentences thematically (e.g., service delivery, governance, capacity building), using numbered Roman/Arabic headings only if user provides section structure.
4. Final output must contain zero markdown tables, zero decorative headers (e.g., "---", "**bold**"), and zero ungrounded assertions (e.g., "widely recognized", "best practice").

## Triggers

- write formal policy report
- draft executable service plan
- add responsibility and metrics
- convert proposal to accountable language
- make report audit-ready
