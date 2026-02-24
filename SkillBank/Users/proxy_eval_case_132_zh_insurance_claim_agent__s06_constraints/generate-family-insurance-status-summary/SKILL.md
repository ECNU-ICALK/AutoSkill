---
id: "c5a3e1b9-41a5-4b09-8cbf-4ee068e899f3"
name: "generate-family-insurance-status-summary"
description: "A reusable skill that produces either a plain-language, scannable status tracking table or a concise, single-paragraph status summary for home insurance claims — both designed specifically for family members with no insurance expertise to understand progress at a glance."
version: "0.1.1"
tags:
  - "insurance"
  - "claim-tracking"
  - "accessibility"
  - "family-communication"
  - "plain-language"
  - "status"
triggers:
  - "make claim status table or summary for family"
  - "simple insurance progress update no jargon"
  - "track claim for non-expert family"
  - "printable or copy-paste claim status"
  - "family-friendly insurance tracker"
---

# generate-family-insurance-status-summary

A reusable skill that produces either a plain-language, scannable status tracking table or a concise, single-paragraph status summary for home insurance claims — both designed specifically for family members with no insurance expertise to understand progress at a glance.

## Prompt

# Goal
Generate a family-friendly insurance claim status output: choose *one* format based on user intent — either (A) a pipe-delimited, printable tracking table *or* (B) a single-paragraph plain-text summary. Both must avoid jargon, assume zero domain knowledge, and omit all case-specific identifiers.

# Constraints & Style
- Language: Use only everyday vocabulary (e.g., 'they said yes' not 'coverage confirmed'; 'still waiting' not 'pending underwriting'); replace technical terms: 'rejection' → 'partial denial', 'subrogation' → 'recovery process', 'indemnity' → 'payout', 'adjuster' → 'claims handler'.
- Table mode: Exactly 5 columns — [Step], [What It Means], [Status], [Last Updated], [What We’re Doing Next]; Status values limited to: ✅ Done, ⏳ Waiting, ❌ Stuck, 🆘 Needs Help, 📝 Preparing; each 'What It Means' phrase <10 words; no markdown tables — use pipe-delimited format.
- Paragraph mode: One continuous paragraph (no line breaks, bullets, headers, or symbols); simple present-tense, subject-verb-object order; include only: (1) where things stand today, (2) what was just done, (3) what happens next, (4) who does it, (5) what to watch for or do by when; max 120 words; trim all filler.
- De-identify: Never include policy numbers, names, dates, insurer names, or IDs — omit unverifiable specifics unless explicitly provided in the current request.
- No legal disclaimers, footnotes, external references, or scripts.

## Triggers

- make claim status table or summary for family
- simple insurance progress update no jargon
- track claim for non-expert family
- printable or copy-paste claim status
- family-friendly insurance tracker
