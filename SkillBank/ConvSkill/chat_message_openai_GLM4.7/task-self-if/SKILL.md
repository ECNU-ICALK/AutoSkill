---
id: "9b8995b0-0fc8-4985-83a4-f10636fee5c1"
name: "task / self / if"
description: "General SOP for common requests related to task, self, if."
version: "0.1.0"
tags:
  - "task"
  - "self"
  - "if"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# task / self / if

General SOP for common requests related to task, self, if.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) python
2) def _step_stream
3) self, memory_step: ActionStep
4) Generator[ChatMessageStreamDelta | ToolCall | ToolOutput | ActionOutput
5) Perform one step in the ReAct framework: the agent thinks, acts, and observes the result
6) Yields ChatMessageStreamDelta during the run if streaming is enabled
7) At the end, yields either None if the step is not final, or the final answer
8) memory_messages = self.write_memory_to_messages
9) input_messages = memory_messages.copy
10) Add new step in logs

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
