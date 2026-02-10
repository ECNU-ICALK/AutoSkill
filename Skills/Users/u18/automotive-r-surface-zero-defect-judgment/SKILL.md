---
id: "bb77bf8d-f9f1-4f90-9c6d-5cad2d8671ff"
name: "automotive-r-surface-zero-defect-judgment"
description: "Applies strict zero-tolerance surface defect policy for R-face (inner arc surface) of ferrite magnet tiles supplied to automotive high-speed motor customers, overriding general national standard allowances."
version: "0.1.1"
tags:
  - "quality-judgment"
  - "automotive"
  - "zero-defect"
  - "ferrite-magnet"
  - "r-surface"
triggers:
  - "R面零缺陷判定"
  - "客户A磁瓦判级"
  - "高速电机磁瓦R面裂纹判定"
  - "发丝纹是否合格"
  - "零收容R面检验"
---

# automotive-r-surface-zero-defect-judgment

Applies strict zero-tolerance surface defect policy for R-face (inner arc surface) of ferrite magnet tiles supplied to automotive high-speed motor customers, overriding general national standard allowances.

## Prompt

# Goal
Determine pass/fail status of ferrite magnet tiles destined for high-speed electric vehicle motors, based exclusively on presence/absence of visible cracks (e.g., hairline cracks, micro-cracks, fissures) on the R-face (inner arc surface), with mandatory NG (Not Good) verdict if any such crack is detected — regardless of size, depth, orientation, or GB/T standard allowances.

# Constraints & Style
- Must treat R-face as a single critical functional surface: it is the adhesive bonding interface and experiences extreme centrifugal stress (≥15,000 rpm); therefore, any visible linear surface discontinuity ≥0.1 mm in length under 10× magnification constitutes an unacceptable failure mode.
- Do NOT apply GB/T or other general appearance standards leniently; reject all interpretations permitting "minor" or "non-performance-affecting" cracks on R-face.
- Do NOT suggest rework, repair, downgrading, or customer exception unless explicitly requested by user in that turn — iron oxide ceramics cannot be repaired; NG means full batch hold or rejection.
- Output must state verdict unambiguously as either "NG" or "OK", followed by one-sentence justification citing R-face functional risk and customer context.
- Avoid technical digressions (e.g., fracture mechanics, hardness values, inspection methods) unless user specifically asks for root cause or mitigation.
- Never reference AEC-Q200, IATF, or other external standards unless user names them — only enforce the user-defined 'R-face zero defect' rule.

# Workflow
1. Identify whether the order is designated for automotive high-speed motor customer (e.g., 'customerA', 'EV motor', '≥15k rpm').
2. Confirm the defect location is the R-face (inner arc surface / bonding surface), not N-face or side faces.
3. Confirm the defect type is a visible crack (linear opening, not scratch, stain, porosity, color variation, or edge chipping) and ≥0.1 mm in length under 10× magnification.
4. If all three conditions are met: return "NG" + justification.
5. If R-face is defect-free per above criteria: return "OK" + justification.

## Triggers

- R面零缺陷判定
- 客户A磁瓦判级
- 高速电机磁瓦R面裂纹判定
- 发丝纹是否合格
- 零收容R面检验
