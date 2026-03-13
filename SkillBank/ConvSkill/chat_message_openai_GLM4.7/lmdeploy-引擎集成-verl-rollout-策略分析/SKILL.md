---
id: "1a456189-f353-4bd5-9ffb-dd4417617b53"
name: "LMDeploy 引擎集成 VERL Rollout 策略分析"
description: "分析 vLLM 的 SPMD 模式与 LMDeploy 的 API Server 模式的架构差异，制定将 LMDeploy 集成到 VERL Rollout 系统的策略。重点涵盖执行频率差异、Rank 映射（DP 到实例）策略以及 Locality 约束（同节点更新）。"
version: "0.1.0"
tags:
  - "verl"
  - "lmdeploy"
  - "distributed training"
  - "rollout"
  - "inference engine"
  - "spmd"
  - "api server"
triggers:
  - "lmdeploy 集成 verl"
  - "verl rollout 适配"
  - "vllm external_launcher 对比"
  - "分布式推理引擎集成"
  - "rank 映射策略"
  - "权重更新机制"
---

# LMDeploy 引擎集成 VERL Rollout 策略分析

分析 vLLM 的 SPMD 模式与 LMDeploy 的 API Server 模式的架构差异，制定将 LMDeploy 集成到 VERL Rollout 系统的策略。重点涵盖执行频率差异、Rank 映射（DP 到实例）策略以及 Locality 约束（同节点更新）。

## Prompt

解释如何将 LMDeploy 集成到 VERL 中，重点对比 vLLM 的 `external_launcher` SPMD 模式与 LMDeploy 的 API Server 模式，并给出 Rank 映射和权重更新的具体实现方案。

## Triggers

- lmdeploy 集成 verl
- verl rollout 适配
- vllm external_launcher 对比
- 分布式推理引擎集成
- rank 映射策略
- 权重更新机制
