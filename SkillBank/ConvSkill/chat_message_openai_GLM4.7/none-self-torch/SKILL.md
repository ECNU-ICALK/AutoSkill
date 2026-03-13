---
id: "0f201bda-e0c0-4739-9f5e-467af2bdb7b7"
name: "none / self / torch"
description: "General SOP for common requests related to none, self, torch."
version: "0.1.0"
tags:
  - "none"
  - "self"
  - "torch"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# none / self / torch

General SOP for common requests related to none, self, torch.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 其 chunk 选择机制不可端到端学习，导致检索不准——即使在域内任务（如 Multi-Query NIAH）也无法达到完美准确率，且随上下文增长性能迅速下降；实验还表明 **NoPE 比 RoPE 更利于长度外推
2) HSA 的改进
3) 可学习的检索式稀疏注意力**：每个 token 对 top-K 相关 chunks 分别做 intra-chunk attention，再用检索得分加权融合（inter-chunk fusion
4) 混合位置编码策略**：滑动窗口用 RoPE（保留在域性能），HSA 部分用 NoPE（提升外推能力
5) 实现细节**：序列按固定块长（如 64）分块，每块有 landmark 表示用于检索；使用 Query-Key Normalization 保障万亿 token 训练稳定性
6) HSA-UltraLong 模型的架构设计与训练策略**，核心目标是：**在保持强大局部建模能力的同时，实现超长上下文的有效泛化
7) 3 Methodology
8) 3.1 模型架构：分层混合注意力 + 共享记忆
9) 1.  **整体结构**（L 层
10) 1.  **下 decoder（前 L/2 层）**：标准 Transformer **滑动窗口注意力（SWA）**，专注局部信息

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
