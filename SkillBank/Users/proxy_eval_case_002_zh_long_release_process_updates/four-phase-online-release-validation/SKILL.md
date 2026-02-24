---
id: "d16d3f27-a7df-48e9-963d-ac00c74f2a68"
name: "four-phase-online-release-validation"
description: "A reusable, threshold-driven online release validation workflow covering regression testing, canary release, real-time monitoring observation, and full rollout — with explicit, user-specified pass/fail conditions, numeric monitoring thresholds, fixed observation windows, and role-scoped rollback authority."
version: "0.1.1"
tags:
  - "release-process"
  - "validation"
  - "threshold-based"
  - "canary"
  - "monitoring"
  - "rollback-policy"
  - "sre"
triggers:
  - "定义发版各阶段通过条件"
  - "明确监控阈值"
  - "设置灰度终止标准"
  - "制定回归测试准入门槛"
  - "规定全量发布触发条件"
  - "指定谁有权执行回滚"
---

# four-phase-online-release-validation

A reusable, threshold-driven online release validation workflow covering regression testing, canary release, real-time monitoring observation, and full rollout — with explicit, user-specified pass/fail conditions, numeric monitoring thresholds, fixed observation windows, and role-scoped rollback authority.

## Prompt

# Goal
Execute a four-phase online release validation process: (1) regression testing, (2) canary release, (3) real-time monitoring observation, and (4) full rollout — each phase must only proceed upon strict, quantifiable pass criteria. Output a clear go/no-go decision per phase, citing observed metrics vs. defined thresholds.

# Constraints & Style
- All pass conditions must be concrete, numeric, and user-specified — no vague terms like 'stable', 'acceptable', or 'looks fine'.
- Monitoring thresholds must be expressed as absolute values or bounded % deviations (e.g., 'P95 latency ≤ 800ms', 'error rate < 0.1%', 'performance deviation ≤ ±15%', 'baseline × 1.15').
- Reject any phase if *any* required threshold is violated — no partial passes, subjective overrides, or manual bypasses.
- Rollback is mandatory on violation: auto-triggered where defined; otherwise, executed only by authorized roles (SREs and Tech Leads) via pre-validated script (e.g., `./rollback.sh <prev_version>`) with dual-person confirmation (operator + verifier) and MFA.
- All time-bound conditions use strict, uninterrupted rolling windows (e.g., '≥20 consecutive minutes') — interruption resets the timer.
- Do not invent thresholds, strategies, tools, or roles; only use those explicitly confirmed by the user in this thread.
- Output decisions in plain language with metric names, observed values (if provided), and threshold comparisons — no markdown tables or decorative formatting.
- Never assume environment, stack, or tooling — keep logic stack-agnostic unless user specifies integration (e.g., K8s, Nacos).

# Workflow
1. Regression Testing Phase:
   - Verify: (a) 100% pass rate on P0/P1 automated test cases; (b) zero new P0/P1 defects; (c) core interface P95 latency within ±10% of prior version baseline.
   - → Proceed only if all three are satisfied.

2. Canary Release Phase:
   - Monitor for minimum duration (≥30 min; ≥2 hr for major changes).
   - Terminate immediately if *any* occurs: (a) error rate > 0.5%; (b) core interface P95 latency increase > 50%; (c) critical resource anomaly (e.g., DB connection pool exhausted, OOM, thread deadlock).
   - → Proceed to observation only if no termination condition triggered.

3. Monitoring Observation Phase:
   - Validate against four dimensions using these exact thresholds:
     • Availability: HTTP 5xx error rate < 0.1% AND service health probe success rate ≥ 99.9%;
     • Performance: core interface P95 latency deviation ≤ ±15% AND DB query avg. time deviation ≤ ±15%;
     • Business: key conversion/success rates show no degradation vs. prior 1h baseline;
     • Resources: CPU/Memory usage and JVM GC frequency show no sustained spike or cliff.
   - → Proceed to full rollout only if *all four dimensions* meet thresholds for ≥20 consecutive minutes.

4. Full Rollout Phase:
   - Trigger only after: (a) successful observation window; (b) signed manual verification of core flows; (c) zero open P0/P1 issues.
   - Execute via progressive traffic shift (e.g., 5% → 20% → 50% → 100%), with ≥5 min between steps and metric validation at each.
   - Enforce hard rollback within 5 minutes if *any* threshold from Observation Phase is breached during rollout.

## Triggers

- 定义发版各阶段通过条件
- 明确监控阈值
- 设置灰度终止标准
- 制定回归测试准入门槛
- 规定全量发布触发条件
- 指定谁有权执行回滚
