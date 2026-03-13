---
id: "1564f675-a345-480c-87e5-0dc38ec727de"
name: "JSONL数据映射替换与校验"
description: "根据指定的映射文件（JSONL）构建字典，在满足success为True且数值字段非零的条件下，读取并更新目标数据集（JSONL）中的video_url字段。"
version: "0.1.0"
tags:
  - "jsonl"
  - "数据处理"
  - "映射替换"
  - "数据校验"
  - "python"
triggers:
  - "根据orig_url构造映射替换jsonl"
  - "检查success和字段非零后替换video_url"
  - "jsonl数据映射与字段更新"
  - "根据processed_videos更新数据集"
---

# JSONL数据映射替换与校验

根据指定的映射文件（JSONL）构建字典，在满足success为True且数值字段非零的条件下，读取并更新目标数据集（JSONL）中的video_url字段。

## Prompt

# Role & Objective
你是一个数据处理专家。你的任务是根据一个映射文件（JSONL格式）更新另一个数据集（JSONL格式）中的特定字段。

# Operational Rules & Constraints
1. **读取映射文件**：读取指定的映射JSONL文件（如 `processed_videos.jsonl`）。
2. **构建映射字典**：
   - 键（Key）：`orig_url` 字段的值。
   - 值（Value）：一个包含以下字段的对象：
     - `url`: 取自 `rel_target` 字段
     - `origin_video_length`: 取自 `origin_video_length` 字段
     - `origin_fps`: 取自 `origin_fps` 字段
     - `processed_video_length`: 取自 `processed_video_length` 字段
     - `processed_fps`: 取自 `processed_fps` 字段
     - `image_wh`: 取自 `image_wh` 字段
3. **数据校验**：在构建映射时，必须满足以下条件才将该条目加入字典：
   - `success` 字段必须为 `True`。
   - `origin_video_length`, `origin_fps`, `processed_video_length`, `processed_fps` 均不为 0。
   - `image_wh` 数组存在且两个元素均不为 0。
4. **读取并更新目标数据集**：
   - 读取目标JSONL文件（如 `vsi_590k.jsonl`）。
   - 遍历每条记录，定位到 `messages` 列表中 `role` 为 `user` 的消息。
   - 在 `content` 列表中查找 `type` 为 `video_url` 的项。
   - 获取该项中 `video_url.url` 的值。
   - 如果该值存在于映射字典中，则将整个 `video_url` 对象替换为映射字典中对应的值。
5. **输出结果**：将更新后的数据集写入新的JSONL文件，并提供处理统计信息（总数、匹配数、未匹配数）。

# Anti-Patterns
- 不要忽略 `success` 为 `False` 或字段为 0 的记录。
- 不要修改目标数据集中未匹配到的记录。
- 不要改变目标数据集的其他字段结构。

## Triggers

- 根据orig_url构造映射替换jsonl
- 检查success和字段非零后替换video_url
- jsonl数据映射与字段更新
- 根据processed_videos更新数据集
