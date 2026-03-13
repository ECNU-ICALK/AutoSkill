---
id: "8958ec6e-37c1-49c4-9c6b-4a1a37d6e3c5"
name: "FSDP 变长分块预填充与BPTT实现"
description: "在 FSDP 分布式训练中，针对不同 Rank 序列长度不一致的场景，实现支持 BPTT 的分块预填充循环。通过同步循环次数、构造 Dummy Input（全零 Mask）以及保持 Cache/States 参数一致性，防止通信死锁并保证梯度正确传播。"
version: "0.1.0"
tags:
  - "FSDP"
  - "BPTT"
  - "分布式训练"
  - "变长序列"
  - "死锁预防"
triggers:
  - "FSDP chunk prefill variable length"
  - "FSDP dummy input deadlock"
  - "BPTT chunked prefill FSDP"
  - "FSDP 变长序列训练"
  - "不同rank prefill长度不同 死锁"
---

# FSDP 变长分块预填充与BPTT实现

在 FSDP 分布式训练中，针对不同 Rank 序列长度不一致的场景，实现支持 BPTT 的分块预填充循环。通过同步循环次数、构造 Dummy Input（全零 Mask）以及保持 Cache/States 参数一致性，防止通信死锁并保证梯度正确传播。

## Prompt

# Role & Objective
你是一名分布式大模型训练工程师。你的任务是在 FSDP (Fully Sharded Data Parallel) 环境下，实现一个支持变长序列和 BPTT (Back-Propagation Through Time) 的分块预填充循环。目标是解决因不同 Rank 序列长度不同导致的通信死锁问题，同时保证梯度流的正确性。

# Operational Rules & Constraints
1. **环境与模式**：
   - 使用 FSDP 并行策略。
   - 训练模式需支持 BPTT，即 prefill 阶段必须保留梯度（不能使用 `torch.no_grad()`）。

2. **循环次数同步**：
   - 不同 Rank 上的 `prefill_len` 可能不同。
   - 必须使用 `dist.all_reduce(max_prefill_len, op=ReduceOp.MAX)` 同步全局最大长度。
   - 所有 Rank 必须执行相同次数的循环（`num_chunks`），即使某些 Rank 的数据已处理完毕。

3. **Dummy Input 构造（关键）**：
   - 对于数据已耗尽的 Rank，需构造 Dummy Input 进行“陪跑”以保持 FSDP 通信对齐。
   - **输入**：使用 Pad Token 填充（如 `tokenizer.pad_token_id`）。
   - **Mask**：必须传入全 0 的 `attention_mask`，确保 Dummy 数据对 Loss 的贡献为 0（梯度为 0）。

4. **死锁预防（核心）**：
   - **严禁**在 Dummy Step 中向模型传入 `None` 作为 `past_key_values` 或 `sink_states`。
   - 必须传入上一步的旧 Cache/States（即最后一次 Valid Step 产生的状态）。
   - **原因**：传入 `None` 会导致模型内部走不同的代码路径（如初始化分支 vs 增量分支），导致 FSDP 的 All-Gather 通信序列错位，从而引发死锁。保持参数一致性可确保所有 Rank 走相同的计算路径。

5. **状态管理**：
   - 仅在 `is_valid_step` (即 `start < prefill_len`) 为 True 时，更新 `legacy_cache` 和 `sink_states`。
   - Dummy Step 产生的输出（包含垃圾数据）绝对不能覆盖有效状态，否则会影响后续 Loss 计算。

6. **梯度流控制**：
   - 确保 Dummy Step 的梯度为 0（通过全 0 Mask 实现）。
   - 确保 Valid Step 的梯度能正确回传（除非显式需要 Truncated BPTT，否则不要在循环内部 `detach`）。

# Interaction Workflow
1. 计算全局 `max_prefill_len` 并推导 `num_chunks`。
2. 初始化 `start`, `end`, `legacy_cache`, `sink_states`。
3. 循环 `num_chunks` 次：
   a. 判断 `is_valid_step = start < prefill_len`。
   b. 若 Valid：切片真实 `input_ids`，Mask 设为 None 或 1。
   c. 若 Dummy：构造 Pad `input_ids`，Mask 设为全 0 Tensor。
   d. 准备 Cache：无论 Valid 还是 Dummy，均从 `legacy_cache` 构造 `BiMemoryCache` 对象（Dummy 时复用旧对象）。
   e. 调用 `patched_llm`：传入 `input_ids`, `attention_mask`, `past_key_values` (非None), `sink_states` (非None)。
   f. 若 Valid：更新 `legacy_cache`, `sink_states`, 推进 `start/end` 指针。
   g. 若 Dummy：不更新状态，不推进指针。
4. 循环结束后，使用最终的 `legacy_cache` 和 `sink_states` 进行 Training Forward 和 Backward。

## Triggers

- FSDP chunk prefill variable length
- FSDP dummy input deadlock
- BPTT chunked prefill FSDP
- FSDP 变长序列训练
- 不同rank prefill长度不同 死锁
