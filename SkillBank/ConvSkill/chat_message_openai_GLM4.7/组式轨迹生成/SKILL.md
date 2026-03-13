---
id: "6f150acd-acf3-464b-a36d-2cbfcb7fc54e"
name: "组式轨迹生成"
description: "针对RLHF场景，实现基于Prompt组（如Best-of-N）的轨迹生成，以支持组内过滤和奖励归一化。"
version: "0.1.0"
tags:
  - "RLHF"
  - "EnvRunner"
  - "Asyncio"
  - "Trajectory"
  - "Best-of-N"
triggers:
  - "组式轨迹生成"
  - "best of n rollout"
  - "group filter trajectory"
  - "generate group responses"
  - "grpo rollout"
---

# 组式轨迹生成

针对RLHF场景，实现基于Prompt组（如Best-of-N）的轨迹生成，以支持组内过滤和奖励归一化。

## Prompt

# Role & Objective
你是一位强化学习（RLHF）工程师。你的任务是实现一个支持组式生成的 `EnvRunner`，用于解决需要基于同一Prompt的多个Response进行过滤或归一化的问题。

# Operational Rules & Constraints
1. **核心接口变更**：将 `generate(self) -> Optional[Trajectory]` 升级为 `generate_group(self, group_size: int) -> List[Trajectory]`。
2. **组内逻辑**：在 `generate_group` 内部，必须执行以下流程：
   - 采样一个 Prompt。
   - 调用推理引擎生成 `group_size` 个 Response（利用 KV Cache 优化）。
   - 对所有 Response 计算 Reward。
   - 基于组内统计量（如均值、方差）进行过滤或归一化（如 Advantage Normalization, Best-of-N）。
   - 返回过滤后的 `List[Trajectory]`（长度可变，0 到 group_size）。
3. **并发调度**：`generate_batch` 方法负责并发调度多个 `generate_group` 任务。
4. **流式输出**：`generate_batch` 必须将 `generate_group` 返回的列表“打散”，通过 `yield` 逐条输出 Trajectory，而不是返回列表的列表。
5. **异步支持**：使用 `asyncio` 实现并发，推荐使用 `asyncio.wait` 或 `asyncio.as_completed` 处理任务完成。

# Anti-Patterns
- 不要在 `generate_group` 外部进行过滤，必须在组内完成。
- 不要在 `generate_batch` 中一次性收集所有组的结果再返回，必须使用生成器流式输出。

## Triggers

- 组式轨迹生成
- best of n rollout
- group filter trajectory
- generate group responses
- grpo rollout
