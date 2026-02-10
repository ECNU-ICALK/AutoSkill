---
id: "9169ed88-3b44-4f92-9d19-10f031a8c320"
name: "severity-based-rollback-and-mitigation-checkpoints"
description: "A reusable incident response capability that defines explicit, severity-tied go/no-go criteria for rollback and mitigation actions — ensuring decisions are objective, timely, and decoupled from individual judgment."
version: "0.1.1"
tags:
  - "incident-response"
  - "sre"
  - "on-call"
  - "rollback"
  - "mitigation"
  - "decision-gates"
  - "observability"
  - "escalation"
triggers:
  - "define rollback go-no-go criteria"
  - "set mitigation decision thresholds"
  - "add objective incident action gates"
  - "enforce timebound recovery checks"
  - "tie rollback to observable metrics"
  - "compress incident playbook for on-call"
  - "generate concise incident response cheat sheet"
  - "distill rollback and escalation rules"
  - "create on-call engineer incident checklist"
  - "make playbook skimmable under pressure"
---

# severity-based-rollback-and-mitigation-checkpoints

A reusable incident response capability that defines explicit, severity-tied go/no-go criteria for rollback and mitigation actions — ensuring decisions are objective, timely, and decoupled from individual judgment.

## Prompt

# Goal
Enforce objective, severity-aligned rollback and mitigation checkpoints during service incidents — each with verifiable go/no-go criteria based on real-time metrics, time bounds, and impact thresholds. Output a clear decision log entry indicating 'GO', 'NO-GO', or 'PENDING' for each checkpoint.

# Constraints & Style
- All criteria must be observable, measurable, and tooling-ready (e.g., Prometheus queries, Datadog monitors, SLO burn rates) — no subjective phrases like 'seems stable' or 'looks better'.
- Use only factual, actor-neutral language: state *what is observed* and *what action is taken*, never *who decided* or *why it failed*.
- For each severity level (SEV-0 to SEV-2), define exactly one primary rollback checkpoint and one primary mitigation checkpoint — both with:
  • Trigger condition (e.g., "error rate > 5% for 90s")
  • Verification method (e.g., "validate via /health endpoint + latency histogram")
  • Timebound (e.g., "must complete within 4 minutes of trigger")
  • Go/no-go threshold (e.g., "GO if 95%+ requests succeed for 60s post-action; else NO-GO")
- SEV-3 has no formal checkpoints — handled via backlog workflow.
- Never include blame, speculation, root cause assertions, or unverifiable status (e.g., 'investigating', 'working on fix').
- Output format: a markdown table with columns: Severity | Checkpoint Type | Trigger | Verification | Timebound | Go/No-Go Threshold | Decision Log Example.
- Compress output into a single, scannable document under 300 words using only bold headers, bullet points, and compact tables — no paragraphs, explanations, code blocks, callouts, emojis, links, or footnotes.
- Retain only metric- or artifact-based criteria (e.g., 'error_rate > 1.5%', 'rollback artifact signed and tested', '72 min stability verified').
- Replace all instance-specific references with generic, de-identified terms: 'service', 'component', 'API', 'DB', 'domain'.
- Enforce strict role-based ownership (e.g., 'Technical Lead', 'SRE', 'IC') — never individuals or teams.
- Language: English only; imperative tone; present tense.

## Triggers

- define rollback go-no-go criteria
- set mitigation decision thresholds
- add objective incident action gates
- enforce timebound recovery checks
- tie rollback to observable metrics
- compress incident playbook for on-call
- generate concise incident response cheat sheet
- distill rollback and escalation rules
- create on-call engineer incident checklist
- make playbook skimmable under pressure
