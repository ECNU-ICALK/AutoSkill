---
id: "927423e9-f03a-4a23-b760-a249a34285fe"
name: "CayleyAdamW优化器实现"
description: "实现继承自torch.optim.Optimizer的CayleyAdamW优化器，用于在正交群O(r)上优化参数。该优化器通过将梯度投影到李代数空间进行Adam更新，并利用Cayley变换将更新映射回正交群，从而严格保持参数的正交性。"
version: "0.1.0"
tags:
  - "PyTorch"
  - "优化器"
  - "正交约束"
  - "流形优化"
  - "Cayley变换"
  - "AdamW"
triggers:
  - "实现CayleyAdamW优化器"
  - "正交群AdamW实现"
  - "Cayley变换优化器"
  - "继承torch.optim.Optimizer"
---

# CayleyAdamW优化器实现

实现继承自torch.optim.Optimizer的CayleyAdamW优化器，用于在正交群O(r)上优化参数。该优化器通过将梯度投影到李代数空间进行Adam更新，并利用Cayley变换将更新映射回正交群，从而严格保持参数的正交性。

## Prompt

Role: PyTorch 优化器开发专家
Task: 实现一个名为 CayleyAdamW 的 PyTorch 优化器类。

Requirements:
1. 继承自 torch.optim.Optimizer 基类。
2. 支持参数: params (可迭代参数), lr (学习率), betas (Adam动量系数), eps (数值稳定项), weight_decay (权重衰减), amsgrad (是否使用AMSGrad), maximize (是否最大化), foreach (是否使用foreach优化), capturable (是否可在CUDA图中捕获), differentiable (是否可微分), reorth_freq (重新正交化频率)。
3. 核心算法逻辑:
   - 验证参数必须是方阵 (shape [n, n])。
   - 将欧氏梯度投影到李代数: A = R^T @ grad, Omega = (A - A.T) / 2。
   - 在李代数空间进行 Adam 动量更新 (m, v)。
   - 计算自适应更新方向 Omega_hat。
   - 重新反对称化 Omega_hat (因为除法破坏了反对称性)。
   - 应用权重衰减 (在李代数中): Omega_hat += weight_decay * skew(R^T @ R - I)。
   - 使用 Cayley 变换更新参数: M = -lr * Omega_hat, R_new = R @ (I + M/2) @ inv(I - M/2)。
   - 可选: 周期性重新正交化 (QR分解)。
4. 必须包含完整的 __init__ 和 step 方法实现。
5. 必须包含辅助方法 check_orthogonality (检查正交性误差) 和 reorthogonalize_all (手动重新正交化)。
6. 代码风格需符合 PyTorch 官方规范，包含完整的文档字符串。

Output: 完整的 Python 代码实现。

## Triggers

- 实现CayleyAdamW优化器
- 正交群AdamW实现
- Cayley变换优化器
- 继承torch.optim.Optimizer
