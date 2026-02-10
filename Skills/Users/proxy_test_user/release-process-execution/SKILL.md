---
id: "aa02690c-7c3d-486f-97f5-21d1759805b0"
name: "release-process-execution"
description: "Executes a standardized, phased software release process including regression testing, canary deployment, monitoring, and full rollout."
version: "0.1.2"
tags:
  - "release"
  - "deployment"
  - "sre"
  - "phased-rollout"
  - "testing"
  - "canary"
  - "monitoring"
  - "regression"
triggers:
  - "run release process"
  - "execute phased release"
  - "before release: run regression, canary, monitor, full rollout"
  - "follow release checklist"
  - "Execute phased rollout"
  - "Start deployment sequence"
---

# release-process-execution

Executes a standardized, phased software release process including regression testing, canary deployment, monitoring, and full rollout.

## Prompt

# Goal
Execute a safe, incremental software release process as defined by the user's operational sequence.

# Constraints & Style
- Must follow the exact four-phase order: (1) run regression tests, (2) deploy to a canary environment, (3) monitor canary behavior and key metrics, (4) proceed to full production rollout.
- Do not skip, reorder, or merge phases.
- Do not invent tools, thresholds, success criteria, or implementation details — those are external inputs; this skill only enforces the phase sequence and intent.
- Treat 'monitor' as a required step with no implicit success threshold unless explicitly specified by the user.
- Full rollout must only occur after monitoring is completed; however, do not infer or enforce stability criteria unless explicitly provided by the user.
- Output must reflect strict adherence to this sequence; do not generate code, tooling details, or configuration unless explicitly requested.

# Workflow
1. Execute regression testing.
2. Deploy to canary environment.
3. Monitor system behavior and performance indicators.
4. Perform full rollout to production.

## Triggers

- run release process
- execute phased release
- before release: run regression, canary, monitor, full rollout
- follow release checklist
- Execute phased rollout
- Start deployment sequence
