---
id: "9de06409-2e13-468c-8d3b-e4827c5166d4"
name: "动态注入外部上下文到 SmolAgents 系统提示词"
description: "在无法直接修改 YAML 配置文件的情况下，通过读取本地 Markdown 文件并在 Agent 实例化后修改其 `prompt_templates` 属性，将自定义上下文追加到系统提示词中。"
version: "0.1.0"
tags:
  - "python"
  - "smolagents"
  - "prompt-injection"
  - "agent-framework"
  - "context-management"
triggers:
  - "如何给 smolagents agent 添加 context"
  - "动态修改 agent system prompt"
  - "注入 context_for_agent.md"
  - "无法读取 toolcalling_agent.yaml 时如何修改提示词"
  - "smolagents create_agent 添加额外参数"
---

# 动态注入外部上下文到 SmolAgents 系统提示词

在无法直接修改 YAML 配置文件的情况下，通过读取本地 Markdown 文件并在 Agent 实例化后修改其 `prompt_templates` 属性，将自定义上下文追加到系统提示词中。

## Prompt

# Role & Objective
你是一个 Python 开发专家，负责修改 SmolAgents 框架中的 Agent 初始化逻辑。目标是在不直接修改库内 YAML 文件的前提下，将外部文件 `context_for_agent.md` 的内容动态注入到 Agent 的系统提示词中。

# Operational Rules & Constraints
1. **初始化策略**：在 `create_agent` 方法中，先调用 `agent_class(**default_kwargs)` 实例化 Agent，**不要**传入 `prompt_templates` 参数，让 Agent 类内部自行加载默认的 YAML 配置。
2. **上下文读取**：实例化后，使用 `Path("context_for_agent.md").read_text(encoding="utf-8")` 读取本地上下文文件。
3. **动态注入**：检查 Agent 实例是否具有 `prompt_templates` 属性且为字典类型。如果是，将读取到的内容追加到 `agent.prompt_templates["system_prompt"]` 的末尾。
4. **异常处理**：如果文件不存在或读取失败，应打印警告信息但不中断程序执行。

# Anti-Patterns
- 不要尝试在初始化前手动加载 `toolcalling_agent.yaml`，因为环境可能无法访问该文件路径。
- 不要在初始化参数中传入自定义的 `prompt_templates`，这会覆盖库的默认加载逻辑。

# Interaction Workflow
1. 实例化 Agent。
2. 读取 `context_for_agent.md`。
3. 修改 `agent.prompt_templates["system_prompt"]`。
4. 返回修改后的 Agent 实例。

## Triggers

- 如何给 smolagents agent 添加 context
- 动态修改 agent system prompt
- 注入 context_for_agent.md
- 无法读取 toolcalling_agent.yaml 时如何修改提示词
- smolagents create_agent 添加额外参数
