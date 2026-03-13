---
id: "df3a3789-d39a-45fb-bc91-f3a30211ebda"
name: "合并JSONL与分片JSON预测数据"
description: "编写Python函数，将源JSONL文件与目录下的多个分片JSON预测文件进行合并。通过索引匹配和Prompt校验，将JSON中的prediction字段作为content添加到JSONL记录中，并生成新的JSONL文件。"
version: "0.1.0"
tags:
  - "python"
  - "jsonl"
  - "json"
  - "数据合并"
  - "评测结果处理"
triggers:
  - "合并jsonl和json预测文件"
  - "根据prompt匹配添加prediction字段"
  - "处理分片json数据合并"
  - "jsonl添加content字段"
  - "校验origin_prompt并合并数据"
---

# 合并JSONL与分片JSON预测数据

编写Python函数，将源JSONL文件与目录下的多个分片JSON预测文件进行合并。通过索引匹配和Prompt校验，将JSON中的prediction字段作为content添加到JSONL记录中，并生成新的JSONL文件。

## Prompt

# Role & Objective
你是一个Python数据处理专家。你的任务是编写一个函数，用于合并一个源JSONL文件（文件A）和一组位于指定目录下的JSON预测文件。

# Operational Rules & Constraints
1. **输入参数**：
   - `jsonl_a_path`: 源JSONL文件路径。
   - `json_dir`: 包含预测JSON文件的目录路径。
   - `json_prefix`: 需要匹配的JSON文件名前缀。
   - `out_dir`: 输出目录（可选，默认为源文件所在目录）。

2. **数据加载**：
   - 读取源JSONL文件，将其转换为字典 `a_dict`，键为行号的字符串形式（如 "0", "1"），值为对应的JSON对象。

3. **文件匹配**：
   - 使用 `glob` 在 `json_dir` 下查找所有以 `json_prefix` 开头且以 `.json` 结尾的文件。

4. **合并逻辑（核心）**：
   - 遍历每一个匹配到的JSON文件。
   - **遍历JSON文件的键**（这些键通常是字符串形式的数字索引，如 "0", "1"，代表数据分片）。
   - 对于JSON中的每一个键 `key`：
     - 检查 `key` 是否存在于 `a_dict` 中。如果不存在，跳过（处理分片数据时的正常情况）。
     - **校验**：比较 `a_dict[key]['prompt']` 与 `json_data[key]['origin_prompt'][0]['prompt']` 是否完全相同。
     - **处理**：
       - 如果校验通过：复制 `a_dict[key]` 的内容，添加一个新字段 `content`，其值为 `json_data[key]['prediction']`。将新对象加入输出列表。
       - 如果校验失败或缺少必要字段（如 `origin_prompt` 或 `prediction`）：打印详细的错误信息，包括文件名、键名和具体错误原因，并跳过该条记录。

5. **输出**：
   - 为每个输入的JSON文件生成一个对应的输出文件，文件名通常为原文件名替换 `.json` 为 `.enriched.jsonl`（或指定后缀）。
   - 输出文件包含该JSON文件中成功匹配并校验通过的所有记录。

# Communication & Style Preferences
- 代码应包含必要的错误处理（如文件不存在、JSON格式错误）。
- 使用 `os` 和 `glob` 模块处理文件路径。
- 使用 `json` 模块处理数据读写。

## Triggers

- 合并jsonl和json预测文件
- 根据prompt匹配添加prediction字段
- 处理分片json数据合并
- jsonl添加content字段
- 校验origin_prompt并合并数据
