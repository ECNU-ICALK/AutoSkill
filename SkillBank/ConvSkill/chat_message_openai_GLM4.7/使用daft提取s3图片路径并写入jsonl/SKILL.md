---
id: "d7a07fdd-1dbb-409e-bafd-eee039a3243d"
name: "使用Daft提取S3图片路径并写入JSONL"
description: "使用Daft库读取S3上的图片文件，提取文件路径，并将路径列表写入本地的JSONL文件。"
version: "0.1.0"
tags:
  - "daft"
  - "s3"
  - "jsonl"
  - "python"
  - "数据处理"
triggers:
  - "daft读s3图片写jsonl"
  - "提取s3图片路径到jsonl"
  - "daft s3 image path to jsonl"
  - "使用daft读取s3图片路径"
---

# 使用Daft提取S3图片路径并写入JSONL

使用Daft库读取S3上的图片文件，提取文件路径，并将路径列表写入本地的JSONL文件。

## Prompt

# Role & Objective
使用Daft库从S3读取图片文件，提取文件路径，并将路径列表写入本地JSONL文件。

# Operational Rules & Constraints
1. 使用 `daft.read_images` 读取S3上的图片文件，支持通配符路径（如 `s3://bucket/prefix/**/*.jpg`）。
2. 使用 `select(col("path"))` 仅保留路径列。
3. 使用 `write_json("filename.jsonl")` 将数据写入本地JSONL文件。
4. 确保代码示例包含必要的导入（如 `import daft`, `from daft import col`）。

## Triggers

- daft读s3图片写jsonl
- 提取s3图片路径到jsonl
- daft s3 image path to jsonl
- 使用daft读取s3图片路径
