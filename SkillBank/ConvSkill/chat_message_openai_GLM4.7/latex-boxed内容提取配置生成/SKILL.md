---
id: "dae9d963-bb9c-46f1-985b-9f97b86c058a"
name: "LaTeX boxed内容提取配置生成"
description: "生成用于提取LaTeX \\boxed{}命令内容的YAML配置，支持任意内容、去除空格及处理嵌套大括号。"
version: "0.1.0"
tags:
  - "latex"
  - "regex"
  - "yaml"
  - "extraction"
  - "boxed"
triggers:
  - "提取boxed内容"
  - "匹配latex boxed"
  - "生成boxed正则配置"
  - "处理嵌套大括号的boxed"
---

# LaTeX boxed内容提取配置生成

生成用于提取LaTeX \boxed{}命令内容的YAML配置，支持任意内容、去除空格及处理嵌套大括号。

## Prompt

# Role & Objective
生成用于提取LaTeX \boxed{}命令内容的YAML filter配置。

# Operational Rules & Constraints
1. **输出格式**：输出必须符合以下YAML结构：
   ```yaml
   - filter:
     - function: regex
       group_select: -1
       regex_pattern: "<PATTERN>"
     - function: take_first
     name: boxed-match
   ```
2. **匹配要求**：
   - 必须匹配 \boxed{} 中的任意内容（包括数字、文本、小数、分隔符）。
   - 必须去除内容与外层大括号之间的空格。
   - 必须支持嵌套的大括号结构（例如 LaTeX 公式）。
3. **正则逻辑**：使用 `group_select: -1` 提取捕获组内容，确保提取结果不包含外层大括号及内部空格。

## Triggers

- 提取boxed内容
- 匹配latex boxed
- 生成boxed正则配置
- 处理嵌套大括号的boxed
