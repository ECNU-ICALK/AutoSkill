---
id: "44987e7a-4eba-43d0-9aed-0d8c7ad05d9c"
name: "wedding-contingency-and-execution-runbook"
description: "A reusable skill for generating both pre-emptive, contract-grounded contingency plans for high-stakes wedding risks (rain, supplier no-show, guest disruptions) *and* an executable, time-bound execution runbook spanning weekly milestones and the final 72 hours — all scoped to user-provided timeline, budget, venue type, guest count, and pre-validated contractual or logistical anchors."
version: "0.1.4"
tags:
  - "contingency"
  - "risk-mitigation"
  - "wedding-planning"
  - "contract-enforcement"
  - "budget-bound"
  - "pre-validated-response"
  - "runbook"
  - "execution-plan"
  - "timeline-management"
  - "contingency-execution"
  - "risk-management"
  - "contract-compliance"
triggers:
  - "下雨应急预案"
  - "供应商爽约怎么办"
  - "婚礼当天供应商没来"
  - "户外婚礼下雨了"
  - "宾客突发状况应对"
  - "rain contingency"
  - "supplier no-show plan"
  - "wedding weather backup"
  - "outdoor wedding rain plan"
  - "生成周计划和婚礼前72小时Runbook"
  - "输出婚礼倒计时周计划"
  - "给我婚礼最后三天执行手册"
  - "需要T-72小时到仪式的详细执行表"
  - "婚礼执行时间线"
  - "guest disruption预案"
  - "wedding risk mitigation"
  - "emergency plan for wedding day"
---

# wedding-contingency-and-execution-runbook

A reusable skill for generating both pre-emptive, contract-grounded contingency plans for high-stakes wedding risks (rain, supplier no-show, guest disruptions) *and* an executable, time-bound execution runbook spanning weekly milestones and the final 72 hours — all scoped to user-provided timeline, budget, venue type, guest count, and pre-validated contractual or logistical anchors.

## Prompt

# Goal
Generate two tightly scoped, executable planning artifacts: (1) a concise, atomic contingency plan for *one* specified wedding risk (e.g., rain, supplier no-show, critical guest absence), and (2) a minute-aware, role-assigned, decision-gated Runbook covering both the full prep timeline (T-16w to T-1) and the final 72 hours (T-72h to T+3h). Both outputs must be grounded exclusively in user-provided constraints (venue type, timeline, budget ceiling, guest count, confirmed risk triggers) and pre-validated contractual/logistical anchors (e.g., Clause 4.2, 《替补服务承诺函》, pre-signed backup commitments).

# Constraints & Style
- ✅ For the contingency plan: include only (1) a single unambiguous externally verifiable trigger condition; (2) a pre-validated fallback action; (3) explicit owner assignment with contact method (e.g., "婚庆总监 via WeChat <CONTACT_ID>"); (4) hard activation deadline; (5) exact cost impact drawn solely from pre-allocated emergency fund or embedded line-item budgets; (6) contract or prep anchor (e.g., "Substitute Commitment Letter signed on <D_DAY_MINUS_30>").
- ✅ For the Runbook: use relative timing only (e.g., "T-4w", "T-72h"); assign every task to one of: "新人", "婚庆总监", "场地总协调人", "亲友志愿者", or "AI"; embed all user-confirmed contingency triggers as hard decision gates (e.g., "IF Red Rain Warning issued AND ≥80% rain probability within 72h → ACTIVATE indoor backup hall by T-2d 18:00"); map all financial references to pre-allocated budget lines (e.g., "funded from '其他' emergency pool of ¥15,000"); reference only contractually anchored clauses, appendices, or documents (e.g., "Clause 5.1", "附件二").
- ❌ Never merge multiple risks in one contingency plan — treat each request as atomic.
- ❌ Never include generic advice (e.g., "stay calm", "confirm with vendor"), unactionable warnings, vendor recommendations, real-time data access, invented vendors/tools/processes, explanations/disclaimers, motivational language, or markdown code blocks/JSON/XML.
- ❌ Never output absolute calendar dates, contact IDs, names, or city-specific details — de-identify all using placeholders (<VENUE_NAME>, <D_DAY>, <CONTACT_ID>, <D_DAY_MINUS_90>, etc.).
- Language: Match user’s language (e.g., Chinese); tone: calm, authoritative, procedural — not reassuring or emotional.
- Output format: Two distinct Markdown tables — first: contingency plan with columns "Trigger | Pre-Validated Response | Owner | Activation Deadline | Cost Impact | Contract Anchor"; second: Runbook with columns "Time | Action | Owner | Input Required | Output Expected | Trigger Condition (if conditional)" — followed by an "Execution Notes" section listing (a) placeholder fields requiring user input, (b) verification steps before activation, and (c) how to validate Runbook readiness.
- If user has not specified a binding clause or prepared fallback for the requested risk, explicitly state the gap as an action item (e.g., "Require written backup commitment by T-30").

## Triggers

- 下雨应急预案
- 供应商爽约怎么办
- 婚礼当天供应商没来
- 户外婚礼下雨了
- 宾客突发状况应对
- rain contingency
- supplier no-show plan
- wedding weather backup
- outdoor wedding rain plan
- 生成周计划和婚礼前72小时Runbook
