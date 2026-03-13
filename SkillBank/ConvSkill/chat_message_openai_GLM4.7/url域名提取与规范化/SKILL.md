---
id: "6a197f38-1b1c-485b-92dd-e2e3950ac265"
name: "URL域名提取与规范化"
description: "从URL中提取规范化域名，去除协议头和www前缀，并限制子域名最多保留3级。"
version: "0.1.0"
tags:
  - "python"
  - "url"
  - "domain"
  - "extraction"
  - "normalization"
triggers:
  - "抽domain"
  - "提取域名"
  - "域名规范化"
  - "保留三个子域名"
  - "去除www前缀"
---

# URL域名提取与规范化

从URL中提取规范化域名，去除协议头和www前缀，并限制子域名最多保留3级。

## Prompt

# Role & Objective
执行URL域名提取任务，将输入的URL转换为特定格式的规范化域名。

# Operational Rules & Constraints
1. **去除协议头**：移除 `http://` 或 `https://` 等协议头。
2. **去除www前缀**：检查主机名部分，如果点号数量大于1且第一段包含'www'，则移除第一段（避免误删如bestwwws.com的情况）。
3. **解析域名组件**：识别子域名、主域名和后缀。
4. **限制子域名层级**：如果存在子域名，仅保留最后3级子域名。
5. **拼接结果**：将处理后的子域名、主域名和后缀拼接成完整字符串。

# Anti-Patterns
- 不要保留协议头。
- 不要保留超过3级的子域名。
- 不要错误地移除包含www但不是前缀的域名部分。

## Triggers

- 抽domain
- 提取域名
- 域名规范化
- 保留三个子域名
- 去除www前缀
