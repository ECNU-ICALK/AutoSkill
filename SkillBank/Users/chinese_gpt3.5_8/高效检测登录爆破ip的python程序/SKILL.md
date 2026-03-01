---
id: "6a8e3cb7-6f51-45cf-9aa0-562a2b2ef4dd"
name: "高效检测登录爆破IP的Python程序"
description: "编写Python2程序，以块数据方式读取大型auth.log文件，检测最近5分钟内'connecting closed'次数超过10次的IP并提示爆破行为，避免全文件遍历以提升性能。"
version: "0.1.0"
tags:
  - "Python2"
  - "日志分析"
  - "安全检测"
  - "爆破检测"
  - "性能优化"
triggers:
  - "写一个程序检测登录爆破"
  - "从auth.log检测爆破IP"
  - "块数据方式读取日志文件"
  - "检测connecting closed次数"
  - "避免遍历大文件检测爆破"
---

# 高效检测登录爆破IP的Python程序

编写Python2程序，以块数据方式读取大型auth.log文件，检测最近5分钟内'connecting closed'次数超过10次的IP并提示爆破行为，避免全文件遍历以提升性能。

## Prompt

# Role & Objective
编写Python2程序，从大型auth.log文件中高效检测登录爆破行为。程序应以块数据方式读取，避免全文件遍历，筛选最近5分钟内'connecting closed'次数超过10次的IP并输出警告。

# Communication & Style Preferences
- 使用Python2语法
- 代码需包含中文注释说明关键步骤
- 输出信息使用中文提示

# Operational Rules & Constraints
- 必须使用块数据读取方式，禁止逐行遍历整个文件
- 时间窗口为当前时间前5分钟（300秒）
- 检测关键词为'connecting closed'
- 阈值为10次，超过则判定为爆破
- 输出格式：IP地址 + 事件次数 + '登录爆破行为'提示
- 优先使用tail命令获取文件末尾数据以减少读取量
- 使用正则表达式提取IP和时间戳
- 处理大文件（GB级别）时需考虑内存效率

# Anti-Patterns
- 不要一次性读取整个文件到内存
- 不要使用低效的逐行遍历方式
- 不要忽略时间戳验证
- 不要硬编码文件路径，使用'/var/log/auth.log'作为默认路径

# Interaction Workflow
1. 计算当前时间前5分钟的时间戳
2. 使用tail命令或块读取方式获取文件数据
3. 正则匹配IP和时间戳
4. 统计各IP的'connecting closed'次数
5. 输出超过阈值的IP及警告信息

## Triggers

- 写一个程序检测登录爆破
- 从auth.log检测爆破IP
- 块数据方式读取日志文件
- 检测connecting closed次数
- 避免遍历大文件检测爆破
