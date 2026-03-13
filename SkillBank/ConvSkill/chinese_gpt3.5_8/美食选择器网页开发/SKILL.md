---
id: "dc421231-c396-4836-a5ad-0bfafd1ab65a"
name: "美食选择器网页开发"
description: "开发一个基于Django的美食选择器网页，包含随机选择功能和可视化转盘交互。"
version: "0.1.0"
tags:
  - "Django"
  - "美食选择器"
  - "转盘"
  - "随机选择"
  - "Canvas"
triggers:
  - "帮我写个美食选择器"
  - "做个随机选吃的网页"
  - "用Django做个转盘选美食"
  - "写个美食抽奖转盘"
  - "做个随机选择午餐的网页"
---

# 美食选择器网页开发

开发一个基于Django的美食选择器网页，包含随机选择功能和可视化转盘交互。

## Prompt

# Role & Objective
开发一个Django网页应用，实现美食随机选择功能，并提供转盘可视化交互。

# Communication & Style Preferences
使用中文进行代码注释和界面文本。代码结构清晰，模块化实现。

# Operational Rules & Constraints
1. 使用Python的random.choice实现随机选择
2. 使用Django框架构建后端
3. 前端使用HTML5 Canvas绘制转盘
4. 必须包含按钮触发选择机制
5. 转盘需展示所有美食选项
6. 点击按钮后转盘旋转并随机停止
7. 使用JavaScript控制转盘动画
8. 支持爬虫获取美食数据（可选）

# Anti-Patterns
- 不要使用硬编码的美食列表，应支持动态配置
- 不要忽略转盘动画的流畅性
- 不要缺少按钮点击防重复机制

# Interaction Workflow
1. 用户访问页面显示转盘和按钮
2. 用户点击按钮触发转盘旋转
3. 转盘旋转动画执行
4. 随机选择美食并显示结果

## Triggers

- 帮我写个美食选择器
- 做个随机选吃的网页
- 用Django做个转盘选美食
- 写个美食抽奖转盘
- 做个随机选择午餐的网页
