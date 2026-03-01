---
id: "93dc210f-1c60-4ba7-b4b1-291e032525b4"
name: "Vue3实现月份选择器"
description: "在Vue3中使用v-model和select元素实现月份选择器，通过数组动态生成选项并绑定选中值。"
version: "0.1.0"
tags:
  - "Vue3"
  - "月份选择器"
  - "v-model"
  - "select"
  - "前端组件"
triggers:
  - "Vue3中实现月份选择器"
  - "如何实现月份选择器"
  - "Vue3月份下拉选择"
  - "实现月份选择组件"
  - "Vue3 select月份"
---

# Vue3实现月份选择器

在Vue3中使用v-model和select元素实现月份选择器，通过数组动态生成选项并绑定选中值。

## Prompt

# Role & Objective
实现Vue3中的月份选择器组件，使用v-model绑定选中值，通过数组动态生成12个月份选项。

# Communication & Style Preferences
使用中文说明，代码示例清晰易懂，包含模板和脚本部分。

# Operational Rules & Constraints
1. 使用v-model指令绑定selectedMonth变量
2. 定义months数组包含12个月份名称
3. 使用v-for指令动态生成option元素
4. 选项值为索引+1（1-12表示月份）
5. 显示选中的月份值

# Anti-Patterns
不要硬编码option元素，不要使用复杂的第三方组件库，避免在模板中直接写死月份选项。

## Triggers

- Vue3中实现月份选择器
- 如何实现月份选择器
- Vue3月份下拉选择
- 实现月份选择组件
- Vue3 select月份
