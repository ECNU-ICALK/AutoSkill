---
id: "5c15caac-8d15-4227-9aa6-c14f8dfb0b69"
name: "过滤模型推理内容用于评测"
description: "在SFE数据集评测前，自动移除模型预测中的推理内容（如<details>标签或<answer>前的文本），确保仅将最终答案送入判分模型。"
version: "0.1.2"
tags:
  - "代码"
  - "评测"
  - "数据清洗"
  - "预处理"
  - "正则"
  - "文本处理"
  - "python"
  - "模型输出"
  - "正则表达式"
  - "模型后处理"
  - "JSONL"
triggers:
  - "过滤推理内容"
  - "去除思考过程"
  - "清理模型输出"
  - "评测前处理"
  - "SFE评测预处理"
  - "抽取thinking content"
  - "删除<think>标签"
  - "清理模型回复"
  - "移除思考过程"
  - "处理DeepSeek输出"
  - "帮我写个对模型回复抽取thinking content的python代码"
  - "删除模型回复中的thinking标签"
  - "清理<think>标签内容"
  - "提取模型思考过程"
  - "处理模型输出中的思考痕迹"
examples:
  - input: "模型输出：'Okay, let me approach... <details>...</details> \\n\\n<answer>...'"
    output: "只保留：<answer>...</answer>"
---

# 过滤模型推理内容用于评测

在SFE数据集评测前，自动移除模型预测中的推理内容（如<details>标签或<answer>前的文本），确保仅将最终答案送入判分模型。

## Prompt

你是一个代码预处理助手。你的任务是在SFE数据集的评测脚本中，对模型预测结果进行预处理。

具体要求如下：
1. 读取评测数据（包含prediction列）。
2. 对每一行的prediction字段应用过滤函数，移除推理内容。
3. 推理内容通常出现在以下两种模式中：
   - <details>...</details> 标签对（常见于思考过程）。
   - <answer> 标签之前的所有文本内容。
4. 过滤后的prediction将用于后续的make_prompt和判分，确保评测的准确性。

请编写一个Python函数 `filter_think_content`，并修改 `SFE`类的 `evaluate`方法，在加载数据后、调用判分前对prediction列进行批量过滤。

## Triggers

- 过滤推理内容
- 去除思考过程
- 清理模型输出
- 评测前处理
- SFE评测预处理
- 抽取thinking content
- 删除<think>标签
- 清理模型回复
- 移除思考过程
- 处理DeepSeek输出

## Examples

### Example 1

Input:

  模型输出：'Okay, let me approach... <details>...</details> \n\n<answer>...'

Output:

  只保留：<answer>...</answer>
