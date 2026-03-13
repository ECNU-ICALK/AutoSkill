---
id: "01d46cba-36b8-4875-8e38-df522f966c00"
name: "mathbf / mathcal / _l"
description: "General SOP for common requests related to mathbf, mathcal, _l."
version: "0.1.0"
tags:
  - "mathbf"
  - "mathcal"
  - "_l"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# mathbf / mathcal / _l

General SOP for common requests related to mathbf, mathcal, _l.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 方案名称：ZSP (Zero-Sum Perturbation) 零和扰动投影
2) 1. 核心思想 (Decomposition
3) 我们将目标残差连接矩阵 $\mathcal{H}^{\mathrm{res}}_l$ 分解为两部分
4) 1.  **静态基准 (Static Base):** 一个固定的、天然满足双随机性质的矩阵 $\mathbf{B}$。在残差网络（ResNet）的语境下，恒等映射是最优的先验，因此取单位矩阵 $\mathbf{I
5) 2.  **动态扰动 (Dynamic Perturbation):** 一个由神经网络生成的扰动矩阵 $\mathcal{Z}_l$，其行和与列和严格为零
6) 公式化表示为
7) mathcal{H}^{\mathrm{res}}_l = \mathbf{B} + \lambda_l \cdot \mathcal{Z}_l, \quad \text{其中 } \mathbf{B} = \mathbf{I}_n
8) 其中 $\lambda_l$ 是一个可学习的标量系数，用于控制偏离恒等映射的程度
9) 2. 零和约束的解析投影 (Analytic Projection for Zero-Sum
10) 原问题中的双随机约束 $\mathcal{H}\mathbf{1} = \mathbf{1}, \mathbf{1}^\top\mathcal{H} = \mathbf{1}^\top$ 等价于对 $\mathcal{Z}_l$ 的约束

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
