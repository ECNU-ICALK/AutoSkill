---
id: "57fa0a6e-4d5e-42f6-a57c-4bcd2807f54a"
name: "family-property-claim-status-tracker-for-family"
description: "A reusable, non-technical status tracking table designed for family members with no insurance expertise, using plain language, visual cues, and zero jargon to monitor home property insurance claim progress."
version: "0.1.0"
tags:
  - "claim-tracking"
  - "family-communication"
  - "accessibility"
  - "template"
triggers:
  - "给家人看得懂的状态追踪表"
  - "simple claim tracker for family"
  - "non-technical insurance status table"
  - "printable claim progress sheet for elders"
---

# family-property-claim-status-tracker-for-family

A reusable, non-technical status tracking table designed for family members with no insurance expertise, using plain language, visual cues, and zero jargon to monitor home property insurance claim progress.

## Prompt

# Goal
Generate a printable, mobile-friendly claim status tracker table that any family member (e.g., elder parent, teen, non-insurance professional) can understand at a glance — no insurance terms, no legal references, no acronyms. Output only the table (no explanations, no headers like 'Table:' or 'Below is...').

# Constraints & Style
- Language: Simple, active-voice Chinese; avoid all insurance jargon (e.g., say 'damage check' not 'loss adjustment', 'pay out' not 'indemnification', 'company' not 'insurer').
- Structure: Exactly 5 columns — Date | What Happened | Who Did It | Next Step | When Due (use relative phrasing: 'in 3 days', 'by Friday', 'after photos').
- Visual clarity: Use ✅ for done, ⏳ for in progress, ❓ for waiting, 🚨 for overdue — no text in status cells.
- De-identify: Replace all case-specific identifiers with placeholders: <POLICY_NUMBER>, <CLAIM_ID>, <EVENT_TYPE> (e.g., 'kitchen leak', 'storm roof damage').
- No dates, names, or contact details — only relative timing and role-based actors ('company rep', 'us', 'electrician').
- Never include legal citations, clauses, or procedural advice — this is *only* a status log, not guidance.
- Output format: Markdown table only — no extra lines, no code fences, no footnotes.

# Workflow
None — this is a static template generation task. Do not add steps, instructions, or commentary.

## Triggers

- 给家人看得懂的状态追踪表
- simple claim tracker for family
- non-technical insurance status table
- printable claim progress sheet for elders
