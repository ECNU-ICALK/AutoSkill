---
id: "917ecde9-c99d-4d9c-9a45-9e92d99fb4e7"
name: "low-response-rate-diagnostic-workflow"
description: "A reusable diagnostic workflow triggered when job application reply rate falls below 8%, designed to identify and correct systemic bottlenecks in resume targeting, outreach framing, or candidate positioning."
version: "0.1.0"
tags:
  - "job-search"
  - "diagnostic"
  - "feedback-loop"
  - "quality-gate"
triggers:
  - "reply rate under 8%"
  - "low application response"
  - "diagnose job search failure"
  - "why no interview invites"
  - "application feedback loop"
---

# low-response-rate-diagnostic-workflow

A reusable diagnostic workflow triggered when job application reply rate falls below 8%, designed to identify and correct systemic bottlenecks in resume targeting, outreach framing, or candidate positioning.

## Prompt

# Goal
Automatically initiate a structured root-cause analysis when the observed reply rate across job applications drops below 8% — not as a one-off check, but as a policy-gated quality control step.

# Constraints & Style
- ✅ Trigger only when reply rate = (replies received / applications sent) < 0.08, calculated over the most recent 20 applications (or all if <20).
- ✅ Do NOT assume low response is due to resume quality alone; systematically evaluate three independent levers: (1) JD alignment fidelity, (2) outreach personalization depth, (3) signal strength of proof artifacts (e.g., embedded prototypes, live reports).
- ✅ Output must be actionable: for each lever, surface *one* concrete, falsifiable hypothesis (e.g., "JD keywords appear in resume but not in cover summary") and *one* micro-test to validate it (e.g., A/B test two subject lines: one with JD phrase, one without).
- ❌ Do NOT generate generic advice (e.g., 'improve your resume'), vague suggestions (e.g., 'be more professional'), or unmeasurable fixes.
- ❌ Do NOT include thresholds, scoring rubrics, or taxonomy labels unless user explicitly defined them (e.g., no 'Tier 1/2/3' classification unless user used it in evidence).

# Workflow
1. Aggregate latest application log (company, role, date sent, reply status, channel).
2. Compute reply rate over sliding window (last 20 or full set).
3. If rate < 8%, run parallel diagnostics on:
   a) Resume-JD keyword mapping density (count of shared high-signal terms in top 1/3 of resume vs. JD);
   b) Outreach message structure (presence of specific reference to recipient’s work, company context, or role-specific challenge);
   c) Proof artifact accessibility (e.g., QR code scan success, PDF load time < 2s, Figma prototype has 'view-only' link).
4. For each failing lever, output exactly one hypothesis + one micro-test.
5. Deliver findings as a plain-text table: [Lever | Observed Gap | Hypothesis | Micro-Test].

## Triggers

- reply rate under 8%
- low application response
- diagnose job search failure
- why no interview invites
- application feedback loop
