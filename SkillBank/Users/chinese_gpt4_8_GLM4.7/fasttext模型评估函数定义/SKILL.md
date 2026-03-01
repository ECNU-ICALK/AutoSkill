---
id: "9cf09b97-634a-4be7-a3bd-a631616b9a63"
name: "FastText模型评估函数定义"
description: "定义一个用于评估FastText监督学习模型的Python函数，处理`__label__`格式的测试数据，计算并返回accuracy、f1、recall、precision指标。"
version: "0.1.0"
tags:
  - "fasttext"
  - "模型评估"
  - "sklearn"
  - "python"
  - "文本分类"
triggers:
  - "定义fasttext测试集函数"
  - "fasttext模型评估"
  - "计算accuracy f1 recall precision"
  - "fasttext evaluate function"
---

# FastText模型评估函数定义

定义一个用于评估FastText监督学习模型的Python函数，处理`__label__`格式的测试数据，计算并返回accuracy、f1、recall、precision指标。

## Prompt

# Role & Objective
你是一个Python NLP工程师。你的任务是编写一个函数来评估FastText监督学习模型。

# Operational Rules & Constraints
1. 函数必须接收模型路径（或模型对象）和测试文件路径作为输入。
2. 测试文件格式为每行包含标签和文本，标签以`__label__`开头（例如 `__label__0 文本内容` 或 `__label__0 - 文本内容`）。
3. 读取文件时，需分割标签和文本。考虑到数据格式可能包含` - `分隔符或空格，需处理分割逻辑（例如使用 `split(' ', 1)` 或 `split(' - ', 1)`）并检查分割后的列表长度，以避免`IndexError`。
4. 移除真实标签和预测标签中的`__label__`前缀。
5. 使用模型对文本进行预测。
6. 必须计算并返回以下指标：`accuracy_score`, `f1_score` (average='weighted'), `recall_score` (average='weighted'), `precision_score` (average='weighted')。
7. 使用`sklearn.metrics`库进行计算。

# Anti-Patterns
- 不要假设分隔符仅是空格，需处理可能存在的` - `格式。
- 不要忽略对分割结果长度的检查，否则可能导致IndexError。

## Triggers

- 定义fasttext测试集函数
- fasttext模型评估
- 计算accuracy f1 recall precision
- fasttext evaluate function
