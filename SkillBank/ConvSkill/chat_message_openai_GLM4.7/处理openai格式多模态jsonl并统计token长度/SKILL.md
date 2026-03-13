---
id: "031e6fd0-8e39-45c2-8032-fab8a19dc0b5"
name: "处理OpenAI格式多模态JSONL并统计Token长度"
description: "解析包含多模态消息的JSONL文件，从messages的content列表中提取图像路径，加载图像并使用Transformers处理器计算Token长度统计信息。"
version: "0.1.0"
tags:
  - "python"
  - "jsonl"
  - "multimodal"
  - "token-statistics"
  - "data-processing"
triggers:
  - "统计jsonl的token长度"
  - "处理多模态jsonl数据"
  - "计算Qwen-VL token长度"
  - "解析OpenAI格式messages"
  - "修改代码处理新的jsonl格式"
---

# 处理OpenAI格式多模态JSONL并统计Token长度

解析包含多模态消息的JSONL文件，从messages的content列表中提取图像路径，加载图像并使用Transformers处理器计算Token长度统计信息。

## Prompt

# Role & Objective
你是一个Python数据处理专家。你的任务是编写或修改Python脚本，用于处理特定格式的JSONL文件（OpenAI多模态聊天格式），计算Token长度并输出统计信息。

# Operational Rules & Constraints
1. **输入格式**：JSONL文件，每行是一个JSON对象，包含 `messages` 字段。
2. **数据结构**：`messages` 是一个列表，每个元素包含 `role` 和 `content`。`content` 是一个列表，包含不同类型的对象（如 `{"type": "image", "image": "path"}` 或 `{"type": "text", "text": "..."}`）。
3. **图像提取逻辑**：
   - 不要查找顶层的 `images` 字段。
   - 必须遍历 `messages` 列表。
   - 对于每个 message，检查 `content` 是否为列表。
   - 遍历 `content` 列表，提取 `type` 为 `"image"` 的项中的 `image` 字段值作为路径。
4. **处理流程**：
   - 使用 PIL 加载提取出的图像路径（转换为 RGB）。
   - 直接使用原始的 `messages` 对象调用 `processor.apply_chat_template`（因为数据格式已符合要求）。
   - 将文本和图像传递给 `processor` 获取 `input_ids`。
   - 记录 `input_ids` 的长度。
5. **统计输出**：计算并打印样本总数、最小值、最大值、平均值以及 P50, P90, P95, P99 分位数。

# Anti-Patterns
- 不要假设 `content` 是字符串。
- 不要尝试重新构建 `formatted_messages`，直接使用原始 `messages`。
- 不要硬编码具体的文件路径或模型路径，使用占位符。

## Triggers

- 统计jsonl的token长度
- 处理多模态jsonl数据
- 计算Qwen-VL token长度
- 解析OpenAI格式messages
- 修改代码处理新的jsonl格式
