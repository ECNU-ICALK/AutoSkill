---
id: "82d36c7f-5c9e-4b2b-a674-3c2ca300b07a"
name: "online-release-process-with-validation-criteria"
description: "A systematic online release process with explicitly defined pass/fail conditions and monitoring thresholds for regression testing, canary release, monitoring observation, and full rollout stages."
version: "0.1.0"
tags:
  - "release-management"
  - "canary-release"
  - "monitoring"
  - "devops"
  - "validation-criteria"
triggers:
  - "release process with validation criteria"
  - "canary deployment thresholds"
  - "monitoring metrics for deployment"
  - "full rollout approval process"
---

# online-release-process-with-validation-criteria

A systematic online release process with explicitly defined pass/fail conditions and monitoring thresholds for regression testing, canary release, monitoring observation, and full rollout stages.

## Prompt

# Goal
Implement a controlled online release process with clear validation criteria at each stage: regression testing must pass, canary release must meet stability thresholds, monitoring observation must show no anomalies, and full rollout requires explicit approval based on metrics.

# Constraints & Style
- **Regression Testing Pass Criteria**: Automated test coverage ≥ 80% on core business flows, manual test report signed-off, database state validated for consistency
- **Canary Release Rules**: Start with 5-10% user traffic, observe minimum 30 minutes, monitor error rate < 1%, response time < 1s, proceed to 20% only if stable
- **Monitoring Thresholds**: Critical alert if error rate > 1% or response time > 2s, business metrics must maintain baseline (±5% variance), log error rate < 0.5%
- **Full Rollout Requirements**: All canary metrics stable for 60+ minutes, no critical bugs reported, explicit approval via change management process
- **Rollback Triggers**: Error rate > 2% or response time > 3s for 5+ minutes, or user complaints exceeding threshold
- **Documentation**: Every release must record version number, change details, timestamps, and responsible personnel in a centralized log

# Workflow
1. **Pre-Release Preparation**: Branch creation, code review, static analysis, backup creation
2. **Regression Testing Execution**: Run automated test suite, manual validation, database consistency check, produce sign-off report
3. **Canary Release**: Deploy to 5-10% traffic, set observation window, monitor specified metrics, document findings
4. **Monitoring Observation**: Continuously track technical/business metrics, set threshold-based alerts, generate monitoring report
5. **Full Rollout Decision**: Review canary results and monitoring data, obtain approval, redirect 100% traffic
6. **Post-Launch Validation**: Execute final health check, update documentation, schedule retrospective

## Triggers

- release process with validation criteria
- canary deployment thresholds
- monitoring metrics for deployment
- full rollout approval process
