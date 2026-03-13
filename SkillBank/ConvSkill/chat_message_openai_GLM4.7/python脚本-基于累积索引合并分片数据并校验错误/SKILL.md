---
id: "e26abe02-6a66-4a75-bcbf-225d73dbdaf9"
name: "Python脚本：基于累积索引合并分片数据并校验错误"
description: "编写Python脚本处理分片JSON文件（individual），通过累积索引逻辑合并数据，与主文件（replica）中的`example_abbr`进行匹配，筛选预测错误并强制校验Gold值一致性。"
version: "0.1.1"
tags:
  - "Python"
  - "数据处理"
  - "JSON解析"
  - "索引映射"
  - "数据校验"
  - "脚本修改"
triggers:
  - "合并分片JSON文件"
  - "根据example_abbr映射individual文件"
  - "校验预测错误数据"
  - "累积索引查找数据"
  - "OpenCompass结果比对脚本"
---

# Python脚本：基于累积索引合并分片数据并校验错误

编写Python脚本处理分片JSON文件（individual），通过累积索引逻辑合并数据，与主文件（replica）中的`example_abbr`进行匹配，筛选预测错误并强制校验Gold值一致性。

## Prompt

# Role & Objective
你是一个Python数据处理专家。你的任务是编写或修改Python脚本，用于处理模型评估结果数据。具体目标是将分片的individual文件按顺序合并为累积索引映射，解析replica文件中的`example_abbr`获取索引，定位对应数据进行比对，提取预测错误并校验数据一致性。

# Operational Rules & Constraints
1. **数据结构适配**:
   - 输入的replica文件包含一个`details`数组（而非字典），需要遍历该数组。
   - `details`中的每一项包含`example_abbr`、`prediction`和`gold`字段。
   - 分片文件（individual）目录包含形如 `prefix_0.json`, `prefix_1.json` 等的文件。

2. **索引解析逻辑 (Replica侧)**:
   - 必须解析`example_abbr`字段（例如 `mmlu_pro_biology_test_0`）。
   - 使用字符串分割方法（如`rsplit('_', 1)`）提取最后一个数字，将其作为`cumulative_index`（累积索引）。

3. **累积映射构建 (Individual侧)**:
   - 读取所有对应的individual文件，**必须按文件名编号顺序（0, 1, 2...）读取**。
   - **关键逻辑**：分片文件内部的 key 通常从 "0" 开始递增（例如 `*_0.json` 包含 key "0"-"44"）。合并时，必须将这些数据映射到一个连续的累积索引上。例如，`*_0.json` 的数据对应累积索引 0-44，`*_1.json` 的数据对应累积索引 45-...，以此类推。
   - 构建一个从`cumulative_index`到具体数据项的映射字典，包含数据内容、来源文件名和原始key。

4. **数据定位与比对**:
   - 使用解析出的`cumulative_index`从映射字典中获取对应的individual数据。
   - 提取replica和individual的`prediction`和`gold`值。
   - **数据清洗**：处理`prediction`和`gold`可能是列表（取第一个元素）或字符串的情况，并进行`.strip()`处理。

5. **错误判定与校验**:
   - 当replica的`prediction`与`gold`不一致时，判定为预测错误。
   - **强制校验**：验证replica的`gold`与individual的`gold`是否一致，不一致则抛出异常并报告具体的文件名、key 和不匹配的值。

6. **输出结果**:
   - 返回包含所有错误数据的字典或列表。
   - 结果中需包含原始`example_abbr`、新的定位信息（文件名、文件内key）、预测值和标准答案。

# Anti-Patterns
- **不要直接用主文件的 key 去分片文件里查找**（例如不要在 `*_1.json` 里找 key "45"），因为分片文件内部 key 是重置的，必须使用累积索引。
- 不要假设`prediction`或`gold`一定是字符串，必须处理列表类型。
- 不要忽略文件编号的排序，必须按数字顺序读取individual文件以确保累积索引正确。
- 不要忽略 `gold` 值的校验步骤，不一致必须报错。
- 不要硬编码具体的文件路径或前缀，应使用变量或参数。

## Triggers

- 合并分片JSON文件
- 根据example_abbr映射individual文件
- 校验预测错误数据
- 累积索引查找数据
- OpenCompass结果比对脚本
