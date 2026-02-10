---
id: "b1521dc9-44a0-4374-b6d7-92b2c7237af3"
name: "insurance-claim-appeal-pathway-and-evidence-supplementation"
description: "A reusable procedure for guiding policyholders through the formal appeal process when a home property insurance claim is partially denied, including jurisdiction-specific escalation steps and a targeted, actionable list of supplementary evidence to submit."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "compliance"
  - "evidence"
  - "PRC-regulation"
triggers:
  - "如果部分拒赔，给申诉路径和补证清单"
  - "claim partially denied appeal steps"
  - "how to challenge insurance denial"
  - "supplement evidence after rejection"
  - "insurance ombudsman process"
---

# insurance-claim-appeal-pathway-and-evidence-supplementation

A reusable procedure for guiding policyholders through the formal appeal process when a home property insurance claim is partially denied, including jurisdiction-specific escalation steps and a targeted, actionable list of supplementary evidence to submit.

## Prompt

# Goal
Generate a clear, step-by-step申诉路径 (appeal pathway) and a precise, prioritized 补证清单 (evidence supplementation checklist) in response to a partial claim denial in home property insurance — tailored to the stated reason for denial and aligned with PRC Insurance Law, CIRC/CCAC guidelines, and standard insurer internal appeal protocols.

# Constraints & Style
- Output must be strictly actionable: each appeal step must specify *who* to contact (role + channel), *what* to request (document type or decision), and *by when* (statutory or practical deadline, e.g., 'within 10 working days of denial notice').
- The 补证清单 must be organized by priority (High/Medium/Low), with each item specifying: (a) exact evidence type, (b) why it directly counters the stated denial reason, and (c) how to obtain it (e.g., 'Request fire department's original incident log via official letter').
- Never invent regulatory clauses or internal insurer policies; only cite widely recognized standards (e.g., 'Article 23 of the PRC Insurance Law', 'CIRC Notice No. [year] on Claim Handling Timeliness') — and only if user context implies PRC jurisdiction.
- Use plain, authoritative Chinese; avoid markdown formatting, disclaimers, or generic advice. Omit all examples, offers of further assistance, or promotional language.
- Do not include templates, scripts, or editable placeholders — output only the structured pathway and checklist.
- Exclude any content about initial filing, evidence collection pre-denial, or general tips — focus exclusively on post-denial redress.

# Workflow
1. Identify the stated reason for partial denial (e.g., 'excluded peril', 'insufficient proof of ownership', 'failure to mitigate').
2. Map that reason to the corresponding statutory or contractual appeal right under PRC insurance regulation.
3. Derive the official escalation sequence: first-level internal review → second-level ombudsman/complaint center → third-level regulatory referral (CBIRC/financial consumer protection bureau).
4. For each escalation level, list required submission materials — then distill into a single ranked 补证清单 addressing root cause gaps.
5. Output only the final structured pathway and checklist — no intros, summaries, or follow-up prompts.

## Triggers

- 如果部分拒赔，给申诉路径和补证清单
- claim partially denied appeal steps
- how to challenge insurance denial
- supplement evidence after rejection
- insurance ombudsman process
