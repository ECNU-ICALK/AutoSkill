---
id: "4d858906-a138-4403-8f74-b37a4f2677e7"
name: "Standard release process"
description: "General SOP for common requests related to self, if, batch_size."
version: "0.1.1"
tags:
  - "self"
  - "if"
  - "batch_size"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# Standard release process

General SOP for common requests related to self, if, batch_size.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):

1. 统一 sampling_params（计算 max_remaining_tokens）
2. 引入 loss_mask 区分 Hint（0）和生成内容（1）
3. Token ID + String Suffix 双重停止检测
4. 完整的 DataProto 构建
5. Control Stream: Policy generates without guidance
6. idx_list
7. for i in range(batch_size)
8. idx_list.append(_pre_process_inputs(self.pad_token_id, idx[i]))
9. do_sample = prompts.meta_info.get("do_sample", True)
10. is_validate = prompts.meta_info.get("validate", False)

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
