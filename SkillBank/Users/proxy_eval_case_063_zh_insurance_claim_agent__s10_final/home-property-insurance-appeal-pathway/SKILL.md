---
id: "cc242eb9-8f2e-4d07-a939-96e724e421a7"
name: "home-property-insurance-appeal-pathway"
description: "A reusable procedure for navigating partial claim denials in home property insurance, including structured escalation paths and targeted evidence supplementation."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "evidence"
  - "compliance"
  - "consumer-rights"
triggers:
  - "如果部分拒赔，给申诉路径和补证清单"
  - "保险公司拒赔怎么办"
  - "怎么申诉保险理赔不全"
  - "补材料申诉流程"
  - "拒赔后如何翻案"
---

# home-property-insurance-appeal-pathway

A reusable procedure for navigating partial claim denials in home property insurance, including structured escalation paths and targeted evidence supplementation.

## Prompt

# Goal
Generate a clear, actionable appeal pathway and precise补证清单 when a home property insurance claim is partially denied — tailored to the stated reason for denial and aligned with regulatory expectations (e.g., China's CBIRC guidelines).

# Constraints & Style
- Must distinguish between *insurer-initiated* denials (e.g., 'not covered per policy wording') and *process-driven* denials (e.g., 'incomplete documentation', 'untimely reporting').
- For each denial reason, list only the **one most authoritative escalation channel** (e.g., insurer’s internal complaint desk → CBIRC 12378 → mediation center), with exact submission requirements (format, deadline, mandatory fields).
- The 补证清单 must be strictly limited to evidence that directly rebuts the stated ground for denial — no generic or redundant items.
- Never advise legal action as first step; always sequence: 1) written appeal to insurer, 2) regulator referral, 3) mediation — unless fraud or bad faith is alleged.
- Use plain, directive language (e.g., "Submit via registered mail with return receipt", "Attach annotated copy of policy clause X.Y").
- Exclude all case-specific identifiers (names, addresses, dates, policy numbers, incident details); use placeholders like <DENIAL_REASON>, <POLICY_CLAUSE_REFERENCE>, <EVIDENCE_TYPE>.

# Workflow
1. Identify the official, written denial reason from the insurer (do not infer or assume).
2. Map it to one of these canonical categories: (a) Non-covered peril, (b) Excluded item/loss, (c) Insufficient evidence, (d) Late reporting, (e) Valuation dispute.
3. For that category, output:
   - The exact next-step appeal channel + submission method + deadline;
   - A minimal, targeted 补证清单 (max 3 items) that objectively addresses the gap;
   - One sentence explaining *why* that evidence resolves the stated objection.

## Triggers

- 如果部分拒赔，给申诉路径和补证清单
- 保险公司拒赔怎么办
- 怎么申诉保险理赔不全
- 补材料申诉流程
- 拒赔后如何翻案
