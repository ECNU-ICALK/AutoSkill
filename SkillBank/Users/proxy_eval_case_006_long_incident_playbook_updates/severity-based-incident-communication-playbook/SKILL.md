---
id: "109f0f8d-eded-43ee-8ca0-cea8500773a8"
name: "severity-based-incident-communication-playbook"
description: "A reusable playbook that enforces factual, blame-free communication during service incidents, with strict timing, channel, and approval rules tied to severity levels."
version: "0.1.0"
tags:
  - "incident-response"
  - "communication-policy"
  - "severity-tiering"
  - "blameless-culture"
triggers:
  - "define incident communication timeline"
  - "set update frequency by severity"
  - "enforce factual incident comms"
  - "avoid blame in outage messaging"
  - "standardize status updates"
---

# severity-based-incident-communication-playbook

A reusable playbook that enforces factual, blame-free communication during service incidents, with strict timing, channel, and approval rules tied to severity levels.

## Prompt

# Goal
Generate a severity-tiered incident communication plan for an online service outage, specifying mandatory internal/external update frequencies, channels, approval requirements, and tone rules — all aligned to SEV-0 through SEV-3.

# Constraints & Style
- ✅ Use only factual, observable language: state *what is happening*, *what is impacted*, *what is being done*, and *when the next update will occur*. Never attribute cause to people, teams, or roles (e.g., avoid "dev team misconfigured", "SRE missed alert").
- ✅ Prohibit blame language entirely: no names, no role-based fault assignment, no speculative root cause in comms (e.g., avoid "likely due to recent deploy"; say "investigating correlation with latest release" only if verified).
- ✅ Enforce severity-specific cadence: SEV-0 = internal every 5 min, external every 15 min; SEV-1 = internal every 15 min, external every 30 min; SEV-2 = internal every 30–60 min, external ≤2 hrs (status page only); SEV-3 = no real-time comms.
- ✅ Require pre-approved templates for all updates — include placeholders for Status, Impact, Action, Next Update, and Owner (role, not name).
- ✅ Mandate explicit owner *role* (e.g., "Tech Lead", "Communicator") in every internal update — never individual names.
- ❌ Do not invent escalation paths, tool integrations, or training workflows unless explicitly requested.
- ❌ Do not include implementation checklists, drill suggestions, or asset offers (e.g., cheat sheets, bot scripts) — those are one-off delivery options, not reusable policy.

# Workflow
None — this is a policy-driven output specification, not a multi-stage AI operation.

## Triggers

- define incident communication timeline
- set update frequency by severity
- enforce factual incident comms
- avoid blame in outage messaging
- standardize status updates
