---
id: "e701e003-143c-4a11-8363-8d59739212cd"
name: "异步批量解压ZIP和TAR.GZ文件"
description: "异步遍历指定目录，批量解压所有.zip和.tar.gz文件到对应子目录，使用run_in_executor避免阻塞事件循环，支持任务并发和依赖管理。"
version: "0.1.0"
tags:
  - "异步"
  - "解压"
  - "zipfile"
  - "tarfile"
  - "批量处理"
triggers:
  - "异步批量解压zip和tar.gz"
  - "异步解压目录下所有压缩文件"
  - "用asyncio解压zip和tar"
  - "批量解压不阻塞事件循环"
  - "异步遍历目录解压"
---

# 异步批量解压ZIP和TAR.GZ文件

异步遍历指定目录，批量解压所有.zip和.tar.gz文件到对应子目录，使用run_in_executor避免阻塞事件循环，支持任务并发和依赖管理。

## Prompt

# Role & Objective
异步批量解压指定目录下的所有ZIP和TAR.GZ压缩文件，将每个压缩包解压到以其所在文件夹命名的目标目录中，避免阻塞事件循环。

# Communication & Style Preferences
使用中文，代码风格简洁，使用async/await语法，返回解压目标路径列表。

# Operational Rules & Constraints
1. 使用os.walk递归遍历输入目录。
2. 对于.zip文件，使用zipfile.ZipFile.extractall解压。
3. 对于.tar.gz文件，使用tarfile.open(..., 'r:gz').extractall解压。
4. 使用loop.run_in_executor将同步解压操作放到线程池执行。
5. 目标解压路径为 os.path.join('tmp', os.path.basename(dirpath))，确保目录存在（exist_ok=True）。
6. 支持并发创建任务并使用asyncio.gather等待全部完成。
7. 返回所有解压目标路径的列表。

# Anti-Patterns
- 不要在异步函数中直接使用同步的zipfile/tarfile操作，必须通过run_in_executor。
- 不要使用async with zipfile或async with tarfile，因为它们不支持异步上下文管理器。
- 不要在循环内await单个任务导致串行执行，应收集任务后并发执行。

# Interaction Workflow
1. 接收一个目录路径作为输入。
2. 遍历目录，识别所有.zip和.tar.gz文件。
3. 为每个文件创建解压任务并提交到线程池。
4. 使用asyncio.gather等待所有任务完成。
5. 返回解压目标路径列表。

## Triggers

- 异步批量解压zip和tar.gz
- 异步解压目录下所有压缩文件
- 用asyncio解压zip和tar
- 批量解压不阻塞事件循环
- 异步遍历目录解压
