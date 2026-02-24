---
id: "07b24989-4db8-49fb-b38f-83e71b233d34"
name: "canine-appetite-decline-escalation-protocol"
description: "Applies a three-tiered, objective, time-bound escalation protocol for canine appetite decline—based on quantified food intake reduction and duration—to determine when to intervene at home, monitor closely, or seek immediate veterinary care, with distinct executable checklists for owners and temporary caregivers."
version: "0.1.2"
tags:
  - "health-monitoring"
  - "clinical-triage"
  - "threshold-based"
  - "dog-care"
  - "preventive-care"
  - "veterinary-escalation"
  - "owner-delegate-split"
triggers:
  - "appetite decline escalation"
  - "when to vet for dog not eating"
  - "dog refuses food rule"
  - "canine health red flag rule"
  - "pet care escalation protocol"
  - "dog not eating daily checklist"
  - "appetite decline action list"
  - "canine anorexia response protocol"
  - "dog food refusal escalation"
  - "daily dog appetite monitoring"
---

# canine-appetite-decline-escalation-protocol

Applies a three-tiered, objective, time-bound escalation protocol for canine appetite decline—based on quantified food intake reduction and duration—to determine when to intervene at home, monitor closely, or seek immediate veterinary care, with distinct executable checklists for owners and temporary caregivers.

## Prompt

# Goal
Generate a precise, actionable three-tiered escalation protocol for canine appetite decline that maps quantified food intake reduction (vs. baseline) and duration to specific caregiver actions and veterinary referral criteria, integrated into an existing pet care plan—delivered as two parallel, chronologically ordered, role-specific checklists: one for the owner and one for temporary delegates.

# Constraints & Style
- Base all assessments on **quantified food intake** (grams or standardized scoops), not subjective impressions; compare to a 7-day baseline average.
- Use only three tiers: Level 1 (20–40% reduction, ≥2 consecutive meals), Level 2 (>40% reduction OR mild systemic signs like lethargy/vomiting, ≥24h), Level 3 (complete anorexia >24h OR critical red flags like collapse, dehydration, or abdominal pain).
- Output only two plain-text checklists: 'Daily Owner Checklist' and 'Daily Delegate Checklist'.
- Each checklist must be strictly chronological, with rows labeled by time window (e.g., 'At first missed meal', 'After 24 hours', 'After 48 hours')—no vague terms like 'if concerned' or 'as needed'.
- Every row must contain exactly three colon-separated fields: [Trigger condition] : [Required action] : [Escalation outcome if condition met].
- Trigger conditions must be objectively verifiable (e.g., 'bowl contains ≥40% original portion', 'no food consumed for 24 consecutive hours', 'weight loss >0.3kg since baseline')—no subjective language.
- Actions must be atomic and executable by the role without interpretation (e.g., 'take photo with timestamp', 'measure rectal temperature', 'call vet immediately').
- Escalation outcomes must specify who does what next, including handoff instructions where relevant (e.g., 'delegate calls vet; owner confirms authorization via voice note').
- Explicitly lower escalation thresholds for high-risk populations (e.g., senior dogs, post-spay/neuter, chronic disease).
- Never recommend fasting beyond 2 hours unless Level 3 is reached.
- Distinguish isolated missed meals (low-risk) from clinically meaningful decline (high-risk).
- Must be embeddable into caregiver instructions without requiring medical interpretation.
- Do not invent symptoms, diagnostics, or treatments outside the defined triage logic.
- Output only the two checklists—no explanations, examples, headers beyond the two titles, or tooling references.
- Total output must fit in ≤25 lines—prioritize brevity over completeness; omit all non-essential context.

# Workflow
1. Observe and record exact food offered and consumed (in grams or consistent units) at each scheduled meal.
2. Compare to baseline (7-day average from prior routine).
3. Classify into Level 1 / 2 / 3 using duration and co-occurring signs.
4. Execute corresponding action set from the appropriate checklist (owner or delegate); log response.
5. If upgrade condition is met, immediately advance to next level’s protocol and trigger handoff per escalation outcome.

## Triggers

- appetite decline escalation
- when to vet for dog not eating
- dog refuses food rule
- canine health red flag rule
- pet care escalation protocol
- dog not eating daily checklist
- appetite decline action list
- canine anorexia response protocol
- dog food refusal escalation
- daily dog appetite monitoring
