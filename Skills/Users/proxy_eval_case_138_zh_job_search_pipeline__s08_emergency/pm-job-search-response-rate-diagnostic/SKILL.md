---
id: "541c881a-8410-49d7-88d3-8ced2c5d18dc"
name: "pm-job-search-response-rate-diagnostic"
description: "A time-bound diagnostic protocol triggered when outreach response rate falls below 8%, guiding targeted root-cause analysis and corrective action for PM job search activities."
version: "0.1.0"
tags:
  - "diagnostic"
  - "outreach"
  - "response-rate"
  - "job-search"
  - "pm"
triggers:
  - "response rate below 8%"
  - "low reply rate diagnosis"
  - "outreach not working"
  - "referral messages ignored"
  - "PM job search follow-up failure"
---

# pm-job-search-response-rate-diagnostic

A time-bound diagnostic protocol triggered when outreach response rate falls below 8%, guiding targeted root-cause analysis and corrective action for PM job search activities.

## Prompt

# Goal
Automatically initiate a structured diagnostic workflow when measured outreach response rate (e.g., from internal referrals, LinkedIn messages, or cold emails) drops below 8% over a defined rolling window (e.g., last 25 outreach attempts), to identify and resolve systemic blockers in the PM job search process.

# Constraints & Style
- Must trigger *only* when response rate < 8% — do not assume low response; require explicit user-provided metric or calculation.
- Diagnostics must be actionable and scoped to the user’s current job search context (e.g., resume quality, message framing, target selection, timing), not generic advice.
- Exclude external factors outside user control (e.g., market conditions, company hiring freezes) unless user explicitly cites them as observed evidence.
- Output must include exactly three prioritized hypotheses (e.g., 'message lacks value preposition', 'targets misaligned with experience level', 'follow-up timing too short') and one concrete testable adjustment per hypothesis.
- All language must remain de-identified: no company names, platforms, tools, or personal identifiers.

# Workflow
1. Confirm response rate metric: ask user to specify numerator (replies received) and denominator (outreach sent) over a defined period or batch.
2. If confirmed < 8%, run triage across three dimensions:
   a) Message content (clarity, value signal, frictionless ask)
   b) Target selection (role fit, seniority alignment, channel relevance)
   c) Timing & cadence (gap between send/follow-up, day/time of outreach)
3. For each top hypothesis, propose one minimal, measurable intervention (e.g., 'replace "can you help?" with "I’ve prepared a 1-sentence match summary — happy to share if relevant"').
4. Output only the three hypotheses + interventions — no explanations, disclaimers, or encouragement.

## Triggers

- response rate below 8%
- low reply rate diagnosis
- outreach not working
- referral messages ignored
- PM job search follow-up failure
