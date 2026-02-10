---
id: "ab616bcf-bc07-4f7a-9b3b-e5a5d30d0ac8"
name: "runway-triggered-cost-control-protocol"
description: "Automatically initiates a time-bound, role-specific cost-control protocol when cash runway falls below 5 months, ensuring immediate spending freezes, transparent communication, and delivery of a structured 96-hour Runway Recovery Plan."
version: "0.1.2"
tags:
  - "financial governance"
  - "crisis response"
  - "startup operations"
  - "cash management"
  - "decision protocol"
  - "ownership"
triggers:
  - "runway drops below 5 months"
  - "cash runway under 5 months"
  - "trigger cost control protocol"
  - "runway alert threshold met"
---

# runway-triggered-cost-control-protocol

Automatically initiates a time-bound, role-specific cost-control protocol when cash runway falls below 5 months, ensuring immediate spending freezes, transparent communication, and delivery of a structured 96-hour Runway Recovery Plan.

## Prompt

# Goal
When cash runway drops below 5 months, trigger a standardized, owner-driven cost-control protocol: activate immediate spending freezes, issue same-day team communication, and deliver a 1-page Runway Recovery Plan by Friday EOD — distinct from routine budget review.

# Constraints & Style
- Must be triggered *automatically* upon confirmed dashboard update (no delay for weekly sync); no discretion on whether or when to trigger.
- All freezes must be operationalized within 4–24 hours: hiring (except one pre-approved mission-critical role), non-core tools, non-revenue contractors, and paid marketing.
- Communication must include: verified runway number, activation notice, link to full plan, and explicit statement that non-essential spend is paused *effective immediately*.
- The Runway Recovery Plan must contain exactly four elements: (1) revised 3-month cash forecast, (2) one revenue-acceleration lever for this quarter, (3) one structural cost-reduction lever beyond freezes, and (4) a clear Go/No-Go checkpoint with defined next-step action if runway remains <4 months after Week 12.
- Output must include: (1) confirmed runway number, (2) top 3 controllable outflows >$1K/month, (3) one approved action with owner and deadline.
- No open-ended analysis: cap deliberation at 60 minutes; use pre-agreed criteria (e.g., "impact vs. effort", "reversibility", "revenue linkage") to rank options.
- During active Cost-Control Protocol, the first 10 minutes of every weekly sync are reserved *exclusively* for cost-control pulse check-in — no new initiatives approved until runway ≥5 months *and* recovery plan is on track.
- Never invent financial assumptions: all numbers (cash balance, burn, outflows) must derive from live dashboard data or verified bank/transaction records.
- Prohibited: deferring the protocol, substituting with 'monitoring', escalating without proposing an action, or omitting the Go/No-Go checkpoint.
- Keep output strictly concise: leadership summary ≤ 5 lines; checklist ≤ 7 rows with Owner/Deadline/Status only.
- Use placeholder thresholds only when generalizing (e.g., <DELAY_THRESHOLD>, <OVERRUN_PERCENTAGE>) — but for this skill, runway threshold is fixed at 5 months and must not be parameterized.
- All actions must be executable within 24–96 hours; no open-ended or planning-phase items.
- Never invent roles or decision rights — use only role labels already established in the team’s governance (e.g., 'CEO', 'Finance Owner', 'Product/Engineering Owner').
- If multiple triggers apply, consolidate into one unified response — do not generate parallel branches.

## Triggers

- runway drops below 5 months
- cash runway under 5 months
- trigger cost control protocol
- runway alert threshold met
