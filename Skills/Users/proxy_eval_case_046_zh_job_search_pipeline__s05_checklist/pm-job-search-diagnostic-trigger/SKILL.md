---
id: "f26f1528-fcb4-48f1-a315-18e0659c8f49"
name: "pm-job-search-diagnostic-trigger"
description: "A time-bound, outcome-aligned PM job search plan that automatically initiates a structured diagnostic workflow when outreach reply rate falls below 8%, to identify and correct engagement bottlenecks."
version: "0.1.0"
tags:
  - "diagnostic"
  - "outreach"
  - "reply-rate"
  - "product-manager"
  - "job-search"
triggers:
  - "reply rate below 8%"
  - "low response rate diagnosis"
  - "referral message not working"
  - "outreach not getting replies"
  - "PM job search stuck"
---

# pm-job-search-diagnostic-trigger

A time-bound, outcome-aligned PM job search plan that automatically initiates a structured diagnostic workflow when outreach reply rate falls below 8%, to identify and correct engagement bottlenecks.

## Prompt

# Goal
Automatically trigger a lightweight, evidence-based diagnostic process when the user's referral or outreach reply rate drops below 8% across any 7-day rolling window — focused on identifying root causes (e.g., message relevance, timing, targeting) and generating actionable, low-effort corrections.

# Constraints & Style
- ✅ Trigger only on measured reply rate < 8% (calculated as: replies ÷ total outbound messages in last 7 days)
- ✅ Diagnostic must be completed in ≤45 minutes; output must fit in one screen (no multi-page reports)
- ✅ Do NOT assume intent, sentiment, or internal hiring process — only analyze observable user actions: message copy, recipient profile, send time, channel (e.g., LinkedIn vs. Maimai), and response pattern
- ✅ Must distinguish between *zero replies* (targeting/messaging failure) and *low replies* (e.g., 2/30 = 6.7%) — each requires different diagnostics
- ❌ Do NOT invent metrics, benchmarks, or platform-specific algorithms not grounded in user-provided data
- ❌ Do NOT require external tools, APIs, or login access

# Workflow
1. Confirm trigger: compute reply rate from user’s last 7 days of outreach log (if unavailable, ask for 3 most recent sent messages + reply status)
2. Classify failure mode:
   - Mode A (Zero replies): check for missing personalization, generic opener, or mismatched recipient seniority/function
   - Mode B (Low replies): audit message length (< 90 chars), specificity of reference (e.g., named feature + observation), and call-to-action clarity
3. Output exactly 3 prioritized fixes — each phrased as an editable template (e.g., 'Replace "Hi, I’m preparing for PM roles" → "Hi [Name], I just used [Product]’s new [Feature] flow — noticed [specific observation]; would love your take on the trade-off you made there."')
4. Suggest one micro-test for next 3 messages (e.g., 'Try sending only on Tuesday 10–11am, referencing a feature launched <7 days ago')

## Triggers

- reply rate below 8%
- low response rate diagnosis
- referral message not working
- outreach not getting replies
- PM job search stuck
