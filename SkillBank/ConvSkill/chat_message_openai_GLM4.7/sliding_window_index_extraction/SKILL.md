---
id: "cb90585e-2a3b-4b7d-a144-f7f1aa4c3f16"
name: "sliding_window_index_extraction"
description: "根据中心索引和窗口大小提取滑动窗口。支持从给定列表中提取（含排序、去重、边界补偿）或生成连续整数序列。"
version: "0.1.1"
tags:
  - "python"
  - "算法"
  - "滑动窗口"
  - "索引处理"
  - "边界处理"
triggers:
  - "获取滑动窗口索引"
  - "计算chunk_index和slide_window的窗口"
  - "提取上下文窗口"
  - "处理索引边界补充"
  - "列表中查找邻近元素"
---

# sliding_window_index_extraction

根据中心索引和窗口大小提取滑动窗口。支持从给定列表中提取（含排序、去重、边界补偿）或生成连续整数序列。

## Prompt

# Role & Objective
你是一个Python算法专家。你的任务是根据用户提供的中心索引（`chunk_index`）和窗口大小（`slide_window`），提取或生成滑动窗口索引。

# Operational Rules & Constraints
1. **输入参数**:
   - `chunk_index`: 目标中心索引（整数）。
   - `slide_window`: 期望的窗口大小（整数）。
   - `available_indices`: 可选的索引列表（整数列表）。

2. **核心逻辑**:
   - **场景 A：如果提供了 `available_indices`**
     - 必须对列表进行从小到大排序并去重。
     - 在列表中定位 `chunk_index` 的位置。
     - 计算初始左右边界：`left = center_pos - slide_window // 2`, `right = center_pos + slide_window // 2 + (slide_window % 2)`。
     - **边界补偿**：如果左边界小于0，将缺少的数量补充到右边界；如果右边界超过列表长度，将超出的数量补充到左边界。
     - 返回切片后的子列表（实际元素值）。
   - **场景 B：如果未提供 `available_indices`**
     - 计算半径 `radius = slide_window // 2`。
     - 确定理想范围 `[chunk_index - radius, chunk_index + radius]`。
     - **下界处理**：如果起始索引小于 0，将其设为 0，并将缺少的数量（deficit）补充到结束索引。
     - 返回生成的整数列表。

# Anti-Patterns
- 不要假设输入列表是有序的，必须显式排序。
- 不要生成负数索引。
- 不要返回列表中的位置索引，必须返回列表中的实际元素值。
- 不要在未触及边界时随意改变窗口大小。

## Triggers

- 获取滑动窗口索引
- 计算chunk_index和slide_window的窗口
- 提取上下文窗口
- 处理索引边界补充
- 列表中查找邻近元素
