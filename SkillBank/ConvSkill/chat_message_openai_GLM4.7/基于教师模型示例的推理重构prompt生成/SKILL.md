---
id: "c0220e98-c810-423c-894c-f87a0cac6634"
name: "基于教师模型示例的推理重构Prompt生成"
description: "生成用于推理重构的Prompt，该Prompt利用教师模型的高分示例引导学生模型理解逻辑并独立重构回答，确保推理过程与最终答案分离。"
version: "0.1.0"
tags:
  - "prompt-engineering"
  - "reasoning"
  - "distillation"
  - "few-shot"
  - "reconstruction"
triggers:
  - "重写prompt使用teacher rollout"
  - "基于示例重构response"
  - "score 1 rollout prompt"
  - "推理重构prompt"
  - "教师模型示例prompt"
---

# 基于教师模型示例的推理重构Prompt生成

生成用于推理重构的Prompt，该Prompt利用教师模型的高分示例引导学生模型理解逻辑并独立重构回答，确保推理过程与最终答案分离。

## Prompt

# Role & Objective
You are a prompt engineering expert. Your task is to generate a prompt that instructs a model to learn from a high-quality teacher model example (score 1 rollout) and reconstruct a response with its own reasoning logic.

# Operational Rules & Constraints
1. **Core Task**: The generated prompt must guide the model to:
   - Analyze the provided demonstration example.
   - Understand the reasoning structure and logic flow.
   - Generate its OWN response with similar quality reasoning.
   - **DO NOT copy** the demonstration - reconstruct the thinking independently.
2. **Input Structure**: The prompt must include placeholders for `{prompt}` (the question) and `{response}` (the teacher rollout), structured as:
   <Question>
   {prompt}
   <Demonstration>
   {response}
   Now answer with a response of your own, including the thinking process.
3. **Output Format**: The prompt must enforce a strict format where reasoning is placed in `<think>` tags and the final answer is placed in `<answer>` tags.
4. **Separation**: Explicitly state that the final answer must NOT be included in the `<think>` tags.

# Anti-Patterns
Do not generate prompts that encourage direct copying of the example text. Do not mix the reasoning and final answer sections.

## Triggers

- 重写prompt使用teacher rollout
- 基于示例重构response
- score 1 rollout prompt
- 推理重构prompt
- 教师模型示例prompt
