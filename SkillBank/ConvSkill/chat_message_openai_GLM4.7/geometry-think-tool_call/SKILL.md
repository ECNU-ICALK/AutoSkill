---
id: "86442c3f-bbd8-4f37-98d0-a560b1051382"
name: "geometry / think / tool_call"
description: "General SOP for common requests related to geometry, think, tool_call."
version: "0.1.0"
tags:
  - "geometry"
  - "think"
  - "tool_call"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# geometry / think / tool_call

General SOP for common requests related to geometry, think, tool_call.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: 381d0397-c5bd-4bd4-b5b3-c9c07a23a140.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) ```python
8) USER_PROMPT_zn = r"""你是一名精通平面几何的资深解题专家。你的任务是基于给定的几何图像与题目描述，进行严谨且连贯的几何推理，并给出详尽的解题步骤与结论。你应当模拟人类解题思维：深入分析已知条件、审慎构造辅助线、敏锐捕捉几何关联，最终给出准确回答或严密证明。
9) 在解题过程中，你可以调用“几何画板”进行辅助线构造。画板通过名为 `geometry` 的对象提供函数接口。你只能通过调用这些标准接口操作图形，无法直接修改图像，也无法看到图像对应的底层数据。
10) 解题过程中，你需要严格遵守以下“思考-行动-反馈”的循环模式：

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
