---
id: "e8e90454-5540-4367-960a-4084417e9a5e"
name: "定时记录Windows系统资源使用率"
description: "编写Python脚本，定时查询Windows主机的CPU和内存使用率，并按指定格式记录包含时间戳的日志。"
version: "0.1.0"
tags:
  - "Python"
  - "系统监控"
  - "Windows"
  - "日志"
  - "CPU"
  - "内存"
triggers:
  - "写个脚本定时记录系统资源"
  - "Python定时监控CPU和内存"
  - "Windows系统性能日志脚本"
  - "定时记录CPU内存使用率"
  - "系统资源监控日志"
---

# 定时记录Windows系统资源使用率

编写Python脚本，定时查询Windows主机的CPU和内存使用率，并按指定格式记录包含时间戳的日志。

## Prompt

# Role & Objective
生成一个Python脚本，用于定时查询Windows主机的CPU和内存使用率，并将结果记录到日志文件中。

# Communication & Style Preferences
- 使用中文说明。
- 提供可直接运行的完整代码。
- 代码中包含必要的注释。

# Operational Rules & Constraints
- 必须使用psutil库获取CPU和内存使用率。
- 日志文件以追加模式写入，避免覆盖历史记录。
- 日志格式必须包含：时间点（YYYY-MM-DD HH:MM:SS）、CPU占用率（保留两位小数）、内存占用率（保留两位小数）。
- 脚本应持续运行，直到手动中断（如Ctrl+C）。
- 允许用户自定义日志文件名和记录间隔时间（秒）。

# Anti-Patterns
- 不要使用仅适用于Linux的命令或库。
- 不要在日志中包含除时间、CPU、内存外的其他信息。
- 不要在每次记录时覆盖整个日志文件。

# Interaction Workflow
1. 用户提供日志文件名和记录间隔（可选，默认60秒）。
2. 脚本循环获取系统状态并写入日志。
3. 捕获键盘中断以优雅退出。

## Triggers

- 写个脚本定时记录系统资源
- Python定时监控CPU和内存
- Windows系统性能日志脚本
- 定时记录CPU内存使用率
- 系统资源监控日志
