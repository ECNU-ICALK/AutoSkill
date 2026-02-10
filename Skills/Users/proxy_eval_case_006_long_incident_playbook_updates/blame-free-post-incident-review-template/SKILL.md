---
id: "d62aaa9b-56f8-4d4a-8a3c-73024d98aa0a"
name: "action-only-post-incident-review-template"
description: "A strictly enforced template for post-incident reviews that captures only testable, assignable, time-bound, and verifiable remediation actions — excluding all narrative, root-cause analysis, descriptive explanations, individual names, and unactionable language."
version: "0.1.1"
tags:
  - "incident-response"
  - "postmortem"
  - "action-oriented"
  - "verifiable"
  - "blame-free"
triggers:
  - "create post-incident review"
  - "generate PIR action items"
  - "enforce action-only postmortem"
  - "remove root-cause from PIR"
  - "require verifiable remediation items"
---

# action-only-post-incident-review-template

A strictly enforced template for post-incident reviews that captures only testable, assignable, time-bound, and verifiable remediation actions — excluding all narrative, root-cause analysis, descriptive explanations, individual names, and unactionable language.

## Prompt

# Goal
Generate a Post-Incident Review (PIR) table containing *only* concrete, verifiable action items — no narration, no root-cause language, no status descriptions, no named individuals, and no untestable or vague statements.

# Constraints & Style
- Output *only* a Markdown table with exactly these columns: **#**, **Action Item (Specific, testable, scoped)**, **Owner (Role, not name)**, **Target Completion**, **Verification Method (How we confirm it’s done)**, **Priority (P0/P1/P2)**.
- Every Action Item must be:
  • Specific: Name exact service, endpoint, metric, tool, or config (e.g., `auth-service`, `/payment/submit`, `error_rate > 1.5%`).
  • Testable: Include observable success criteria (e.g., "synthetic test verifies trip behavior", "alert fires in staging").
  • Scoped: Limited to one atomic change (e.g., *not* "improve alerting" → *yes* "update `checkout-api` alert threshold from `error_rate > 5%` to `error_rate > 1.5%` for `/payment/submit` endpoint").
- Owner field must contain *only role titles* (e.g., `SRE`, `Tech Lead`, `Platform Engineer`) — never names, teams, or ambiguous terms like "the team".
- Target Completion must specify business days (e.g., `3 business days`) — never relative terms like "ASAP", "soon", or "T+X days/hours".
- Verification Method must describe an *objective, auditable check*: e.g., "Deployment confirmed in prod; synthetic test verifies trip behavior", "Runbook published in Confluence; linked from PagerDuty alert" — no subjective phrases like "reviewed", "discussed", or "confirmed".
- Priority must be exactly `P0`, `P1`, or `P2` — no explanations or modifiers.
- Exclude all blame-adjacent language: no references to "failure", "mistake", "oversight", "should have", "caused by", "due to", "root cause", "lesson learned", "we observed", "was misconfigured", "lacked monitoring", "improve", "review", or "investigate".
- Every row must include both a Target Completion *and* a Verification Method.
- If no verifiable gap is identified, output only the header row and the line: "*No action items: All observed behaviors aligned with current SLOs, runbooks, and tooling.*"
- If input contains narrative content, strip it entirely before populating the table.
- No section headers beyond the table; no introduction, summary, timeline, or 'what happened' narrative.

## Triggers

- create post-incident review
- generate PIR action items
- enforce action-only postmortem
- remove root-cause from PIR
- require verifiable remediation items
