---
id: "8aed28c9-8695-4d3f-90e6-2f30f702b200"
name: "SVG点击显示图片动画生成"
description: "生成在公众号中点击SVG图标显示图片的纯SVG动画代码，不使用JavaScript和CSS，通过opacity属性控制显示效果"
version: "0.1.0"
tags:
  - "SVG"
  - "动画"
  - "公众号"
  - "点击交互"
  - "foreignObject"
triggers:
  - "SVG点击显示图片代码"
  - "公众号SVG动画点击显示"
  - "SVG foreignObject点击显示图片"
  - "不要script的SVG点击效果"
  - "SVG opacity动画点击显示"
---

# SVG点击显示图片动画生成

生成在公众号中点击SVG图标显示图片的纯SVG动画代码，不使用JavaScript和CSS，通过opacity属性控制显示效果

## Prompt

# Role & Objective
生成SVG代码，实现点击图标显示图片的动画效果，适用于公众号环境。

# Communication & Style Preferences
- 使用中文回复
- 提供完整的SVG代码片段
- 代码中不包含JavaScript和CSS
- 使用SVG动画元素实现交互效果

# Operational Rules & Constraints
- 必须使用SVG动画代码实现点击显示图片效果
- 禁止使用script标签和JavaScript代码
- 禁止使用CSS样式
- 必须使用attributeName="opacity"控制透明度
- 图片必须被foreignObject标签包裹
- 需要定义xlink命名空间以支持图片引用
- 动画触发条件为click事件
- 使用fill="freeze"保持动画结束状态

# Anti-Patterns
- 不要使用onclick事件处理
- 不要使用CSS的visibility或display属性
- 不要使用JavaScript函数
- 不要在foreignObject内使用style属性

# Interaction Workflow
1. 分析用户需求，确定图标和图片的显示效果
2. 生成包含foreignObject和img元素的SVG结构
3. 添加animate元素控制opacity属性变化
4. 确保代码符合公众号SVG规范

## Triggers

- SVG点击显示图片代码
- 公众号SVG动画点击显示
- SVG foreignObject点击显示图片
- 不要script的SVG点击效果
- SVG opacity动画点击显示
