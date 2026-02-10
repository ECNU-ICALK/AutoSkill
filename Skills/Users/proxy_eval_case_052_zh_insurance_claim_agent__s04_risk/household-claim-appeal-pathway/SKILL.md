---
id: "6d9f7ef8-89f6-461e-9d23-860ad8595bfe"
name: "household-claim-appeal-pathway"
description: "A reusable protocol for responding to partial claim denials in household property insurance, specifying standardized escalation steps and targeted evidence supplementation requirements."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "evidence"
  - "compliance"
  - "household-claim"
triggers:
  - "部分拒赔怎么办"
  - "保险理赔被驳回部分"
  - "申诉拒赔项目"
  - "补材料申诉流程"
  - "如何推翻保险公司拒赔决定"
---

# household-claim-appeal-pathway

A reusable protocol for responding to partial claim denials in household property insurance, specifying standardized escalation steps and targeted evidence supplementation requirements.

## Prompt

# Goal
Generate a clear, actionable appeal pathway and precise补证清单 when a household property insurance claim receives a partial denial — mapping each denied item to its root cause (e.g., exclusion, insufficient proof, valuation dispute) and prescribing only the minimum necessary, insurer-aligned evidence to challenge it.

# Constraints & Style
• Output must be strictly structured into two labeled sections: "Appeal Pathway" (sequential, role-specific escalation steps with time-bound expectations) and "Targeted Rebuttal Evidence" (itemized per denied loss, citing exact policy clauses or underwriting guidelines where user has provided them);
• Never invent policy language, coverage exclusions, or internal insurer procedures — only reflect constraints explicitly stated or confirmed by the user (e.g., 'they cited “wear and tear” exclusion', 'denied because no police report') ;
• Exclude generic advice (e.g., 'remain polite', 'keep records'); include only enforceable, traceable actions (e.g., 'submit Form IR-7 within 10 days', 'request written rationale under Article 28 of Insurance Law') ;
• Use placeholders for case-specific values: <DENIED_ITEM>, <POLICY_CLAUSE_REF>, <INSURER_NAME>, <REPORT_DATE>;
• All evidence types must be concrete, collectible, and time-bound (e.g., 'notarized repair quote dated within 5 business days', 'signed statement from licensed plumber confirming sudden rupture').

# Workflow
1. Parse the insurer’s written denial notice to identify: (a) each denied item, (b) stated reason, (c) cited policy section or internal guideline;
2. For each denied item, determine the narrowest evidentiary gap — not 'more proof' but *the specific proof missing that directly contradicts the stated reason*;
3. Map the appeal channel: first internal review → ombudsman → regulatory referral — with required submission formats, deadlines, and expected response windows;
4. Output only the minimal, non-redundant evidence needed to close each gap — rejecting bulk uploads or irrelevant documentation.

## Triggers

- 部分拒赔怎么办
- 保险理赔被驳回部分
- 申诉拒赔项目
- 补材料申诉流程
- 如何推翻保险公司拒赔决定
