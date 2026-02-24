---
id: "8a74a7eb-667c-4147-b85c-3563424a076a"
name: "compress-public-service-timeline-with-constraint-awareness"
description: "Adjusts implementation timelines in public-facing service announcements by compressing deadlines while explicitly preserving non-negotiable steps and dependencies—ensuring factual integrity, regulatory compliance, and operational feasibility remain intact."
version: "0.1.0"
tags:
  - "timeline-compression"
  - "public-communication"
  - "constraint-aware-editing"
  - "government-to-citizen"
triggers:
  - "把时间压缩一周"
  - "缩短工期但保留关键节点"
  - "加速落地但不跳步骤"
  - "压时限、保底线"
---

# compress-public-service-timeline-with-constraint-awareness

Adjusts implementation timelines in public-facing service announcements by compressing deadlines while explicitly preserving non-negotiable steps and dependencies—ensuring factual integrity, regulatory compliance, and operational feasibility remain intact.

## Prompt

# Goal
Given a publicly released service optimization plan (e.g., community eldercare rollout), compress the overall timeline by exactly one week across all time-bound commitments—without omitting, merging, or skipping any step that is legally mandated, technically dependent, or contractually binding. Output only the revised dates and a concise, bullet-pointed list of steps that *cannot* be shortened, with clear justification for each.

# Constraints & Style
- Must preserve all original dependencies (e.g., 'system launch requires prior security audit'; 'staff training must precede service deployment').
- Must retain all statutory, contractual, or inter-agency coordination requirements (e.g., 'requires signed agreement from X agency', 'must align with fiscal quarter close').
- Never compress steps involving third-party certification, regulatory approval, hardware installation, or data interface testing—these are non-negotiable.
- Use plain language; avoid jargon. List only what *must stay*—not what *could change*.
- Output format: first line = new headline date (e.g., 'All measures now effective by 2024-12-24'); then 'Non-compressible steps:' followed by bullets.
- No explanations beyond the justification clause per bullet.
- Do not invent new constraints or add policy references absent from source.

## Triggers

- 把时间压缩一周
- 缩短工期但保留关键节点
- 加速落地但不跳步骤
- 压时限、保底线
