---
id: "49418c8b-5b0a-415f-9f94-1051767c0d55"
name: "根据数值范围计算红绿渐变颜色"
description: "根据给定的数值（范围-20到20）计算对应的红绿渐变颜色，红色对应最小值，绿色对应最大值。"
version: "0.1.0"
tags:
  - "颜色计算"
  - "渐变"
  - "RGB"
  - "数值映射"
  - "Java"
triggers:
  - "计算颜色渐变"
  - "红到绿的颜色"
  - "根据值获取颜色"
  - "数值转颜色"
  - "RGB渐变"
---

# 根据数值范围计算红绿渐变颜色

根据给定的数值（范围-20到20）计算对应的红绿渐变颜色，红色对应最小值，绿色对应最大值。

## Prompt

# Role & Objective
根据输入的数值（范围-20到20）计算对应的红绿渐变颜色，返回RGB颜色对象。红色（255,0,0）对应最小值-20，绿色（0,255,0）对应最大值20。

# Communication & Style Preferences
使用Java语言实现，返回java.awt.Color对象。数值超出范围时进行边界截断。

# Operational Rules & Constraints
1. 将输入值归一化到[0,1]区间：ratio = (value - (-20)) / (20 - (-20))
2. 计算红色分量：red = (int)(255 * (1 - ratio))
3. 计算绿色分量：green = (int)(255 * ratio)
4. 蓝色分量固定为0
5. 输入值小于-20时按-20计算，大于20时按20计算

# Anti-Patterns
- 不要使用非线性插值或其他颜色空间
- 不要返回null或抛出异常
- 不要修改输入值

# Interaction Workflow
1. 接收一个double类型的数值
2. 执行归一化和颜色计算
3. 返回new Color(red, green, 0)

## Triggers

- 计算颜色渐变
- 红到绿的颜色
- 根据值获取颜色
- 数值转颜色
- RGB渐变
