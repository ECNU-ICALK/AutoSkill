---
id: "1cc80c17-e9f7-4503-a047-c495ce47e71f"
name: "behavior-based-user-interview-protocol"
description: "A reusable, time-boxed (≤20 min), consent-aware protocol for conducting remote user interviews that prioritize observable behaviors and concrete actions over subjective opinions, hypothetical preferences, or leading assumptions — and includes a standardized rubric to score and prioritize recurring pain points across interviews."
version: "0.1.3"
tags:
  - "user-research"
  - "interview-design"
  - "behavioral-evidence"
  - "ux-research"
  - "consent"
  - "non-leading"
  - "pain-point-prioritization"
  - "time-boxed"
  - "remote"
triggers:
  - "focus on behavior-based questions"
  - "avoid opinion-only questions"
  - "avoid leading questions"
  - "add consent script"
  - "interview protocol grounded in actions"
  - "elicit real usage not preferences"
  - "add a scoring rubric for prioritizing recurring pain points"
  - "prioritize observable actions over opinions"
  - "20-minute remote interview"
  - "concise behavior-based interview"
  - "time-boxed analytics interview"
  - "remote user research under 20 minutes"
---

# behavior-based-user-interview-protocol

A reusable, time-boxed (≤20 min), consent-aware protocol for conducting remote user interviews that prioritize observable behaviors and concrete actions over subjective opinions, hypothetical preferences, or leading assumptions — and includes a standardized rubric to score and prioritize recurring pain points across interviews.

## Prompt

# Goal
Generate a user interview protocol focused exclusively on eliciting behavior-based evidence — actions users have taken, tools they have used, decisions they have made, and sequences they have followed — rather than opinions, preferences, intentions, or imagined future usage. After interviews, apply a consistent rubric to score and prioritize recurring pain points based on frequency, severity, and scope.

# Constraints & Style
- Strict time budget: 20 minutes total. Allocate: 2 min consent + 14 min core questions + 4 min wrap-up/closing. Stop at 20:00 — even mid-sentence.
- Begin with a concise, plain-language consent script covering recording, data use, anonymity, and the right to skip or stop — read aloud verbatim and confirm verbal agreement before proceeding. No note-taking during consent or sensitive moments; use silent recording (with consent) or brief bullet-style capture only during behavioral narration.
- All questions must be grounded in past or current behavior, anchored to recent, specific instances (e.g., 'last time', 'most recent', 'yesterday', 'this week'); avoid 'usually', 'generally', or speculative frames like 'in an ideal world'.
- Eliminate all opinion-only, preference-only, importance-, or intention-based phrasing: no 'What do you think?', 'How would you like…?', 'What would make X better?', 'What do you prefer?', 'How important is Y?', 'Would you use Z?', or 'What does [term] mean to you?'.
- Avoid hypotheticals and ideals unless explicitly tied to a recent real instance (e.g., 'When was the last time you tried to…? What happened?').
- Prohibit leading language: do not embed assumptions (e.g., avoid 'How did you fix the slow load time?' → instead ask 'What did you do the last time the dashboard took >5 seconds to load?').
- Prioritize sequencing, timing, artifacts (screenshots, reports, dashboards), workarounds, and UI-level detail as evidence sources.
- Use neutral, non-leading, action-oriented probing: replace 'Why did you…?' with 'What happened next?', 'What did you do after seeing that?', or 'And then what did you do?'. Limit follow-ups to *one* per answer: only 'And then what did you do?' or 'What did the screen show next?'.
- If participant offers opinion or speculation: gently redirect using *only* this phrase: 'To keep this grounded in behavior — could you tell me about a time you *actually did* something like that? What did you click, type, or send?'
- Limit to 5 core questions max — selected from high-yield categories (one per category): Workflow, Decision trigger, Workaround, Failure, Environment — each phrased neutrally and anchored in recency.
- After interviews, extract discrete pain points as verbatim behavioral breakdowns (e.g., 'manually reformatting CSV before pasting into Slack'); do not interpret, summarize, or infer motivation.
- Apply a standardized pain-point scoring rubric per unique pain point: assign scores (1–3) on Frequency (how many participants independently reported this *same specific behavior breakdown*), Severity (time/effort/risk of workaround), and Scope (solo → team → org-wide impact); total score = sum; only pain points scoring ≥6 are elevated for design prioritization.

# Workflow
1. Start timer. Read consent script verbatim; confirm verbal agreement.
2. Ask exactly 5 pre-selected questions — one from each category (Workflow, Decision trigger, Workaround, Failure, Environment) — phrased neutrally and anchored in recency.
3. For every question, verify it asks for a specific, dated, or contextualized action — not an evaluation, definition, preference, or assumption.
4. During interview: Ask only behavior-anchored questions; use at most one neutral follow-up per answer ('And then what did you do?' or 'What did the screen show next?').
5. Replace any remaining opinion-based, hypothetical, leading, or abstract question with its behavior-anchored equivalent before finalizing.
6. For each response, apply real-time behavioral probing: request chronological sequencing, exact copy/paste text, screen-sharing cues, or artifact references — without introducing assumptions.
7. At 18:00, begin wrap-up: thank participant, reiterate anonymity, offer opt-in for follow-up.
8. After each interview: Extract discrete pain points as verbatim behavioral sequences — avoid aggregating across participants yet.
9. After all interviews: For each unique pain point, apply the 3-dimension rubric across all participant evidence.
10. Output: Ranked list of pain points with total scores and supporting behavioral quotes (de-identified).

## Triggers

- focus on behavior-based questions
- avoid opinion-only questions
- avoid leading questions
- add consent script
- interview protocol grounded in actions
- elicit real usage not preferences
- add a scoring rubric for prioritizing recurring pain points
- prioritize observable actions over opinions
- 20-minute remote interview
- concise behavior-based interview
