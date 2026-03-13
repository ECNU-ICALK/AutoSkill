---
id: "e9ad642e-d0e5-4a9a-8b0f-5de0c1b5a543"
name: "HuggingFace 数据集并行上传与断点续传脚本生成"
description: "生成用于将本地文件夹所有文件上传至 HuggingFace 仓库的 Bash 脚本，支持断点续传、并行上传、自动重试及指定仓库子目录。"
version: "0.1.0"
tags:
  - "huggingface"
  - "bash"
  - "upload"
  - "parallel"
  - "resume"
triggers:
  - "huggingface 并行上传"
  - "断点续传上传脚本"
  - "批量上传文件到hf"
  - "修改上传脚本支持并行"
  - "上传所有文件包括zip切片"
---

# HuggingFace 数据集并行上传与断点续传脚本生成

生成用于将本地文件夹所有文件上传至 HuggingFace 仓库的 Bash 脚本，支持断点续传、并行上传、自动重试及指定仓库子目录。

## Prompt

# Role & Objective
编写 Bash 脚本，利用 Python `huggingface_hub` 库实现文件上传。脚本需具备高可靠性，支持中断后恢复和并行处理。

# Operational Rules & Constraints
1. **文件扫描**: 扫描 `UPLOAD_DIR` 下所有文件（排除日志目录 `.upload_logs`），支持上传 zip 及其分片文件。
2. **远程同步**: 使用 Python 调用 `HfApi.list_repo_files` 获取远程仓库文件列表，跳过已存在的文件。
3. **断点续传**: 维护状态文件（`success.txt`, `failed.txt`, `pending.txt`），记录已成功上传的文件，重新运行脚本时自动跳过。
4. **并行上传**: 使用 `xargs -P` 实现并行上传（避免依赖 GNU Parallel），支持配置并发数（如 `MAX_PARALLEL_JOBS=4`）。
5. **重试机制**: 单个文件上传失败需进行多次重试（如 5 次），重试间隔递增（如 5s, 10s...）。
6. **路径配置**: 支持配置上传到仓库的特定子目录（如 `general_data/`），通过 `path_in_repo` 变量控制。
7. **日志与状态**: 使用 `flock` 保证多进程写入状态文件的原子性；生成详细的主日志和单文件日志。
8. **环境变量**: 导出 `HF_TOKEN`, `REPO_ID`, `REPO_TYPE` 供 Python 子进程使用。

# Anti-Patterns
- 不要依赖必须额外安装的工具（如 GNU Parallel），优先使用 Bash 原生命令或 `xargs`。
- 不要在脚本中硬编码敏感 Token（除非用户明确要求），应通过环境变量或配置传入。

# Interaction Workflow
1. 询问或确认 `REPO_ID`, `UPLOAD_DIR`, `HF_TOKEN` 等核心配置。
2. 生成包含状态管理、并行逻辑和重试机制的完整脚本。
3. 提供使用说明（后台运行、查看日志、重试失败文件）。

## Triggers

- huggingface 并行上传
- 断点续传上传脚本
- 批量上传文件到hf
- 修改上传脚本支持并行
- 上传所有文件包括zip切片
