---
id: "4d523fc3-8cda-445e-92b7-a9d569a6ab8c"
name: "budget-compression-with-quality-preservation"
description: "A reusable budget optimization skill that applies a precise percentage-based reduction to an existing budget while mandating equivalent or improved functional quality through validated alternative solutions."
version: "0.1.0"
tags:
  - "budgeting"
  - "cost-optimization"
  - "quality-preservation"
  - "substitution"
triggers:
  - "预算压缩但不降质量"
  - "压缩预算替代方案"
  - "10%预算削减替代项"
  - "成本优化不牺牲核心功能"
  - "高质量低成本替代"
---

# budget-compression-with-quality-preservation

A reusable budget optimization skill that applies a precise percentage-based reduction to an existing budget while mandating equivalent or improved functional quality through validated alternative solutions.

## Prompt

# Goal
Apply a specified percentage reduction (e.g., 10%) to a given budget allocation, and generate one or more concrete, non-regressive alternatives for each affected category — ensuring core functionality, user-defined quality thresholds, and measurable equivalence (e.g., same coverage, duration, or outcome) are preserved.

# Constraints & Style
- Must not reduce scope, coverage, reliability, or essential user outcomes — only cost structure.
- Each alternative must be specific, actionable, and grounded in real-world substitutes (e.g., tiered service plans, bulk procurement, behavioral shifts, or platform switches).
- Explicitly state *how* quality is preserved (e.g., "same 24/7 support via community-tier plan", "identical nutritional profile using seasonal produce").
- Reject vague suggestions (e.g., "find cheaper options") or trade-offs that degrade core value (e.g., skipping maintenance, downgrading security).
- Output only the alternatives — no justification paragraphs, no motivational language, no new frameworks.

# Workflow
1. Parse the original budget line(s) and target compression rate.
2. For each line item, identify its core functional requirement (e.g., 'daily meal provision', 'reliable internet access', 'child safety certification').
3. Propose ≥1 alternative that meets that requirement at lower cost, with explicit preservation logic.
4. Format as a minimal markdown table: | Category | Original | Compressed | Alternative | Quality Preservation Logic |

## Triggers

- 预算压缩但不降质量
- 压缩预算替代方案
- 10%预算削减替代项
- 成本优化不牺牲核心功能
- 高质量低成本替代
