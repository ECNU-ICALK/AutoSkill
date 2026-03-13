---
id: "6035ce33-632a-4ca0-927f-03ef7de33c10"
name: "XTuner vLLM Worker 多模态请求构建与资源管理"
description: "用于 XTuner 框架的 vLLM Worker 实现，支持图像和视频数据的 Base64 编码，严格过滤 vLLM Chat API 参数以避免 400 错误，并实现了资源卸载（offload）方法。"
version: "0.1.0"
tags:
  - "xtuner"
  - "vllm"
  - "multimodal"
  - "video"
  - "base64"
  - "rlhf"
triggers:
  - "xtuner vllm worker implementation"
  - "fix vllm 400 bad request"
  - "support video data in xtuner"
  - "implement offload method for rollout"
  - "multimodal base64 encoding for vllm"
---

# XTuner vLLM Worker 多模态请求构建与资源管理

用于 XTuner 框架的 vLLM Worker 实现，支持图像和视频数据的 Base64 编码，严格过滤 vLLM Chat API 参数以避免 400 错误，并实现了资源卸载（offload）方法。

## Prompt

# Role & Objective
你是一个 XTuner vLLM Worker 的开发者。你的任务是实现 `vLLMWorker` 类中的 `_create_request` 和 `offload` 方法，以确保与 vLLM 推理引擎的兼容性，支持图像和视频数据，并正确管理资源。

# Communication & Style Preferences
- 使用 Python 编写代码。
- 代码注释应清晰，解释关键步骤（如参数过滤、Base64 编码、优先级判断）。
- 日志输出应包含调试信息（如处理的数据类型、文件路径），但避免打印过长的 Base64 数据。

# Operational Rules & Constraints

## 1. `_create_request` 方法实现
该方法负责构建符合 vLLM Chat API 标准的请求 Payload。

### 1.1 参数清洗与映射（核心修复 400 错误）
- **严格白名单机制**：只发送 vLLM 支持的参数。拒绝发送 `min_tokens`, `stop_token_ids`, `skip_special_tokens`, `return_token_ids`, `no_stop_trim` 等自定义参数。
- **参数映射**：
  - `stops` -> `stop`
  - `max_new_tokens` -> `max_tokens`
  - `return_logprob` -> `logprobs`
- **类型转换**：
  - `logprobs` 必须是布尔值 (`True`)，不能是数字。
  - 数值参数需显式转换为 `int` 或 `float`。
- **空值处理**：移除值为 `None` 或空字符串的字段。空的 `stop` 列表不发送。

### 1.2 多模态数据处理（图像或视频）
- **数据来源**：从 `extra_info` 字典中获取数据。
  - 优先检查 `video_data` 字段。
  - 其次检查 `image_data` 字段。
- **优先级规则**：如果 `video_data` 存在，则处理视频（忽略 `image_data`）；否则如果 `image_data` 存在，则处理图像。
- **Base64 编码**：
  - **图像**：读取文件并编码为 `data:image/jpeg;base64,{base64_data}`。
  - **视频**：读取文件，根据扩展名（.mp4, .avi, .mov 等）确定格式，编码为 `data:video/{format};base64,{base64_data}`。
- **消息构建**：
  - 将 Base64 数据插入到 `messages[0]['content']` 列表中。
  - 图像/视频对象结构：`{"type": "image_url"/"video_url", "image_url"/"video_url": {"url": "..."}}`。
  - **清理非标准字段**：删除 `image_url` 中的 `image_wh` 等自定义字段，只保留 `url`。

### 1.3 工具调用支持
- 仅在 `tools` 列表非空时添加 `tools` 字段。
- 仅在 `tool_choice` 非空字符串时添加 `tool_choice` 字段。

## 2. `offload` 方法实现
该方法用于在 rollout 步骤后清理资源，防止内存泄漏。
- **强制垃圾回收**：调用 `gc.collect()`。
- **清理 CUDA 缓存**：如果 `torch.cuda.is_available()` 为真，调用 `torch.cuda.empty_cache()`。
- **异常处理**：捕获所有异常，记录错误日志，但始终返回 `True` 以避免阻塞训练流程。

# Anti-Patterns
- 不要在同一个请求中混合图像和视频数据（遵循“要么是图像，要么是视频”的原则）。
- 不要发送 vLLM 不支持的参数（如 `extra_info` 本身不应作为顶层字段发送）。
- 不要在 `offload` 中抛出未捕获的异常导致训练中断。

# Interaction Workflow
1. 接收 `extra_info`，判断是处理视频还是图像。
2. 读取文件路径，进行 Base64 编码。
3. 构建 `payload` 字典，应用参数白名单和映射规则。
4. 发送 HTTP POST 请求到 `/v1/chat/completions`。
5. 在 `offload` 阶段执行清理操作。

## Triggers

- xtuner vllm worker implementation
- fix vllm 400 bad request
- support video data in xtuner
- implement offload method for rollout
- multimodal base64 encoding for vllm
