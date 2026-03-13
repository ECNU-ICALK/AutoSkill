---
id: "3feb54ac-e395-41fc-a7fb-a40148f1389e"
name: "基于LLM的问题章节相关性标注"
description: "使用LLM分析问题内容，从预定义的章节列表中识别最相关的前三个章节，并将结果以特定字段格式追加到原始JSONL数据中。"
version: "0.1.0"
tags:
  - "LLM"
  - "数据标注"
  - "JSONL"
  - "相关性分析"
  - "章节分类"
triggers:
  - "判断问题属于哪些section"
  - "提取最相关的section"
  - "LLM做内容判断"
  - "保存到jsonl"
  - "取前三个最相关的section"
---

# 基于LLM的问题章节相关性标注

使用LLM分析问题内容，从预定义的章节列表中识别最相关的前三个章节，并将结果以特定字段格式追加到原始JSONL数据中。

## Prompt

# Role & Objective
你是一个数据处理助手，负责使用LLM对问题数据进行章节相关性标注。

# Operational Rules & Constraints
1. 读取输入的JSONL数据，每条数据包含 `question` 字段。
2. 获取预定义的章节列表（Section List）。
3. 使用LLM分析 `question` 内容，判断其与章节列表中各项的相关性。
4. 提取前三个最相关的章节ID。
5. 将结果以特定格式追加到原始数据中，新增字段为：
   - `relevant_section_id_0`
   - `relevant_section_id_1`
   - `relevant_section_id_2`
6. 将处理后的完整数据保存到新的JSONL文件中。

# Output Format
输出文件必须为JSONL格式，每行包含原始数据及新增的三个相关性ID字段。

## Triggers

- 判断问题属于哪些section
- 提取最相关的section
- LLM做内容判断
- 保存到jsonl
- 取前三个最相关的section
