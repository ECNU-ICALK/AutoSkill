---
id: "63274a03-65c0-4b17-8750-7bfa868116c0"
name: "批量IP模型信息检查Shell脚本生成"
description: "生成一个Bash脚本，用于遍历硬编码的IP列表，通过curl查询模型信息接口，并统计'model_name'出现的次数。"
version: "0.1.0"
tags:
  - "shell"
  - "bash"
  - "curl"
  - "ip-list"
  - "batch-check"
triggers:
  - "写一个shell脚本实现 ip是一个列表"
  - "批量检查ip的model数量"
  - "生成shell脚本查询多个ip的模型信息"
---

# 批量IP模型信息检查Shell脚本生成

生成一个Bash脚本，用于遍历硬编码的IP列表，通过curl查询模型信息接口，并统计'model_name'出现的次数。

## Prompt

# Role & Objective
生成用于批量检查IP模型信息的Shell脚本。

# Operational Rules & Constraints
1. IP列表必须硬编码在脚本内部的数组变量中（如 `IPS=(...)`），严禁读取外部文件。
2. 使用 `curl` 命令访问 `/model/info` 接口，携带 `Authorization: Bearer sk-admin` 请求头。
3. 使用管道 `| jq | grep model_name | wc -l` 处理输出并统计数量。
4. 输出格式应为 `IP <tab> count`。
5. 脚本应包含基本的错误处理（如 `set -euo pipefail`）。

# Anti-Patterns
- 不要生成需要从文件读取IP列表的代码。
- 不要修改curl命令的核心逻辑或解析方式。

## Triggers

- 写一个shell脚本实现 ip是一个列表
- 批量检查ip的model数量
- 生成shell脚本查询多个ip的模型信息
