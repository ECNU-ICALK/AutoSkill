---
id: "c30161f7-c07c-49d1-a395-c5eef28fca04"
name: "C语言浮点数向零舍入"
description: "用C语言实现将双精度浮点数向零舍入为整数的程序，正数向下舍入，负数向上舍入。"
version: "0.1.0"
tags:
  - "C语言"
  - "浮点数"
  - "向零舍入"
  - "floor"
  - "ceil"
triggers:
  - "浮点数向零舍入"
  - "C语言向零舍入"
  - "正数向下负数向上舍入"
  - "双精度浮点数舍入"
  - "floor ceil舍入"
---

# C语言浮点数向零舍入

用C语言实现将双精度浮点数向零舍入为整数的程序，正数向下舍入，负数向上舍入。

## Prompt

# Role & Objective
编写C语言程序，实现双精度浮点数向零舍入功能。

# Communication & Style Preferences
使用标准C语言语法，代码简洁清晰，包含必要注释。

# Operational Rules & Constraints
1. 使用double类型接收输入
2. 使用math.h库的floor和ceil函数
3. 正数使用floor向下舍入
4. 负数使用ceil向上舍入
5. 输出格式为整数
6. 包含必要的头文件stdio.h和math.h

# Anti-Patterns
不要使用类型转换(int)直接截断，不要使用round函数，不要忽略负数情况。

# Interaction Workflow
1. 读取双精度浮点数输入
2. 判断正负
3. 根据正负选择floor或ceil
4. 输出舍入后的整数

## Triggers

- 浮点数向零舍入
- C语言向零舍入
- 正数向下负数向上舍入
- 双精度浮点数舍入
- floor ceil舍入
