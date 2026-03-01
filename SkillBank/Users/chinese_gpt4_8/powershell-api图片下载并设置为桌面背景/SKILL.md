---
id: "8a018b04-6e7a-49be-b458-bc426af377f6"
name: "PowerShell API图片下载并设置为桌面背景"
description: "使用PowerShell发送POST请求下载图片，设置为桌面背景后自动删除的自动化脚本"
version: "0.1.0"
tags:
  - "PowerShell"
  - "自动化"
  - "API请求"
  - "桌面背景"
  - "文件下载"
triggers:
  - "powershell下载图片设置壁纸"
  - "API图片下载设置为桌面背景"
  - "powershell自动化设置壁纸"
  - "下载图片并设置为背景后删除"
  - "powershell post请求下载图片"
---

# PowerShell API图片下载并设置为桌面背景

使用PowerShell发送POST请求下载图片，设置为桌面背景后自动删除的自动化脚本

## Prompt

# Role & Objective
创建一个PowerShell自动化脚本，用于从API下载图片并设置为桌面背景，完成后自动清理临时文件。

# Communication & Style Preferences
- 使用PowerShell原生命令和.NET互操作
- 代码简洁清晰，包含必要的注释
- 处理异常情况，确保脚本健壮性

# Operational Rules & Constraints
1. 必须使用POST方法发送请求
2. 请求体为JSON格式，包含historyParam.code参数
3. 图片保存到系统下载文件夹
4. 使用Windows API设置桌面背景
5. 设置完成后必须删除临时图片文件
6. 添加适当的等待时间确保壁纸设置生效

# Anti-Patterns
- 不要使用硬编码的绝对路径
- 不要忽略异常处理
- 不要在设置壁纸前删除文件
- 不要使用第三方PowerShell模块

# Interaction Workflow
1. 定义API端点和请求参数
2. 构建JSON请求体
3. 发送POST请求并下载图片
4. 调用Windows API设置桌面背景
5. 等待确保设置生效
6. 删除临时图片文件

## Triggers

- powershell下载图片设置壁纸
- API图片下载设置为桌面背景
- powershell自动化设置壁纸
- 下载图片并设置为背景后删除
- powershell post请求下载图片
