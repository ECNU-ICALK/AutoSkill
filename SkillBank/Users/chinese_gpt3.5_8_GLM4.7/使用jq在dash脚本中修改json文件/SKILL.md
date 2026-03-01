---
id: "6c498f39-429e-4af1-81b8-b3e619ba087b"
name: "使用jq在Dash脚本中修改JSON文件"
description: "在Dash脚本中使用jq工具修改JSON文件的键值对，通过--arg参数传递变量以避免转义问题，并使用临时文件实现原文件覆盖。"
version: "0.1.0"
tags:
  - "shell"
  - "dash"
  - "jq"
  - "json"
  - "脚本"
triggers:
  - "dash脚本修改json"
  - "jq修改键值"
  - "shell脚本jq变量"
  - "dash jq update json"
  - "jq dash脚本"
---

# 使用jq在Dash脚本中修改JSON文件

在Dash脚本中使用jq工具修改JSON文件的键值对，通过--arg参数传递变量以避免转义问题，并使用临时文件实现原文件覆盖。

## Prompt

# Role & Objective
编写Dash脚本，使用jq工具修改JSON文件中的指定键值对。

# Operational Rules & Constraints
1. 脚本必须使用 `#!/bin/sh` 作为shebang。
2. 使用 `read` 命令接收用户输入的键和值，分别赋值给变量 `key` 和 `arg`。
3. 使用 `jq` 命令修改JSON文件，必须使用 `--arg` 选项传递变量，格式为 `jq --arg key "${key}" --arg arg "${arg}" '.[$key] = $arg'`，以确保反斜杠等特殊字符不被错误转义。
4. 修改操作必须通过输出到临时文件（如 `temp`）再移动回原文件的方式实现，以避免文件损坏。
5. 所有代码输出必须使用Markdown代码块。

# Anti-Patterns
- 不要直接重定向输出到原文件，必须使用临时文件中转。
- 不要在jq表达式中直接拼接Shell变量字符串，应使用--arg传递。

## Triggers

- dash脚本修改json
- jq修改键值
- shell脚本jq变量
- dash jq update json
- jq dash脚本
