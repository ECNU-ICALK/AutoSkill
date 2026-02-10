---
id: "6087abe0-9253-4700-b089-0905a053a023"
name: "cross-city-relocation-role-allocation"
description: "A reusable, role-based task delegation framework for domestic cross-city relocation that assigns concrete, non-overlapping, time-bound responsibilities across three stakeholder groups — the primary mover (decision-maker/external liaison), immediate family (on-site coordinator/physical handler), and elderly parents (internal steward/document preparer) — with explicit handoff points and synchronized evidence capture to ensure coordinated execution without overlap, omission, or cognitive overload."
version: "0.1.1"
tags:
  - "relocation"
  - "role-allocation"
  - "family-coordination"
  - "crisis-response"
  - "evidence-synchronization"
triggers:
  - "三套分工清单"
  - "家人父母分工"
  - "搬家角色分配"
  - "责任分派表"
  - "谁负责什么"
---

# cross-city-relocation-role-allocation

A reusable, role-based task delegation framework for domestic cross-city relocation that assigns concrete, non-overlapping, time-bound responsibilities across three stakeholder groups — the primary mover (decision-maker/external liaison), immediate family (on-site coordinator/physical handler), and elderly parents (internal steward/document preparer) — with explicit handoff points and synchronized evidence capture to ensure coordinated execution without overlap, omission, or cognitive overload.

## Prompt

# Goal
Generate a clear, de-identified three-column responsibility matrix for a domestic cross-city move, assigning discrete, non-overlapping, time-bound actions to: (1) the primary mover (<USER>), (2) co-relocating family members (<FAMILY>), and (3) aging parents (<PARENTS>). Each column must contain only executable, atomic, low-cognitive-load tasks — no supervision, interpretation, decision-making, or external coordination.

# Constraints & Style
- All tasks must be atomic, observable, verifiable, and executable in ≤5 minutes (e.g., 'call property manager to confirm key handover' — not 'handle lease logistics').
- No task may require physical mobility beyond light activity (e.g., no 'carry boxes', 'climb stairs'); assign physically demanding or high-stakes actions only to <USER> or <FAMILY>.
- <PARENTS> tasks must be strictly limited to: document preparation (e.g., scanning IDs), remote verification (e.g., video-call landlord), passive coordination (e.g., receiving confirmation SMS), or creating/naming shared evidence albums — never external communication, legal signing, financial commitment, or platform navigation.
- Every handoff must be event-triggered and time-stamped (e.g., 'T+15 min', 'upon receipt of cancellation notice'), not duration- or condition-based.
- Mandate synchronized evidence capture: each role must produce *one* timestamped artifact per handoff node (screen recording, photo/video, voice memo, or upload to pre-established shared album), and all uploads must be cross-referenced (e.g., '<USER> uploads screenshot to shared album named "Relocation-Evidence-<DATE>"').
- Exclude all city names, platform URLs, brand names, monetary values, dates, personal identifiers, or legal/financial actions. Use placeholders: <USER>, <FAMILY>, <PARENTS>.
- Output only a Markdown table with exactly three headers: | <USER> | <FAMILY> | <PARENTS> | — no intro, no summary, no examples.
- Do not include budgeting, vendor selection, legal review, system navigation, or complaint initiation — those are out of scope for role allocation.

## Triggers

- 三套分工清单
- 家人父母分工
- 搬家角色分配
- 责任分派表
- 谁负责什么
