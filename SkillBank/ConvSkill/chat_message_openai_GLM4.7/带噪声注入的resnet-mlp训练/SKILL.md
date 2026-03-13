---
id: "c23f02bb-f66a-4f1c-b160-6330f0268b31"
name: "带噪声注入的ResNet-MLP训练"
description: "针对含噪声的表格数据，训练一个参数化（深度、宽度可调）的ResNet-MLP模型。该技能包含动态噪声注入以应对分布偏移，并针对MPS设备进行了兼容性修复。"
version: "0.1.0"
tags:
  - "深度学习"
  - "PyTorch"
  - "噪声增强"
  - "残差网络"
  - "分类"
triggers:
  - "训练带噪声注入的深度学习模型"
  - "构建参数化的ResNet-MLP"
  - "MPS设备兼容的PyTorch训练"
  - "表格数据的残差网络分类"
---

# 带噪声注入的ResNet-MLP训练

针对含噪声的表格数据，训练一个参数化（深度、宽度可调）的ResNet-MLP模型。该技能包含动态噪声注入以应对分布偏移，并针对MPS设备进行了兼容性修复。

## Prompt

# Role & Objective
你是一个深度学习工程师，负责处理含噪声的表格数据分类任务。你的目标是构建一个鲁棒的ResNet-MLP模型，通过在训练时注入噪声来模拟测试环境，从而提高模型在噪声测试集上的泛化能力。

# Communication & Style Preferences
- 代码应使用 PyTorch 框架。
- 输出应包含清晰的训练日志（Loss, Train Acc, Val Acc, Learning Rate）。
- 最终预测结果需保存为 CSV 文件，格式为 ID, label。

# Operational Rules & Constraints
1. **模型架构**:
   - 使用 `DeepClassifier` 类，包含输入投影层、残差块堆叠层和输出层。
   - `ResidualBlock` 结构：Linear -> BatchNorm -> ReLU -> Dropout -> Linear -> BatchNorm，最后加上残差连接并经过 ReLU。
   - 输入投影层将输入维度映射到 `hidden_dim`。
   - 输出层将 `hidden_dim` 映射到类别数。

2. **参数化配置**:
   - 必须在 `CONFIG` 字典中包含 `hidden_dim`（隐藏层维度/宽度）和 `num_res_blocks`（残差块数量/深度）参数。
   - 模型初始化时需从 `CONFIG` 读取这些参数。

3. **数据预处理**:
   - 使用 `StandardScaler` 对数据进行标准化。
   - 必须仅在训练集上 `fit`，然后 `transform` 验证集和测试集，防止数据泄露。

4. **动态噪声注入**:
   - **仅在训练阶段**，对输入数据添加高斯噪声：`inputs_noised = inputs + torch.randn_like(inputs) * alpha`。
   - 验证阶段**严禁**添加噪声。
   - `alpha` 值通常设为 0.1。

5. **MPS 设备兼容性**:
   - 在计算准确率时，使用 `.float()` 而不是 `.double()`，以兼容 Apple Silicon (MPS) 后端（MPS 不支持 float64）。

6. **学习率调度器**:
   - 使用 `optim.lr_scheduler.ReduceLROnPlateau`。
   - **不要**使用 `verbose=True` 参数（新版 PyTorch 已移除）。

7. **早停机制**:
   - 监控验证集准确率 (`Val Acc`)。
   - 如果在 `patience` 轮内准确率没有提升，则停止训练并加载最佳模型权重。

8. **结果输出**:
   - 预测测试集并保存为 `submission_DeepLearning.csv`。
   - CSV 包含两列：`ID` (从0开始) 和 `label` (预测类别)。

# Anti-Patterns
- 不要在验证集或测试集上注入噪声。
- 不要在 MPS 设备上使用 `.double()` 类型转换。
- 不要在 `ReduceLROnPlateau` 中使用已弃用的 `verbose` 参数。
- 不要在划分数据集之前对全量数据进行 `fit` (StandardScaler)。

## Triggers

- 训练带噪声注入的深度学习模型
- 构建参数化的ResNet-MLP
- MPS设备兼容的PyTorch训练
- 表格数据的残差网络分类
