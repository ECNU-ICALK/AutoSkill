---
id: "3e35ed5f-d711-44f4-9e9d-d473067fc1da"
name: "home-property-insurance-appeal-pathway"
description: "A reusable procedure for navigating partial claim denials in home property insurance, including jurisdiction-specific escalation steps and targeted evidence supplementation."
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
  - "补证清单"
  - "申诉路径"
  - "拒赔后怎么维权"
---

# home-property-insurance-appeal-pathway

A reusable procedure for navigating partial claim denials in home property insurance, including jurisdiction-specific escalation steps and targeted evidence supplementation.

## Prompt

# Goal
Generate a clear, actionable appeal pathway and precise补证清单 when a home property insurance claim receives partial denial — scoped to the user's actual loss type (e.g., water damage, theft) and insurer’s stated reason for exclusion.

# Constraints & Style
- Must distinguish between insurer-level appeals (internal review, ombudsman) and external redress (insurance regulator complaint, mediation, litigation) — only include channels valid in the user’s jurisdiction (default: mainland China; if user specifies otherwise, adapt).
- For each appeal tier, list exact required inputs: e.g., 'Written appeal letter + copy of denial notice + new evidence' — no vague phrases like 'submit supporting documents'.
- The 补证清单 must be loss-scenario-specific and reason-specific: e.g., if denied for 'lack of proof of ownership', require only invoices/registration/docs for *the denied items*, not all items; if denied for 'excluded peril', require meteorological or police evidence *directly contradicting the exclusion*.
- Never invent legal thresholds (e.g., 'within 15 days') unless user cites policy language or regulation; if uncertain, default to 'within the timeframe specified in your policy’s dispute clause' and flag for user verification.
- Output in plain, directive language — no explanations, no disclaimers, no marketing phrases ('feel free', 'happy to help').
- Exclude all case-specific identifiers: no names, addresses, policy numbers, dates, or insurer names — use placeholders like <POLICY_NUMBER>, <DENIAL_REASON>, <LOSS_TYPE>.

# Workflow
1. Identify the stated denial reason from the insurer’s written notice (e.g., 'not covered under 'sudden and accidental water damage' clause', 'no police report for theft').
2. Map that reason to one or more validated appeal tiers (insurer internal → industry ombudsman → regulator).
3. For each tier, specify: (a) submission channel (email/portal/post), (b) mandatory attachments, (c) expected response timeline (if codified in regulation/policy), (d) user action trigger (e.g., 'if no response in 10 working days, escalate to...').
4. Generate a minimal, targeted 补证清单: only evidence that directly rebuts the cited denial reason — grouped by tier where applicable.

## Triggers

- 部分拒赔怎么办
- 保险理赔被拒如何申诉
- 补证清单
- 申诉路径
- 拒赔后怎么维权
