---
id: "84b47692-e8ae-402c-8939-697fbb6d88e3"
name: "customer-facing-communication-quality-check"
description: "A time-aware quality assurance protocol for customer-facing support messages that minimizes repetitive back-and-forth by ensuring clarity, completeness, and anticipatory information delivery — with adaptive rigor for reduced staffing periods (e.g., weekends), while preserving core quality gates."
version: "0.1.1"
tags:
  - "customer-communication"
  - "quality-assurance"
  - "support-efficiency"
  - "tone-control"
  - "weekend-operations"
triggers:
  - "reduce back-and-forth with customers"
  - "avoid repetitive questions"
  - "customer message quality check"
  - "calm professional tone"
  - "prevent follow-up emails"
  - "weekend support messaging"
  - "low-staffing customer communication"
---

# customer-facing-communication-quality-check

A time-aware quality assurance protocol for customer-facing support messages that minimizes repetitive back-and-forth by ensuring clarity, completeness, and anticipatory information delivery — with adaptive rigor for reduced staffing periods (e.g., weekends), while preserving core quality gates.

## Prompt

# Goal
Generate or validate customer-facing support messages (e.g., triage replies, status updates, resolution notices) to eliminate avoidable follow-up questions — by embedding all necessary context, next steps, and decision boundaries upfront, with adjustments for reduced staffing windows (e.g., Friday 18:00–Monday 08:59 local time).

# Constraints & Style
- Tone: Calm, professional, and empathetic — no urgency language (e.g., avoid "immediately", "ASAP", "urgent", "right away"); use precise, confident timeframes instead (e.g., "by 3:00 PM PT today", "first thing Monday morning").
- Must include *all four* core quality gates before sending:
  • ✅ **Explicit scope**: State what *is* and *is not* covered in this response (e.g., "This confirms your export issue — we’re not reviewing billing history here.").
  • ✅ **Single clear ask (or none)**: If action is needed from the customer, phrase it as *one* specific, low-effort request — with example format (e.g., "Please share a screenshot of the error *and* the exact time it occurred").
  • ✅ **Anticipated next step + timeframe**: Name the *next internal action* and its committed SLA — adjusted for staffing capacity (e.g., "Engineering will investigate and update you by 5:00 PM ET tomorrow"; or during weekends: "Our on-call engineer has been notified; full triage resumes Monday.").
  • ✅ **No open loops**: Avoid vague prompts like "Let us know if you have questions." Instead, close with a bounded offer (e.g., "If you observe this behavior again *after* [date/time], please reply with the new timestamp and browser version.").
- Weekend-specific adaptations (applies when current time is Friday 18:00 → Monday 08:59 local):
  • Require *at least two* of: (1) observed context (e.g., account ID, error code), (2) a precisely matched KB link with brief justification, (3) a single next step or question.
  • Do not promise SLAs incompatible with weekend coverage (e.g., omit or rephrase any <4-hr commitments).
  • If escalation is pending/delayed, state timing transparently and neutrally.
- Must NOT include: technical jargon without brief plain-language translation; assumptions about customer environment/knowledge; unqualified promises (e.g., "fixed soon"); passive voice obscuring ownership (e.g., "a fix will be deployed" → "our team is deploying a fix"); or open-ended questions.

# Workflow
1. Review draft message against the four core quality gates.
2. If current time falls within weekend window (Fri 18:00 → Mon 08:59 local), apply staffing-aware adaptations: verify at least two contextual elements, adjust SLAs/escalation language, and relax the Self-Service Anchor check *only* when no matching KB article exists *and* the issue is newly observed in weekend logs.
3. If any gate fails, revise *in place* — do not add disclaimers or footnotes; integrate corrections directly into the body.
4. Output only the final validated message — no commentary, no markdown headers, no explanations.

## Triggers

- reduce back-and-forth with customers
- avoid repetitive questions
- customer message quality check
- calm professional tone
- prevent follow-up emails
- weekend support messaging
- low-staffing customer communication
