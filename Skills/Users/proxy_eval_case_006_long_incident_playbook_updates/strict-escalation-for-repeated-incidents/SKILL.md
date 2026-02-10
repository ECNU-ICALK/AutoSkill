---
id: "40775845-e6ce-4f74-a9ac-38929cd4f083"
name: "strict-escalation-for-repeated-incidents"
description: "A reusable incident response policy that enforces stricter escalation rules when the same or related failure patterns recur within a 24-hour window, triggering automatic cross-team engagement and change freezes."
version: "0.1.0"
tags:
  - "incident-response"
  - "escalation"
  - "sre"
  - "policy"
  - "automation-readiness"
triggers:
  - "escalate repeated incidents faster"
  - "strict escalation for 24h recurrence"
  - "auto-war-room on incident repeat"
  - "freeze changes after repeat failure"
  - "enforce repeat-incident policy"
---

# strict-escalation-for-repeated-incidents

A reusable incident response policy that enforces stricter escalation rules when the same or related failure patterns recur within a 24-hour window, triggering automatic cross-team engagement and change freezes.

## Prompt

# Goal
Enforce stricter, time-bound escalation rules for incidents that represent a recurrence of the same failure pattern (e.g., identical service, error signature, or root cause category) within a 24-hour period — regardless of severity level.

# Constraints & Style
- A 'repeated incident' is defined as: (a) same impacted service or component (e.g., `auth-service`, `payments-api`), AND (b) same primary error class (e.g., `504 gateway timeout`, `connection pool exhaustion`, `JWT validation failure`) confirmed via logs/metrics, AND (c) onset within 24 hours of prior incident resolution.
- Upon detection of a repeated incident:
  • SEV-0/SEV-1: Immediate war room activation (no delay); IC must brief executive leadership within **3 minutes**, not 10.
  • All severities: Automatic freeze on *all* non-critical deployments and config changes across the affected service’s dependency graph (including upstream/downstream services) — enforced via CI/CD gate.
  • Escalation to Engineering Director is mandatory at T+5 min (not T+10 or later), with documented rationale if deferred.
- No manual override of these escalation rules without real-time approval from both IC and Engineering Director — logged immutably in incident timeline.
- Language must remain factual and metric-based: e.g., *"Auth-service 504 rate >95% for 2nd time in 18h — auto-escalating per repeat-failure policy"*, not *"This keeps happening!"*
- Do not infer recurrence from vague similarity; require explicit match on service identifier + error signature + timestamp window.

# Workflow
1. At incident declaration, check for open or resolved incidents matching service + error class in last 24h (use Jira/PagerDuty/Grafana annotations).
2. If match found, apply strict escalation rules immediately — no waiting for first update cycle.
3. Post confirmation message in `#incident-response`: "REPEAT-DETECTED: [Service] [Error] — strict escalation engaged. War room active. Change freeze in effect."
4. Log all bypass attempts (with approvers and justification) in incident timeline.

## Triggers

- escalate repeated incidents faster
- strict escalation for 24h recurrence
- auto-war-room on incident repeat
- freeze changes after repeat failure
- enforce repeat-incident policy
