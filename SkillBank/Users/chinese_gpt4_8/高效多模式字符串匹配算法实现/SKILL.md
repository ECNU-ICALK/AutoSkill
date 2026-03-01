---
id: "b7da2b2d-416d-4908-a0d8-b8ae458e8f41"
name: "高效多模式字符串匹配算法实现"
description: "当需要在大量关键词（十万以上）中高效查找目标字符串包含哪些关键词时，使用Aho-Corasick算法实现线性时间复杂度的多模式匹配。"
version: "0.1.0"
tags:
  - "字符串匹配"
  - "算法"
  - "性能优化"
  - "Aho-Corasick"
  - "Python"
triggers:
  - "高效查找字符串包含哪些关键词"
  - "大量关键词匹配算法"
  - "十万以上字符串数组匹配"
  - "多模式字符串匹配"
  - "Aho-Corasick算法实现"
---

# 高效多模式字符串匹配算法实现

当需要在大量关键词（十万以上）中高效查找目标字符串包含哪些关键词时，使用Aho-Corasick算法实现线性时间复杂度的多模式匹配。

## Prompt

# Role & Objective
实现一个高效的Python函数，用于在原始字符串中查找包含哪些来自大型字符串数组（十万以上）的子字符串。要求使用Aho-Corasick算法以保证最高效率。

# Communication & Style Preferences
- 使用Python标准库或第三方库实现
- 代码需包含清晰的注释说明关键步骤
- 提供安装依赖的指令
- 返回匹配到的子字符串列表

# Operational Rules & Constraints
- 必须使用Aho-Corasick算法实现多模式匹配
- 支持大规模关键词数组（十万以上）
- 时间复杂度应为O(n+m)，其中n为目标字符串长度，m为所有关键词总长度
- 返回所有匹配到的关键词，不重复
- 使用pyahocorasick库实现

# Anti-Patterns
- 不要使用逐个遍历关键词的朴素匹配方法
- 不要使用正则表达式拼接的方式
- 不要忽略大小写敏感性问题（除非明确要求）

# Interaction Workflow
1. 安装pyahocorasick库
2. 构建Aho-Corasick自动机
3. 添加所有关键词到自动机
4. 执行匹配并返回结果

## Triggers

- 高效查找字符串包含哪些关键词
- 大量关键词匹配算法
- 十万以上字符串数组匹配
- 多模式字符串匹配
- Aho-Corasick算法实现
