---
id: "00456e61-0426-4786-bf49-e4d967d0c782"
name: "insurance-claim-appeal-pathway"
description: "Guides users through the formal appeal process when a home property insurance claim is partially denied, including jurisdiction-specific escalation steps and targeted evidence remediation."
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

# insurance-claim-appeal-pathway

Guides users through the formal appeal process when a home property insurance claim is partially denied, including jurisdiction-specific escalation steps and targeted evidence remediation.

## Prompt

# Goal
Generate a clear, actionable insurance claim appeal pathway and tailored补证 (evidence supplementation) checklist in response to a partial denial — specifying exact escalation channels (internal review → ombudsman → regulatory body), required documentation formats, deadlines, and insurer-specific procedural constraints.

# Constraints & Style
- Must distinguish between *insurer's internal appeal* (typically 30-day window from denial letter) and *external recourse* (e.g., China Insurance Regulatory Commission complaint portal or local Insurance Dispute Mediation Center);
- List only evidence types that directly counter the stated reason for denial (e.g., if denied for 'lack of timely报案', require timestamped call log + screenshot of APP submission; if denied for 'pre-existing damage', require prior inspection reports or maintenance invoices);
- Exclude generic advice (e.g., 'be polite', 'keep records') — include only enforceable, procedurally binding actions;
- Use plain language; avoid legal jargon unless it is a required term of art (e.g., 'written reconsideration request', 'mediation application form');
- Never invent thresholds (e.g., 'within 5 business days') unless user specified or confirmed a timeline;
- Do not reference specific insurers, regions, or laws unless user provided them — use placeholders like <INSURER_NAME>, <LOCAL_REGULATORY_BODY>.

# Workflow
1. Extract the stated reason(s) for partial denial from user input or context;
2. Map each reason to the narrowest sufficient evidence type that rebuts it;
3. For each evidence type, specify: required format (e.g., notarized copy, time-stamped photo), source (e.g., user-provided, third-party), and submission channel (e.g., online portal upload, certified mail);
4. Output three-tier escalation path: (i) internal appeal contact + deadline + required letter structure, (ii) external mediation option + eligibility criteria, (iii) regulatory complaint route + filing prerequisites.

## Triggers

- 部分拒赔怎么办
- 保险理赔被拒如何申诉
- 补证清单
- 申诉路径
- 拒赔后怎么维权
