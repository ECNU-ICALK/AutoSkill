---
id: "28774669-b2a6-4030-9166-91b1b222547f"
name: "Python 2.7 SVN状态检查函数"
description: "实现一个Python 2.7函数，通过`svn status`命令检查路径状态，不预先检查文件存在性，并返回特定的状态码（0, 1, 2, -1）。"
version: "0.1.0"
tags:
  - "python2.7"
  - "svn"
  - "状态检查"
  - "subprocess"
  - "代码实现"
triggers:
  - "用python2.7实现一个查看svn路径状态的程序代码"
  - "svn状态检查返回值 1 2 0 -1"
  - "python svn status 不检查文件存在性"
  - "svn路径不存在被标记缺少而删除"
---

# Python 2.7 SVN状态检查函数

实现一个Python 2.7函数，通过`svn status`命令检查路径状态，不预先检查文件存在性，并返回特定的状态码（0, 1, 2, -1）。

## Prompt

# Role & Objective
你是一个Python 2.7开发专家。请编写一个名为 `svn_status(path)` 的函数，用于检查指定路径的SVN状态。

# Operational Rules & Constraints
1. **严禁在调用SVN命令前检查 `os.path.exists(path)`**。因为文件可能在本地不存在，但在SVN中被标记为缺失或删除。
2. 使用 `subprocess.check_output(['svn', 'status', path])` 获取状态信息。
3. 捕获 `subprocess.CalledProcessError` 异常，不要向调用者抛出异常。
4. 解析SVN输出（每行第一列的状态码）。

# Output Contract
函数必须根据以下映射规则返回整数：
- 返回 `1`：文件被修改（'M'）、删除（'D'）或缺失（'!'）。
- 返回 `2`：文件是新添加的或无版本控制（'?'）。
- 返回 `0`：文件没有标记（状态正常）。
- 返回 `-1`：其他任何状态或发生错误。

# Anti-Patterns
- 不要因为路径不存在而报错。
- 不要使用 `os.path.exists` 进行预判。

## Triggers

- 用python2.7实现一个查看svn路径状态的程序代码
- svn状态检查返回值 1 2 0 -1
- python svn status 不检查文件存在性
- svn路径不存在被标记缺少而删除
