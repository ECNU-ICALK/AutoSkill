---
id: "395fe462-611e-4758-8d19-c084345e6553"
name: "Python列表字符串按分隔符转换为指定字典"
description: "将包含特定分隔符（'=='）的字符串列表转换为包含指定键（'name', 'version'）的字典列表。"
version: "0.1.0"
tags:
  - "python"
  - "数据转换"
  - "列表"
  - "字典"
  - "flask"
triggers:
  - "把list数据转化为字典"
  - "list转dict特定格式"
  - "字符串分割转字典"
  - "a==x 转字典"
---

# Python列表字符串按分隔符转换为指定字典

将包含特定分隔符（'=='）的字符串列表转换为包含指定键（'name', 'version'）的字典列表。

## Prompt

# Role & Objective
编写Python程序，将特定格式的字符串列表转换为字典列表。

# Operational Rules & Constraints
1. 输入为一个字符串列表，例如 `['a==x', 'b==y']`。
2. 遍历列表中的每个字符串。
3. 使用 `split('==')` 方法拆分字符串。
4. 将拆分后的第一部分赋值给字典的 `name` 字段。
5. 将拆分后的第二部分赋值给字典的 `version` 字段。
6. 将生成的字典对象添加到结果列表中。
7. 代码环境为 Python 2 和 Flask 框架。

# Anti-Patterns
- 不要使用 `eval()` 函数。
- 不要忽略分隔符 '=='。

## Triggers

- 把list数据转化为字典
- list转dict特定格式
- 字符串分割转字典
- a==x 转字典
