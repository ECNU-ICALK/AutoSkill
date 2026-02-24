---
id: "313495bf-970a-4e28-bf06-ca76b8e0c4dc"
name: "weekly-job-search-review-and-planning"
description: "A time-boxed weekly review and planning ritual for job seekers, enforcing strict ≤12-hour/week commitment while generating actionable next steps, outcome-based validation, and automatic diagnostic response when reply rate falls below 8%."
version: "0.1.1"
tags:
  - "job-search"
  - "time-management"
  - "feedback-loop"
  - "execution-template"
  - "diagnostic-trigger"
triggers:
  - "weekly job search review"
  - "what should I do next week"
  - "review my progress"
  - "create my action plan"
  - "fallback mode"
---

# weekly-job-search-review-and-planning

A time-boxed weekly review and planning ritual for job seekers, enforcing strict ≤12-hour/week commitment while generating actionable next steps, outcome-based validation, and automatic diagnostic response when reply rate falls below 8%.

## Prompt

# Goal
Generate a concise, copy-paste-ready weekly review template and a prioritized list of ≤3 high-leverage action items for the coming week — all aligned to the user’s strict ≤12h/week constraint and real-time performance data (especially reply rate vs. 8% threshold).

# Constraints & Style
- Output must be fully de-identified: no names, companies, tools, platforms, or personal details — use placeholders like <TARGET_ROLE>, <JD_SOURCE>, or <CHANNEL>.
- Use plain Markdown only: no tables, no alignment syntax, no emojis, no bold/italic beyond headers and checklist bullets, no decorative symbols (e.g., ✅, 📌, ➕).
- Review template must be fill-in-the-blank, single-level, and require zero formatting effort — ready to paste into any note app or chat.
- Action items must be verb-led, time-estimated (in hours), and include *only* what’s needed to execute: tool-agnostic templates, placeholder-driven phrasing, or one-click link patterns — no explanations.
- If reply_rate < 8%, output diagnostic action(s) as top priority using only these three root causes: channel imbalance, low resume open rate, or low JD match — no new root causes.
- Total estimated time across all action items must sum to ≤12 hours; explicitly state remaining buffer time.
- Include a 'Fallback Mode' section: exactly 3 sub-30-minute actions that preserve momentum if full weekly load isn’t possible.
- Never suggest open-ended learning, portfolio expansion, or tool mastery — only actions with direct, near-term hiring impact.
- Never invent metrics, thresholds, or tools not previously confirmed by the user.

# Workflow
1. Accept filled-in review input (time spent, reply rate, key results, 1 insight, 1 small improvement).
2. Compute reply rate; if < 8%, activate diagnostic logic using only the three root causes: channel imbalance, low resume open rate, or low JD match.
3. Derive action items that directly address the most probable root cause *and* the user’s stated time friction (e.g., 'resume editing took too long' → inject templated phrasing).
4. If triggered: output only the 3-step diagnostic flow (Step 1: 3-question attribution; Step 2: prescriptive fix pack; Step 3: verification protocol) — no explanations, no options.
5. If not triggered: output two sections — (A) Weekly Review Template (fields: wins, gaps, metric snapshot, lesson) and (B) Next Week’s Action Plan (≤3 numbered, time-estimated actions + Fallback Mode + explicit buffer time statement).

## Triggers

- weekly job search review
- what should I do next week
- review my progress
- create my action plan
- fallback mode
