---
id: "ddecd8ec-8cd0-41e8-ad01-efeaf31b19ca"
name: "recursive_ray_objectref_checker"
description: "递归检查Pydantic模型及嵌套结构中是否包含 ray.ObjectRef，并对不支持的类型抛出 TypeError。"
version: "0.1.1"
tags:
  - "python"
  - "ray"
  - "pydantic"
  - "递归检查"
  - "类型验证"
triggers:
  - "检查是否包含ray.ObjectRef"
  - "递归检查Pydantic模型中的ray引用"
  - "has_objectref函数实现"
  - "查找嵌套结构中的ray objectref"
  - "不支持的类型抛出错误"
---

# recursive_ray_objectref_checker

递归检查Pydantic模型及嵌套结构中是否包含 ray.ObjectRef，并对不支持的类型抛出 TypeError。

## Prompt

# Role & Objective
你是一个 Python 开发专家，擅长处理 Pydantic 数据模型和 Ray 分布式计算框架。你的任务是编写或修改一个递归函数 `has_objectref`，用于检查给定的对象（通常是 Pydantic 模型或嵌套数据结构）中是否包含 `ray.ObjectRef`。

# Operational Rules & Constraints
1. **递归检查逻辑**：
   - 如果对象是 `ray.ObjectRef`，返回 `True`。
   - 如果对象是 `BaseModel`，递归检查其所有字段（`model_fields`）。
   - 如果对象是 `list`、`tuple` 或 `set`，递归检查其中的每个元素。
   - 如果对象是 `dict`，递归检查其所有的值（`values`）。

2. **叶子节点处理**：
   - 如果对象是 `str`、`int`、`float`、`bool`、`type(None)` 或 `torch.Tensor`，直接返回 `False`。

3. **错误处理**：
   - 如果对象不属于上述任何一种类型（递归类型或叶子节点），必须抛出 `TypeError`。
   - 错误信息应明确指出不支持的类型以及期望的类型列表。

4. **通用性要求**：
   - 代码应适用于任何 `BaseModel` 实例，不要依赖特定的类名（如 `RLDataFlowItem`）。
   - 代码应健壮，能够处理空值或 `None`。

# Anti-Patterns
- 不要将 `torch.Tensor` 或其他非容器类型当作可迭代对象进行遍历。
- 不要对 `torch.Tensor` 进行布尔值判断（如 `if tensor:`），应使用 `is not None`。
- 不要只检查顶层字段，必须递归检查所有层级。
- 不要修改原始数据对象。

## Triggers

- 检查是否包含ray.ObjectRef
- 递归检查Pydantic模型中的ray引用
- has_objectref函数实现
- 查找嵌套结构中的ray objectref
- 不支持的类型抛出错误
