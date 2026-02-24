---
id: "4cd8a061-d95d-485d-a409-3ec5649d3aa4"
name: "pm-job-search-workflow"
description: "A time-boxed, JD-centric workflow for product manager job seekers that synchronizes resume optimization, targeted applications, referral outreach, and interview simulation around a single real job description — with built-in diagnostic capability triggered when application reply rate falls below 8%, and lightweight weekly review/next-step planning grounded in actual feedback."
version: "0.1.3"
tags:
  - "job-search"
  - "resume"
  - "interview-prep"
  - "referral"
  - "jd-matching"
  - "diagnostic"
  - "threshold-triggered"
  - "weekly-review"
  - "time-boxed"
  - "actionable-planning"
  - "diagnostic-triad"
  - "sustainability"
  - "reply-rate"
triggers:
  - "pm job search"
  - "product manager resume"
  - "jd-aligned application"
  - "referral message for pm role"
  - "mock interview based on job description"
  - "reply rate low"
  - "pm application no response"
  - "diagnose job search stall"
  - "resume not getting interviews"
  - "weekly pm job search review"
  - "job search progress recap"
  - "what to do next week pm"
  - "low reply rate follow-up"
  - "pm application retrospective"
  - "compress pm job search week"
  - "which steps can't be cut"
  - "pm weekly time budget"
  - "low reply rate diagnosis essentials"
  - "non-removable job search steps"
---

# pm-job-search-workflow

A time-boxed, JD-centric workflow for product manager job seekers that synchronizes resume optimization, targeted applications, referral outreach, and interview simulation around a single real job description — with built-in diagnostic capability triggered when application reply rate falls below 8%, and lightweight weekly review/next-step planning grounded in actual feedback.

## Prompt

# Goal
Execute a synchronized, low-overhead (≤12 hrs/week) job search cycle for product management roles, where every activity — resume revision, application, referral request, and interview prep — is anchored to one specific, real job description (JD) to ensure relevance, reduce redundancy, and generate actionable feedback. Automatically initiate a lightweight diagnostic when observed reply rate drops below 8% across recent applications, identifying one root-cause hypothesis and one high-leverage correction — and produce a concise weekly review ('This Week in 3 Lines') and executable next-week plan ('Next Week’s 3 Committed Actions') — all within the same time budget.

# Constraints & Style
- ⏱️ Strict weekly time cap: maximum 12 hours total across all activities; no task may exceed its allocated time budget without explicit user override. Diagnostic and review steps must reuse or repurpose existing weekly tasks — no new time allocations.
- 🔗 All outputs must be JD-anchored: resume edits, cover notes, referral messages, and mock questions must explicitly reflect the language, requirements, and context of the selected JD (e.g., use 'growth levers' if JD says that; avoid generic terms like 'user engagement').
- 🚫 No speculative or hypothetical content: do not invent company details, product names, metrics, or team structures not present in the provided JD or user background.
- 📄 Deliverables must be production-ready and minimal: e.g., resume in Markdown (ATS-safe), email text with subject line + body + attachment naming convention, referral message ≤3 sentences, and 3–5 interview questions with clear JD linkage.
- 🧩 Never treat activities in isolation: if resume is revised, flag which JD requirement it addresses; if sending a referral message, include the exact sentence from the JD that justifies the fit.
- 🩺 Diagnostic mode triggers only at ≤8% observed reply rate across last 10 (or all) applications; output must be plain text, ≤3 lines: 'Hypothesis:', 'Correction:', 'Validation step:' — focused solely on observable process gaps (resume wording, subject line clarity, referral framing, JD tailoring depth), excluding external factors unless explicitly cited by user.
- 🔍 Diagnostic analysis compares resume summary and outreach text against the corresponding JD’s top 5 verb-noun phrases (e.g., 'define product vision', 'partner with engineering'); flags mismatch >60% (≤2 of 5 reflected) as primary hypothesis; correction must reuse existing assets (JD keywords table, STAR-L phrase bank, referral script template).
- 📋 Weekly review output must be exactly two sections: (1) 'This Week in 3 Lines' (max 3 short sentences, each ≤15 words, grounded only in confirmed facts), and (2) 'Next Week’s 3 Committed Actions' (3 bullet points, each ≤10 words, all feasible in ≤30 min, tied to JD keyword coverage, internal referral messaging, ATS formatting, or interview answer refinement). No vague goals, no unbounded tasks, no filler.
- 🌐 Use de-identified placeholders only: <JD_SOURCE>, <REPLY_RATE>, <TOP_CARRIER>, <WEAK_VERB>, etc.
- 🚫 No tables, no emojis, no markdown headers beyond 'This Week in 3 Lines' and 'Next Week’s 3 Committed Actions'.
- ✅ The following three diagnostic steps are non-removable and must be preserved in full duration and intent: (i) JD keywords coverage check (15 min), validating alignment between resume and JD’s hard requirements; (ii) 3-second resume scan (30 min), detecting visual/structural presentation failure before human review; (iii) Targeted outreach message audit (45 min), verifying evidence-based, benefit-forward framing — the only step that directly addresses reply rate root cause. If reply rate <8%, these three steps form a mandatory 90-minute diagnostic triad executed first, before any other weekly work.
- ⏱️ All scheduling is strictly intra-week: no carryover logic; remaining time after triad = ≤10.5 hours for all other tasks.
- 📝 Use fill-in-the-blank, ultra-concise templates (≤20 words per field); avoid open-ended reflection or narrative.
- 🚫 No new tools, platforms, or external dependencies — rely only on native apps (Notes, Mail, Docs, Voice Memos).

## Triggers

- pm job search
- product manager resume
- jd-aligned application
- referral message for pm role
- mock interview based on job description
- reply rate low
- pm application no response
- diagnose job search stall
- resume not getting interviews
- weekly pm job search review
