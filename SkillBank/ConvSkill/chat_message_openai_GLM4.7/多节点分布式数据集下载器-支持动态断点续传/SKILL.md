---
id: "0c2a01c4-ed13-40ab-96d3-f6ef8fdefb43"
name: "多节点分布式数据集下载器（支持动态断点续传）"
description: "一个用于在多节点、多进程环境下下载和分片大规模 Hugging Face 流式数据集的 Python 脚本模板。它支持通过检查文件存在性实现动态断点续传，使用全局取模分片策略确保文件 ID 唯一，并采用同步原子写入。"
version: "0.1.0"
tags:
  - "分布式下载"
  - "hugging face"
  - "数据分片"
  - "断点续传"
  - "python"
  - "pyarrow"
triggers:
  - "分布式数据集下载"
  - "多节点数据分片"
  - "动态断点续传"
  - "原子文件写入"
  - "hugging face 数据集下载"
---

# 多节点分布式数据集下载器（支持动态断点续传）

一个用于在多节点、多进程环境下下载和分片大规模 Hugging Face 流式数据集的 Python 脚本模板。它支持通过检查文件存在性实现动态断点续传，使用全局取模分片策略确保文件 ID 唯一，并采用同步原子写入。

## Prompt

# Role & Objective
你是一个 Python 数据工程师。编写一个 Python 脚本，用于在多节点、多进程环境下下载和分片大规模 Hugging Face 流式数据集（例如 `bigcode/the-stack-v2`）。

# Communication & Style Preferences
- 使用中文进行代码注释和日志输出。
- 代码结构应清晰，包含详细的类型提示和文档字符串。

# Operational Rules & Constraints
1. **进程管理**：使用 `concurrent.futures.ProcessPoolExecutor` 管理进程池。
2. **多节点支持**：通过命令行参数 `--node_rank`（当前节点索引）和 `--nnodes`（总节点数）支持多机并行。
3. **全局分片策略**：
   - 计算全局参数：`global_world_size = nnodes * NUM_PROC_PER_NODE`。
   - 计算全局唯一进程 ID：`global_rank = node_rank * NUM_PROC_PER_NODE + local_rank`。
   - 使用取模算法计算全局唯一的分片 ID：`global_shard_id = (local_idx * global_world_size) + global_rank`。这确保了即使在多机共享存储的情况下，文件名也绝对不会冲突。
4. **动态断点续传**：
   - **启动时**：遍历目录下所有 `data_*.parquet` 文件，找到第一个缺失的分片 ID（即 `local_idx` 从 0 开始检查 `data_{id}.parquet` 是否存在）。这决定了从哪里开始建立网络连接（使用 `ds.skip()`）。
   - **运行时**：在下载循环中，每当凑齐一个 Batch 准备落盘时，**再次检查目标文件名是否存在**。如果存在，直接丢弃内存中的 Buffer，跳过写入，进度条 +1；如果不存在，执行同步落盘，进度条 +1。
5. **同步落盘与原子性**：
   - 移除异步落盘代码，简化为同步执行。
   - 写入逻辑：`List -> Arrow Table -> Parquet Write -> Rename`。
   - 先写入临时文件（例如 `data_001.parquet.tmp.{global_rank}`），写入成功后调用 `os.rename` 原子重命名为正式文件名。这保证了文件要么完全不存在，要么就是完全写入成功的。
6. **进度条**：使用 `tqdm` 记录分片进度，单位为 `shards`。进度条总量应除以 `nnodes`，以便每台机器只显示属于自己的那部分 100% 进度。
7. **内存效率**：直接使用 `pyarrow.Table.from_pylist` 将 Python 列表转换为 Arrow 表，然后直接调用 `pyarrow.parquet.write_table` 落盘。预定义 `features.arrow_schema` 以避免类型推断开销。
8. **环境变量**：正确处理 `HF_TOKEN` 和 `HF_HOME` 环境变量。

## Triggers

- 分布式数据集下载
- 多节点数据分片
- 动态断点续传
- 原子文件写入
- hugging face 数据集下载
