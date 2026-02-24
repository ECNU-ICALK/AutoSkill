---
id: "1f4f1c57-ed64-46d1-a919-9cfa5848e986"
name: "risk-graded-gray-release-with-auto-escalation"
description: "Dynamically sets gray release parameters (initial traffic ratio, observation duration, expansion thresholds) based on pre-assessed change risk level (L1–L4), and automatically escalates to the appropriate on-call owner upon two consecutive metric violations within identical, risk-defined observation windows."
version: "0.1.2"
tags:
  - "gray-release"
  - "risk-management"
  - "observability"
  - "escalation"
  - "sre"
  - "incident-response"
triggers:
  - "连续两次异常自动升级"
  - "灰度期指标连击告警"
  - "双周期阈值突破升级"
  - "风险分级灰度加自动上报"
---

# risk-graded-gray-release-with-auto-escalation

Dynamically sets gray release parameters (initial traffic ratio, observation duration, expansion thresholds) based on pre-assessed change risk level (L1–L4), and automatically escalates to the appropriate on-call owner upon two consecutive metric violations within identical, risk-defined observation windows.

## Prompt

# Goal
Execute a risk-adaptive gray release with automatic escalation: for a given change, apply pre-approved gray parameters per its L1–L4 risk level, monitor key metrics in strict observation windows, and trigger immediate, auditable escalation to the designated on-call owner if *the same hard metric violates its threshold in two consecutive observation windows*.

# Constraints & Style
- Initial gray ratio, observation window length, and expansion thresholds are strictly determined by risk level (L1–L4) — no manual override.
- "Consecutive" means two back-to-back, full-length, non-overlapping observation windows (e.g., two 30-min windows for L3); not arbitrary or overlapping time slices.
- Escalation is only triggered when the same metric breaches its defined threshold in two consecutive evaluation intervals; single or intermittent breaches do not qualify.
- Escalation must include: (1) exact metric name and threshold, (2) timestamps of both violations, (3) current gray ratio and risk level, (4) direct @mention of the on-call owner (via enterprise IM webhook), plus automated phone call, Jira incident ticket creation, and a 5-minute response countdown.
- Escalation is not a rollback trigger — it is a human-in-the-loop alert for urgent review; rollback still requires explicit satisfaction of defined Hard Rollback conditions and dual confirmation for L3/L4.
- All escalation logic must be implemented as stateful checks in monitoring pipeline (e.g., Prometheus recording rule + Alertmanager silencing/labeling), not client-side heuristics.
- No skipping observation windows or jumping gray ratios (e.g., 0.5% → 50%).
- Escalation is platform-enforced and globally enabled — cannot be disabled.
- Output must be concise, actionable, and optimized for rapid execution by an on-call engineer under pressure — avoid explanations, rationale, or background.
- Escalation target mapping: L1/L2 → SRE, L3 → Tech Lead, L4 → Tech Director.
- Require explicit 'acknowledged' signal (e.g., button click) to stop response timer; timeout triggers secondary alert.
- Present exactly three irreversible options: [Continue], [Hold], [Rollback].

# Workflow
1. At gray release start, load risk level (L1–L4) from release metadata (e.g., `release-risk-level` annotation).
2. Load corresponding gray strategy (ratio, window, thresholds) from central config (e.g., Nacos).
3. Start gray with initial ratio; begin first observation window timer.
4. For each metric (e.g., `error_rate`, `p95_latency`), evaluate at end of each full observation window using rolling window aggregation.
5. Maintain per-metric violation history: record timestamp of each breach; reset history on clean pass.
6. If any metric has ≥2 consecutive breach timestamps within last 2×window minutes → immediately freeze gray ratio, call on-call owner, send structured IM alert with version, risk level, metric delta, and Grafana link, create Jira incident ticket, and start 5-minute response countdown.
7. Log full audit trail (timestamps, metric snapshots, call ID, response confirmation, trace ID, and responsible roles).

## Triggers

- 连续两次异常自动升级
- 灰度期指标连击告警
- 双周期阈值突破升级
- 风险分级灰度加自动上报
