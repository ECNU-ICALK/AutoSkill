---
id: "6b4f0f6c-7276-4514-a99c-f22d7de2f84b"
name: "self / cfg / torch"
description: "General SOP for common requests related to self, cfg, torch."
version: "0.1.0"
tags:
  - "self"
  - "cfg"
  - "torch"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# self / cfg / torch

General SOP for common requests related to self, cfg, torch.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 死特征 0.4，L0 为 140 可用吗
2) 直接回答：这通常是一个不可用或质量较差的状态
3) 死特征比例 (Dead Feature Ratio, 40%)：偏高
4) 这意味着你的字典中有 40% 的容量被浪费了。如果你的字典大小（Dictionary Size）是 $N$，实际起作用的只有 $0.6N
5) 虽然在早期实验中出现这种情况很常见，但为了获得高质量的特征，通常希望将死特征比例控制在 **5% 以下**，甚至接近 0%。高死特征率通常意味着初始化不佳或学习率过高/过低
6) 平均激活特征数 (L0 Norm, 140)：通常过高
7) 对于大多数常见的语言模型（如 GPT-2 Small, Pythia-160m, 甚至 Llama-3 8B），单 token 激活 140 个特征意味着稀疏性不足
8) 后果：** 你的特征很可能不是“单义的”（Monosemantic）。当 L0 很高时，模型倾向于学习到“多义特征”或特征之间的线性组合，这违背了使用 SAE 进行特征解耦的初衷
9) 理想值：** 通常我们追求的 L0 范围在 **10 到 50** 之间（具体取决于字典大小扩展倍数，expansion factor）。OpenAI 和 Anthropic 的论文中，L0 通常控制在几十的量级
10) 2. 降低死特征比例（Dead Features）的思路

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
