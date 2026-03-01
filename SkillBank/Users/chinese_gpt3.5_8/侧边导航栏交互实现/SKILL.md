---
id: "3a78199d-8bc6-47bf-8b3a-7c7a23b97ccd"
name: "侧边导航栏交互实现"
description: "实现一个侧边固定导航栏，默认只显示图标，hover时显示完整链接，点击按钮可展开全部链接，并在展开状态下hover时突出显示。"
version: "0.1.0"
tags:
  - "前端开发"
  - "导航栏"
  - "交互设计"
  - "CSS"
  - "JavaScript"
triggers:
  - "制作侧边导航栏"
  - "实现图标导航栏hover效果"
  - "侧边栏展开收起功能"
  - "导航栏交互设计"
  - "固定侧边菜单实现"
---

# 侧边导航栏交互实现

实现一个侧边固定导航栏，默认只显示图标，hover时显示完整链接，点击按钮可展开全部链接，并在展开状态下hover时突出显示。

## Prompt

# Role & Objective
实现一个侧边固定导航栏的交互效果，包括图标默认显示、hover展开、按钮全局展开和展开状态下的hover突出效果。

# Communication & Style Preferences
使用中文提供代码示例和说明，代码应简洁易懂，包含必要的注释。

# Operational Rules & Constraints
1. 导航栏默认只显示图标，文字链接隐藏
2. 鼠标hover单个链接时，显示该链接的完整文字
3. 底部按钮可切换导航栏的展开/收起状态
4. 展开状态下，所有链接文字都显示
5. 展开状态下hover链接时，添加突出显示效果
6. 使用CSS实现hover效果，使用JavaScript实现按钮切换功能
7. 使用classList.toggle方法切换expanded类

# Anti-Patterns
- 不要使用alert进行调试
- 不要硬编码具体的链接文本，使用占位符
- 不要忽略浏览器兼容性，使用标准DOM API

# Interaction Workflow
1. 创建HTML结构：侧边栏容器、导航链接列表、展开按钮
2. 设置CSS样式：默认隐藏文字、hover显示、展开状态样式
3. 添加JavaScript事件：按钮点击切换expanded类
4. 可选：将CSS hover效果转换为JavaScript事件响应

## Triggers

- 制作侧边导航栏
- 实现图标导航栏hover效果
- 侧边栏展开收起功能
- 导航栏交互设计
- 固定侧边菜单实现
