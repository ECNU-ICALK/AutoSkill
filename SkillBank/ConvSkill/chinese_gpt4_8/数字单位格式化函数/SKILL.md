---
id: "cd9fa837-16ad-4571-ba52-dd5184062921"
name: "数字单位格式化函数"
description: "将数字转换为带千或万单位的字符串，支持指定小数位数或保留原始位数。"
version: "0.1.1"
tags:
  - "JavaScript"
  - "数字格式化"
  - "函数封装"
  - "单位转换"
  - "小数控制"
triggers:
  - "数字格式化带单位"
  - "金额格式化千k万w"
  - "formatNumberWithUnits"
  - "数字转k w单位"
  - "保留小数位格式化"
---

# 数字单位格式化函数

将数字转换为带千或万单位的字符串，支持指定小数位数或保留原始位数。

## Prompt

# Role & Objective
封装一个可复用的JavaScript函数，用于将数字格式化为带单位（千k、万w）的字符串，支持灵活控制小数位数。

# Communication & Style Preferences
代码应简洁、高效且易于理解。优先使用清晰的变量名和逻辑结构。

# Core Workflow
1. 定义函数 `formatNumberWithUnits(number, fixedDecimalPlace)`。
2. 根据数字大小选择单位（无单位、'k'、'w'）。
3. 根据参数 `fixedDecimalPlace` 处理小数位数。
4. 返回格式化后的字符串。

# Constraints & Style
1. 函数名：`formatNumberWithUnits`。
2. 参数：
   - `number` (number): 要格式化的数字。
   - `fixedDecimalPlace` (number|null, 可选): 指定小数位数，若为null则保留原始小数位数。
3. 单位规则：
   - 小于1000：直接返回数字字符串。
   - 1000-9999：除以1000，追加'k'。
   - 10000及以上：除以10000，追加'w'。
4. 小数处理：
   - `fixedDecimalPlace`为数字时：使用`toFixed`固定位数。
   - `fixedDecimalPlace`为null时：整数直接除，小数保留原始位数。
5. 返回值：格式化后的字符串。

# Anti-Patterns
- 不要修改原始数字。
- 不要处理超出JavaScript浮点精度范围的数字。
- 不要添加其他单位（如M、B）。

# Examples
- `formatNumberWithUnits(12345, 2) // '1.23w'`
- `formatNumberWithUnits(12345, null) // '1.2345w'`

## Triggers

- 数字格式化带单位
- 金额格式化千k万w
- formatNumberWithUnits
- 数字转k w单位
- 保留小数位格式化
