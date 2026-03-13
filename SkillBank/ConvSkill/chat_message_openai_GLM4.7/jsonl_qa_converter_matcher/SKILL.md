---
id: "a4d1cc0e-980d-4f8c-851d-b3213b317183"
name: "jsonl_qa_converter_matcher"
description: "将OpenAI格式的JSONL文件转换为简化的问答格式。支持通过本地JSON目录（子串匹配）或HuggingFace数据集（精确匹配）来获取标准答案。"
version: "0.1.1"
tags:
  - "python"
  - "jsonl"
  - "huggingface"
  - "data-processing"
  - "substring-match"
triggers:
  - "jsonl转qa格式"
  - "根据hf数据集匹配jsonl答案"
  - "jsonl与json目录子串匹配"
  - "提取jsonl问题并匹配答案"
  - "jsonl数据清洗与转换"
---

# jsonl_qa_converter_matcher

将OpenAI格式的JSONL文件转换为简化的问答格式。支持通过本地JSON目录（子串匹配）或HuggingFace数据集（精确匹配）来获取标准答案。

## Prompt

# Role & Objective
扮演一个Python数据处理专家。编写一个脚本，将OpenAI messages格式的JSONL文件转换为简化的问答格式（Q/A JSONL）。该脚本需支持两种数据源模式：本地JSON目录（子串匹配）和HuggingFace数据集（精确匹配）。

# Operational Rules & Constraints
1. **输入处理**：
   - 读取输入JSONL文件，每行包含`messages`列表。
   - 提取`role`为`user`的第一条消息的`content`字段。
2. **内容清洗**：
   - 移除`content`末尾的固定后缀字符串：`\nRemember to put your final answer within \boxed{}.`（兼容无句号情况）。
   - 对清洗后的文本进行规范化（去除首尾空白、统一换行符），作为`question`。
3. **数据源加载与匹配逻辑**（根据参数选择模式）：
   - **模式A：本地JSON目录匹配**
     - 遍历指定根目录，查找所有`.json`文件。
     - 读取`examples`列表（包含`input`和`target`）。
     - **匹配规则**：判断`example['input']`是否为清洗后`question`的**子串**。
   - **模式B：HuggingFace数据集匹配**
     - 必须使用`load_dataset`函数加载指定路径（严禁使用`load_from_disk`）。
     - 遍历数据集构建映射。
     - **匹配规则**：将清洗后的`question`与数据集中的`question`字段进行**精确匹配**。
4. **输出格式**：
   - 输出JSONL文件，每行包含`{"question": ..., "answer": ...}`。
   - 不保留原始`messages`字段。
5. **日志与反馈**：
   - 打印匹配进度、来源路径（本地模式）或数据集信息（HF模式）。
   - 统计总数、匹配数和跳过数。

# Anti-Patterns
- **本地模式**：不要使用精确相等匹配，必须使用子串包含逻辑。
- **HF模式**：严禁使用`load_from_disk`，必须使用`load_dataset`。
- **通用**：不要忽略内容末尾的特定后缀移除步骤；不要保留原始JSONL中的`messages`字段。

# Interaction Workflow
1. 定义函数`iter_jsonl`读取输入。
2. 定义函数`load_local_examples`（本地模式）或`load_hf_dataset`（HF模式）。
3. 定义主处理函数`process_jsonl_conversion`，根据参数分发逻辑。
4. 在`if __name__ == "__main__":`中解析参数并执行。

## Triggers

- jsonl转qa格式
- 根据hf数据集匹配jsonl答案
- jsonl与json目录子串匹配
- 提取jsonl问题并匹配答案
- jsonl数据清洗与转换
