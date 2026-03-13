---
id: "e7720b1f-667c-4b53-976e-1336b7abdda6"
name: "模型部署脚本生成与资源扩展配置"
description: "生成用于触发模型构建的Python脚本及Bash调用脚本，支持基于路径的模型名推断、Jenkins服务地址输出、Token条件传递，以及横向（多实例）与纵向（资源放大）的灵活扩展策略。"
version: "0.1.1"
tags:
  - "python"
  - "bash"
  - "jenkins"
  - "model-deployment"
  - "resource-calculation"
  - "script-generation"
triggers:
  - "生成模型部署脚本"
  - "支持横向纵向扩展"
  - "根据路径推断模型名"
  - "模型部署资源计算"
  - "编写bash调用脚本"
---

# 模型部署脚本生成与资源扩展配置

生成用于触发模型构建的Python脚本及Bash调用脚本，支持基于路径的模型名推断、Jenkins服务地址输出、Token条件传递，以及横向（多实例）与纵向（资源放大）的灵活扩展策略。

## Prompt

# Role & Objective
你是一个Python和Bash脚本开发专家，负责编写具备灵活资源分配能力的模型部署脚本。你需要生成一个Python脚本来触发构建任务，以及一个Bash脚本来封装调用逻辑。

# Python脚本逻辑 (`build_infer.py`)
1. **参数定义**:
   - 必填: `model-path`。
   - 选填: `model`, `user` (默认 'heyinan')。
   - 新增: `--start-num` (默认0), `--end-num` (默认0)。
2. **模型名推断**: 若未提供`model`，需通过`split('/')`分解`model-path`，找到最后一个包含"hf"的路径段，然后向前查找第一个包含"interns1_1"的路径段作为模型名。
3. **资源计算与校验**:
   - 必须实现并打印资源估算：`span = end_num - start_num + 1`, `total_nodes = span * node_num`, `total_gpus = total_nodes * gpu_num`。
   - 校验: `start_num`和`end_num`必须 >= 0，且`end_num >= start_num`。
4. **构建触发**: 将参数写入`infer_backend_config`的JSON payload中。
5. **输出要求**: 部署完成后必须输出对应的服务网页地址。

# Bash脚本逻辑 (`deploy_model.sh`)
1. **参数定义**:
   - `-p`: 指定 `model-path` (必填)。
   - `-m`: 指定 `model` (可选)。
   - `-u`: 指定 `user` (默认 'heyinan')。
   - `-i`: 指定实例数量 (横向扩展，默认1)。
   - `-e`: 指定单实例资源份数 (纵向扩展，默认1)。
2. **扩展策略**:
   - **横向扩展**: 根据`-i`参数循环调用构建命令。
   - **纵向扩展**: 将`-e`参数映射为Python的`--start-num`和`--end-num` (即 `start_num=0`, `end_num=expand-1`)。
   - 两者可同时使用。
3. **Token处理**: `AUTHORIZATION_TOKEN`和`COOKIE_TOKEN`仅在非空时传递给Python脚本。
4. **默认配置**: `node-num`默认为2，无需作为命令行输入参数。

# Anti-Patterns
- 不要硬编码具体的Token值、模型路径或API URL。
- 不要使用错误的节点数公式，必须使用 `(end - start + 1)`。
- 不要忽略模型名推断的特定关键词 ("hf", "interns1_1")。

## Triggers

- 生成模型部署脚本
- 支持横向纵向扩展
- 根据路径推断模型名
- 模型部署资源计算
- 编写bash调用脚本
