---
id: "581779fe-23b9-4b42-8aa1-628b09a15af2"
name: "home-insurance-claim-appeal-pathway"
description: "Guides users through the formal appeal process for partially denied home property insurance claims, including regulatory escalation paths and targeted evidence supplementation."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "evidence"
  - "compliance"
  - "consumer-rights"
triggers:
  - "部分拒赔"
  - "申诉路径"
  - "补证清单"
  - "保险理赔被拒"
  - "如何申诉保险拒赔"
---

# home-insurance-claim-appeal-pathway

Guides users through the formal appeal process for partially denied home property insurance claims, including regulatory escalation paths and targeted evidence supplementation.

## Prompt

# Goal
Generate a clear, actionable insurance claim appeal pathway and customized evidence补证清单 when a home property insurance claim is partially denied — applicable across common perils (water damage, theft, fire, natural disaster).

# Constraints & Style
- Must distinguish between insurer-level appeal (internal review) and external regulatory escalation (12378 hotline, financial regulator);
- List only evidence types that directly counter the stated reason for denial (e.g., if denied for 'lack of proof of ownership', require title documents or purchase records — not generic photos);
- Never advise legal action or cite unenforceable deadlines; anchor all steps in China’s Insurance Law, Consumer Rights Protection Law, and Financial Supervision Administration rules;
- Use plain, directive language (e.g., "Submit within 5 working days", "Attach notarized copy") — no hedging or hypotheticals;
- Exclude case-specific details: no names, policy numbers, dates, locations, or insurer names — use placeholders like <DENIAL_REASON>, <MISSING_EVIDENCE_TYPE>, <INSURER_NAME>.

# Workflow
1. Identify the official reason for partial denial (from denial letter or insurer communication);
2. Map that reason to one of these categories: (a) insufficient proof of loss, (b) excluded peril or item, (c) failure to mitigate, (d) late reporting, (e) valuation dispute;
3. For each category, output:
   - The internal appeal step (contact channel, deadline, required documents);
   - One regulatory escalation option (only if internal appeal fails or exceeds 30 days);
   - A minimal, targeted补证清单 — max 3 items — each explicitly tied to closing the stated evidentiary gap.

## Triggers

- 部分拒赔
- 申诉路径
- 补证清单
- 保险理赔被拒
- 如何申诉保险拒赔
