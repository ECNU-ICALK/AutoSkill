---
id: "e0b6db48-8f6e-4669-b07b-08157a6c670f"
name: "self / torch / none"
description: "General SOP for common requests related to self, torch, none."
version: "0.1.0"
tags:
  - "self"
  - "torch"
  - "none"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# self / torch / none

General SOP for common requests related to self, torch, none.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) from . import BaseActor
2) from lib.utils.misc import NestedTensor
3) from lib.utils.box_ops import box_cxcywh_to_xyxy, box_xywh_to_xyxy
4) import torch
5) from lib.utils.merge import merge_template_search
6) from ...utils.heapmap_utils import generate_heatmap
7) from ...utils.ce_utils import generate_mask_cond, adjust_keep_rate
8) class CEUTrackActor(BaseActor
9) Actor for training CEUTrack models
10) def __init__(self, net, objective, loss_weight, settings, cfg=None

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
