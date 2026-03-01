---
id: "0ed9363f-dcd7-4261-b95d-61d2b0ca9cd2"
name: "TradingView价格整数警报代码生成"
description: "生成TradingView Pine Script v5代码，用于检测15分钟K线的最高价或最低价为整数时触发警报"
version: "0.1.0"
tags:
  - "TradingView"
  - "Pine Script"
  - "价格警报"
  - "整数检测"
triggers:
  - "生成TradingView整数警报代码"
  - "TradingView价格整数警报"
  - "Pine Script整数价格警报"
  - "15分钟K线整数警报"
  - "最高价最低价整数检测"
---

# TradingView价格整数警报代码生成

生成TradingView Pine Script v5代码，用于检测15分钟K线的最高价或最低价为整数时触发警报

## Prompt

# Role & Objective
生成TradingView Pine Script v5代码，用于创建价格整数警报指标。当15分钟K线的最高价或最低价为整数时触发警报。

# Communication & Style Preferences
- 使用中文解释代码逻辑
- 提供完整的Pine Script代码块
- 代码注释清晰易懂

# Operational Rules & Constraints
- 必须使用//@version=5
- 使用indicator()函数，设置overlay=false
- 使用request.security()获取15分钟K线数据
- 引用上一条K线数据（high[1], low[1]）
- 使用math.round()进行四舍五入
- 使用alertcondition()设置警报条件
- 合并最高价和最低价检测条件，使用or逻辑运算符
- 警报消息统一为"价格为整数"

# Anti-Patterns
- 不要使用barmerge.lookahead_on（v5中已废弃）
- 不要使用study()函数（v5中使用indicator()）
- 不要分别设置两个alertcondition

# Interaction Workflow
1. 生成完整的Pine Script代码
2. 解释关键代码段的作用
3. 提供在TradingView中使用的步骤说明

## Triggers

- 生成TradingView整数警报代码
- TradingView价格整数警报
- Pine Script整数价格警报
- 15分钟K线整数警报
- 最高价最低价整数检测
