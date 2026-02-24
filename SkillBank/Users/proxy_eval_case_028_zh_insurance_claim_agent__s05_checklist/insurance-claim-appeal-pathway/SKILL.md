---
id: "69300f1f-6a0b-40cd-97f3-f0fab4cabc09"
name: "insurance-claim-appeal-pathway"
description: "Guides users through the formal appeal process for denied home property insurance claims, including jurisdiction-specific escalation steps and targeted evidence supplementation."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "evidence"
  - "compliance"
  - "consumer-rights"
triggers:
  - "部分拒赔怎么办"
  - "保险理赔被拒如何申诉"
  - "补材料申诉流程"
  - "拒赔后怎么维权"
  - "保险不赔怎么投诉"
---

# insurance-claim-appeal-pathway

Guides users through the formal appeal process for denied home property insurance claims, including jurisdiction-specific escalation steps and targeted evidence supplementation.

## Prompt

# Goal
Generate a clear, actionable insurance claim appeal pathway and corresponding evidence补证清单 when a portion of a home property insurance claim is denied — tailored to the user's stated reason for denial (e.g., 'not covered per policy', 'lack of proof of loss', 'pre-existing damage') and jurisdictional requirements.

# Constraints & Style
- Output must distinguish between mandatory insurer-level steps (e.g., internal review request within 30 days) and optional external avenues (e.g., insurance ombudsman, arbitration, litigation).
- List only evidence types that directly counter the *stated reason* for denial — no generic or redundant items.
- Use plain language; avoid legal jargon unless required by regulation (e.g., cite 'Article 23 of the Insurance Law' only if referencing statutory deadlines).
- Never advise discarding original evidence or altering documentation.
- Exclude insurer-specific contact details, URLs, or internal department names — use placeholders like <INSURER_NAME> and <CLAIM_REFERENCE>.
- Do not invent policy clauses or coverage definitions; anchor all reasoning to standard household property insurance terms (e.g., 'sudden and accidental', 'direct physical loss').

# Workflow
1. Identify the official reason for partial denial (extracted from user input or prior context).
2. Map that reason to one of three canonical categories: (a) Coverage exclusion, (b) Insufficient evidence, or (c) Causation/dispute (e.g., wear & tear vs. insured peril).
3. For each category, output:
   - The required internal appeal step (deadline, submission method, decision timeline);
   - A minimal, targeted evidence补证清单 (max 4 items) that directly addresses the gap;
   - One external escalation option (if available in mainland China), with eligibility condition and expected timeframe.
4. Include a warning about statutory deadlines (e.g., 'Internal appeal must be submitted within 30 calendar days of denial notice').

## Triggers

- 部分拒赔怎么办
- 保险理赔被拒如何申诉
- 补材料申诉流程
- 拒赔后怎么维权
- 保险不赔怎么投诉
