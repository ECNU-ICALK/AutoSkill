---
id: "aef7b5fb-1171-4009-8cb6-a24d9573a0be"
name: "严格无重叠Mask数据集过滤"
description: "生成Python脚本，用于过滤COCO格式数据集，移除任意两个实例mask存在像素重叠（交集大于0）的样本。"
version: "0.1.0"
tags:
  - "数据集过滤"
  - "Mask重叠"
  - "COCO"
  - "RLE"
  - "Python脚本"
triggers:
  - "只要mask有重叠的就应该筛掉"
  - "过滤重叠mask的数据集"
  - "严格无重叠mask筛选"
  - "重写脚本去除重叠样本"
---

# 严格无重叠Mask数据集过滤

生成Python脚本，用于过滤COCO格式数据集，移除任意两个实例mask存在像素重叠（交集大于0）的样本。

## Prompt

# Role & Objective
编写Python脚本，用于过滤包含重叠Mask的数据集样本。

# Operational Rules & Constraints
1. **严格重叠判定**：只要样本中任意两个Mask的交集像素数大于0（即有任何重叠），该样本即被判定为无效并移除。不使用IoU阈值。
2. **数据格式**：输入为JSON文件（如COCO格式），样本包含`answers`字段，其中包含RLE格式的`segmentation`。
3. **处理流程**：
   - 读取JSON数据。
   - 遍历样本，提取所有Mask。
   - 对所有Mask对进行两两检查，使用`pycocotools`解码RLE，计算`np.logical_and(mask1, mask2).sum()`。
   - 如果交集 > 0，标记为移除。
4. **输出处理**：将过滤后的数据保存到指定路径。在写入文件前，检查并自动创建输出目录（`os.makedirs`）。
5. **统计信息**：输出总样本数、移除样本数、剩余样本数及移除率。

# Anti-Patterns
- 不要使用IoU阈值（如0.1）来判断是否重叠。
- 不要忽略大Mask包含小Mask的情况（只要交集>0即视为重叠）。

## Triggers

- 只要mask有重叠的就应该筛掉
- 过滤重叠mask的数据集
- 严格无重叠mask筛选
- 重写脚本去除重叠样本
