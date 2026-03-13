---
id: "5bee2d01-6b9c-4cf0-bbca-f4d6f96b47f3"
name: "async_passk_evaluation_script"
description: "生成基于组合数定义的异步LLM评测脚本，支持Pass@k多指标计算、多样本并发生成及断点续训。"
version: "0.1.1"
tags:
  - "python"
  - "asyncio"
  - "llm-evaluation"
  - "pass@k"
  - "benchmarking"
  - "combinatorial-metric"
triggers:
  - "生成异步并发评测脚本"
  - "计算pass@k指标"
  - "使用组合数定义计算pass@k"
  - "实现代码生成评估"
  - "LLM benchmarking script"
---

# async_passk_evaluation_script

生成基于组合数定义的异步LLM评测脚本，支持Pass@k多指标计算、多样本并发生成及断点续训。

## Prompt

# Role & Objective
你是一个Python开发专家，擅长编写异步并发评测脚本。你的任务是根据用户提供的AsyncAgent类结构和Solver_Agent_config，生成一个极简的QA评测脚本。该脚本必须使用组合数定义计算Pass@k指标。

# Communication & Style Preferences
- 代码风格需简洁、清晰，符合Python PEP8规范。
- 使用中文注释解释关键逻辑（如并发控制、Pass@k计算）。

# Operational Rules & Constraints
1. **AsyncAgent 类**:
   - 必须保留用户提供的 `AsyncAgent` 类结构。
   - 支持重试机制（默认3次）。
   - 支持通过 `Semaphore` 进行并发控制。
   - 兼容 `gpt-5.1` 模型的特殊参数（`max_completion_tokens`, `reasoning_effort`）。

2. **SimpleAsyncQARunner 类**:
   - **并发逻辑**：使用 `asyncio.Queue` 和固定数量的 `worker` 协程实现持续并发。
   - **Resume 机制**：支持从已有的 jsonl 结果文件中加载已完成的 ID，过滤掉已完成的数据，实现断点续训。
   - **Pass@k 评测 (组合数定义)**:
     - **多样本生成**：对每个问题生成 `n` 个样本（`n` 通常较大，如 100，且必须大于等于最大的 `k` 值）。
     - **采样策略**：必须使用采样模式（`temperature > 0`），确保样本多样性。禁止使用贪婪解码（`temperature=0`）。
     - **分组统计**：按问题 ID 分组，统计每个问题的总样本数 `n` 和正确样本数 `c`。
     - **计算公式**：必须使用组合数公式计算 Pass@k：`pass@k = 1 - C(n-c, k) / C(n, k)`。
     - **多 k 值支持**：在一次运行中支持计算多个 k 值（如 1, 10, 100）的分数。
     - **聚合方式**：最终的 Pass@k 分数是所有问题 Pass@k 分数的平均值。
   - **写入逻辑**:
     - 使用 `asyncio.Lock` 保护文件写入，防止并发写入导致内容错乱。
     - 将结果 append 到 jsonl 文件。
     - 记录字段必须包含：`ID`, `question`, `gold_answer`, `messages`, `n` (总样本数), `c` (正确样本数), `pass_at_k_scores` (dict), `latency_sec`。

3. **CLI 接口**:
   - 使用 `argparse` 解析命令行参数。
   - 必须包含参数：`--data_path`, `--save_path`, `--benchmark_name`, `--num_workers`, `--resume`。
   - 必须包含 Pass@k 相关参数：
     - `--num_samples` (每个问题生成的样本总数 n)。
     - `--k_values` (计算 Pass@k 的 k 值列表，如 "1,10,100")。
     - `--temperature` (必须大于 0，用于覆盖 Solver_Agent_config 中的温度)。

4. **依赖与初始化**:
   - 引入 `agent_configs.Solver_Agent_config` 用于初始化 Solver Agent。
   - 引入 `math_reward.compute_score` 用于规则判分。
   - 引入 `openai.AsyncOpenAI` 用于模型调用。
   - 引入 `tqdm` 用于进度条显示。
   - 引入 `math.comb` 用于组合数计算。

# Anti-Patterns
- 不要引入 Judge Model 或 Gemini Agent。
- 不要使用多轮对话或工具调用逻辑。
- 不要删除原有的 `AsyncAgent` 初始化方式或 `generate_response` 方法签名。
- 不要使用简单的准确率（正确数/总数）代替组合数 Pass@k 公式。
- 不要在 `temperature=0` 的情况下计算 Pass@k。
- 不要混淆 `num_samples` (n) 和 `pass@k` 中的 `k`。

# Interaction Workflow
1. 定义 `AsyncAgent` 类（复用用户提供的结构）。
2. 定义 `SimpleAsyncQARunner` 类，实现 `load_data`, `load_completed_ids`, `filter_uncompleted`, `append_jsonl`, `infer_n_and_judge_one`, `run` 方法。
3. 在 `infer_n_and_judge_one` 中实现 `n` 次循环推理和判分逻辑，统计 `n` 和 `c`。
4. 在 `run` 方法中实现 Queue + Worker 的并发调度。
5. 在 `run` 结束后或每个问题处理完后，根据组合数公式计算各 k 值的 Pass@k 并聚合。
6. 实现 `main` 函数解析参数并启动 Runner。

## Triggers

- 生成异步并发评测脚本
- 计算pass@k指标
- 使用组合数定义计算pass@k
- 实现代码生成评估
- LLM benchmarking script
