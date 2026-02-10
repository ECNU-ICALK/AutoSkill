---
id: "e8add408-f37f-4a73-aedb-a0f19de00e66"
name: "insurance-claim-appeal-pathway-and-evidence-gap-analysis"
description: "A reusable procedure to generate a structured insurance claim appeal pathway and targeted evidence补证清单 when partial denial occurs, grounded in policy terms and insurer-specific escalation protocols."
version: "0.1.0"
tags:
  - "insurance"
  - "claims"
  - "appeal"
  - "evidence"
  - "compliance"
triggers:
  - "如果部分拒赔，给申诉路径和补证清单"
  - "保险公司拒赔怎么申诉"
  - "被拒赔了，需要补什么材料"
  - "理赔不全，怎么申请复核"
---

# insurance-claim-appeal-pathway-and-evidence-gap-analysis

A reusable procedure to generate a structured insurance claim appeal pathway and targeted evidence补证清单 when partial denial occurs, grounded in policy terms and insurer-specific escalation protocols.

## Prompt

# Goal
Given a partial claim denial from a home property insurer, produce: (1) a step-by-step internal appeal pathway (including deadlines, responsible units, and required submission formats), and (2) a precise, actionable evidence补证清单 that directly addresses each stated reason for denial — with no generic or redundant items.

# Constraints & Style
- Must distinguish between insurer-mandated steps (e.g., 'written appeal within 30 days to Claims Review Unit') and strategic actions (e.g., 'request full claim file under local insurance regulation').
- Evidence补证 items must be mapped one-to-one with each explicit denial reason (e.g., if denied for 'lack of proof of ownership', list only verifiable ownership documents — not photos or invoices). 
- Exclude all hypotheticals, legal commentary, or jurisdictional speculation unless user specifies regulatory context (e.g., 'under PRC Insurance Law Art. 23').
- Use plain, directive language — no explanations, no reassurance, no markdown formatting beyond headers and bullet points.
- Never invent insurer internal units, forms, or deadlines; only reflect those confirmed by user-provided denial notice or standard practice explicitly acknowledged by user.

# Workflow
1. Extract each discrete reason for partial denial from the user’s provided denial notice or summary.
2. For each reason, identify the *exact* evidentiary gap (e.g., 'no third-party verification of cause' vs. 'missing purchase receipt').
3. For each gap, specify the minimal sufficient evidence type, source, and format (e.g., 'Notarized statement from licensed plumber, on letterhead, describing root cause and date of inspection').
4. Assemble the appeal pathway chronologically: deadline → channel → recipient → required attachments → expected response timeframe.
5. Output only the pathway and the evidence补证 list — no introduction, summary, or offers of further assistance.

## Triggers

- 如果部分拒赔，给申诉路径和补证清单
- 保险公司拒赔怎么申诉
- 被拒赔了，需要补什么材料
- 理赔不全，怎么申请复核
