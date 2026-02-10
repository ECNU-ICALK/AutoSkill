---
id: "fb980ce0-4ae8-4df0-bc1f-9c58f03df240"
name: "family-friendly-claim-tracker-compression-rule"
description: "A reusable rule set for compressing a family-oriented insurance claim status tracker into a one-week timeline while preserving legally and operationally critical steps."
version: "0.1.0"
tags:
  - "claim-tracking"
  - "legal-compliance"
  - "family-audience"
  - "time-compression"
  - "evidence-preservation"
triggers:
  - "把时间压缩一周"
  - "哪些步骤不能删"
  - "压缩家庭版理赔追踪表"
  - "一周内必须完成的申诉步骤"
  - "法律不可删节点"
---

# family-friendly-claim-tracker-compression-rule

A reusable rule set for compressing a family-oriented insurance claim status tracker into a one-week timeline while preserving legally and operationally critical steps.

## Prompt

# Goal
Compress the family-friendly insurance claim status tracking timeline from its original multi-stage structure into a strict 7-day (D+0 to D+7) schedule, explicitly identifying which steps are non-removable due to legal deadlines, evidence integrity requirements, or procedural dependencies.

# Constraints & Style
- Must preserve all time-bound legal requirements: the 10-workday window to file a formal written异议 (per Insurance Law Art. 23/25) and the mandatory 15-day insurer response period must remain intact and visible in the compressed view.
- Must retain all evidence-critical actions: EMS mailing with tracking, screenshot/photo capture of notices, and written follow-up of verbal communications — no step that creates or secures admissible evidence may be omitted or merged.
- Must keep all dependency chains explicit: e.g., 'D+3: Send异议' cannot exist without 'D+0: Receive & photo-document拒赔 notice'; if D+0 is missing, the entire sequence collapses.
- Use plain language only — no insurance jargon, no Latin terms, no clause numbers unless directly quoted from law (e.g., 'Insurance Law Article 25').
- Output format: a single Markdown table with columns: | Day | Action | Why This Step Cannot Be Removed |.
- Do not invent new steps, roles, thresholds, or tools beyond those user-confirmed in prior turns.
- De-identify all case-specific data: use placeholders like <POLICY_NUMBER>, <CLAIM_ID>, <NOTICE_DATE>.

# Workflow
None — this is a constraint-based compression analysis, not a multi-stage AI operation. No workflow steps are to be generated.

## Triggers

- 把时间压缩一周
- 哪些步骤不能删
- 压缩家庭版理赔追踪表
- 一周内必须完成的申诉步骤
- 法律不可删节点
