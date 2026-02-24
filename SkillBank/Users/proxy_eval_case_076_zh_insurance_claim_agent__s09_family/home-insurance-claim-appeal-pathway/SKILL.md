---
id: "733aa628-4145-4e5b-9fa7-c6145744f4ee"
name: "home-insurance-claim-appeal-pathway"
description: "A reusable procedure for responding to partial claim denials in home property insurance, including regulatory-compliant escalation steps and targeted evidence remediation."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "compliance"
  - "evidence"
  - "china-regulation"
triggers:
  - "如果部分拒赔，给申诉路径和补证清单"
  - "理赔被拒怎么申诉"
  - "保险公司拒赔怎么办"
  - "补材料申诉流程"
  - "拒赔后如何维权"
---

# home-insurance-claim-appeal-pathway

A reusable procedure for responding to partial claim denials in home property insurance, including regulatory-compliant escalation steps and targeted evidence remediation.

## Prompt

# Goal
Generate a clear, actionable appeal pathway and precise补证清单 (evidence supplementation list) when a home property insurance claim receives a partial denial — specifying *exactly* which items/losses were denied, the stated reason (e.g., 'not covered under policy', 'insufficient proof of ownership', 'pre-existing damage'), and the insurer’s internal reference.

# Constraints & Style
- Output must be strictly de-identified: never include real insurer names, policy numbers, dates, addresses, or personal names; use placeholders like <INSURER>, <POLICY_NUMBER>, <DENIAL_REFERENCE>, <DENIED_ITEM>, <STATED_REASON>.
- Cite only China-specific regulatory anchors: the *Insurance Law of the PRC*, *Measures for the Administration of Insurance Consumer Complaints* (CBIRC Order No. 8), and *Guidelines on Handling Property Insurance Claims* (CIRC Notice [2012] No. 16).
- For each denied item, list *only* the minimal, admissible evidence required to rebut that specific reason — no generic advice (e.g., if denied for 'lack of theft report', require *only* 'original police立案回执 with case number and 'criminal investigation confirmed' wording'; not 'more photos').
- Never invent new policy clauses or coverage interpretations; base all rebuttal logic solely on standard exclusions (e.g., wear & tear, intentional loss) and evidentiary thresholds defined in CBIRC guidance.
- Exclude emotional language, negotiation tactics, or speculative outcomes; focus exclusively on procedural rights and documentable remediation steps.
- Structure output in three mandatory sections: (1) Regulatory Appeal Pathway (with time-bound escalation tiers), (2) Denial-Specific补证清单 (tabular: Denied Item | Stated Reason | Required Evidence | Source Guidance), (3) Submission Protocol (how/where to submit, with receipt requirement).

# Workflow
1. Parse the user-provided denial notice to extract: <DENIAL_REFERENCE>, <DENIED_ITEM>, and verbatim <STATED_REASON>.
2. Map <STATED_REASON> to one of these CBIRC-recognized denial categories: 'coverage exclusion', 'evidentiary insufficiency', 'causal ambiguity', 'valuation dispute', or 'procedural default'.
3. For each category, retrieve the corresponding regulatory remedy path and minimum evidence standard from authoritative CBIRC-issued materials.
4. Generate output using only the above mapped elements — no extrapolation, no hypotheticals, no insurer-specific process assumptions.

## Triggers

- 如果部分拒赔，给申诉路径和补证清单
- 理赔被拒怎么申诉
- 保险公司拒赔怎么办
- 补材料申诉流程
- 拒赔后如何维权
