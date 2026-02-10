---
id: "d16e25b6-e813-46cf-bc3f-31f9c1a8c505"
name: "property-claim-appeal-pathway-and-evidence-gap-resolution"
description: "A reusable skill for guiding policyholders through the formal appeal process when a home insurance claim is partially denied, including jurisdiction-specific escalation steps and targeted evidence补证清单 generation."
version: "0.1.0"
tags:
  - "insurance"
  - "appeal"
  - "evidence"
  - "compliance"
  - "claims"
triggers:
  - "appeal partial claim denial"
  - "respond to home insurance rejection"
  - "get insurer appeal steps"
  - "resolve evidence gap after denial"
  - "generate rebuttal evidence list"
---

# property-claim-appeal-pathway-and-evidence-gap-resolution

A reusable skill for guiding policyholders through the formal appeal process when a home insurance claim is partially denied, including jurisdiction-specific escalation steps and targeted evidence补证清单 generation.

## Prompt

# Goal
Generate a clear, actionable insurance claim appeal pathway and a precise, prioritized evidence补证清单 in response to a partial denial — scoped to the user's insurer, policy type (home property), and stated reason for denial.

# Constraints & Style
- Output only the appeal pathway (steps, responsible parties, deadlines, escalation contacts) and the补证清单 (items ranked by evidentiary weight and urgency), with zero generic advice or filler.
- Do not invent regulatory citations, internal insurer departments, or procedural thresholds unless explicitly confirmed by the user (e.g., 'My insurer said it's under review by the Complaints Department').
- All insurer-specific details (e.g., department names, internal forms, portal URLs, complaint reference formats) must be omitted unless provided verbatim by the user.
- Use placeholders: <INSURER_NAME>, <DENIAL_REASON>, <POLICY_NUMBER>, <CLAIM_REFERENCE>.
- Never include emotional language, reassurance, or motivational phrasing (e.g., 'don’t worry', 'you’ve got this').
- Avoid markdown tables, callouts, or decorative symbols (✅/⚠️/🔹); use plain bullet structure only.

# Workflow
1. Extract from user input: (a) insurer name, (b) stated denial reason (e.g., 'lack of proof of ownership', 'excluded peril'), and (c) any cited policy clause or letter reference.
2. If insurer name is missing or ambiguous, output only generic statutory escalation logic (e.g., 'file with local insurance regulator within 30 days of written denial') — no assumptions.
3. For each denial reason, map to one required evidence type — prioritize insurer-accepted formats (e.g., 'notarized affidavit' over 'personal statement').
4. Rank补证 items by: (i) legal/admissibility weight, (ii) turnaround time (<48h vs >5d), and (iii) dependency (e.g., 'police report' must precede 'repair quote').
5. Output two clean sections: 'Appeal Pathway' and 'Targeted Evidence补证清单'.

## Triggers

- appeal partial claim denial
- respond to home insurance rejection
- get insurer appeal steps
- resolve evidence gap after denial
- generate rebuttal evidence list
