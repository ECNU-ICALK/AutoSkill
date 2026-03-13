---
id: "b8a79e80-c3a0-43d2-bd4d-e2c751dfa785"
name: "self / none / tl"
description: "General SOP for common requests related to self, none, tl."
version: "0.1.0"
tags:
  - "self"
  - "none"
  - "tl"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# self / none / tl

General SOP for common requests related to self, none, tl.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 使用多个寄存器 accumulator 来避免频繁的 global memory 读写
2) 策略
3) 为每个 D 分块维护一个独立的 accumulator (acc_0, acc_1
4) 所有 accumulator 都在寄存器中，遍历完所有 KV 块后一次性写回
5) 代价是寄存器压力更大，但避免了 O(num_kv_blocks * num_d_blocks) 次 global memory 访问
6) 适用场景
7) NUM_D_BLOCKS 较小 (2-4)，寄存器能放下所有 accumulator
8) KV 序列较长，减少 global memory 访问收益大
9) cur_q_block_idx = tl.program_id(0
10) cur_head = tl.program_id(1

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
