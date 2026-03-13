---
id: "8b8707cd-ee5b-44ff-bb5e-26a3d03c56fc"
name: "py / mnt / petrelfs"
description: "General SOP for common requests related to py, mnt, petrelfs."
version: "0.1.0"
tags:
  - "py"
  - "mnt"
  - "petrelfs"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# py / mnt / petrelfs

General SOP for common requests related to py, mnt, petrelfs.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 节点间网络不稳定/带宽不足
2) GPU 之间通信性能差异
3) DeepSpeed 梯度桶大小不合适
4) NCCL 配置不适合多节点环境
5) 解决方案
6) 1. **优化 DeepSpeed ZeRO 配置
7) 修改你的 DeepSpeed 配置文件
8) json
9) zero_optimization
10) stage": 1

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
