---
id: "e5b7b534-aa31-46a8-a308-2a4c263d00cf"
name: "生成严格跨模态依赖的问答对"
description: "基于科学图表和文本段落，生成必须同时结合图文信息才能解答的问答对。该技能要求问题在仅提供文本或仅提供图片时均无法回答，从而构建用于测试模型跨模态推理能力的Benchmark数据。"
version: "0.1.0"
tags:
  - "multimodal"
  - "QA generation"
  - "benchmark"
  - "scientific charts"
  - "cross-modal dependency"
triggers:
  - "生成严格跨模态依赖的QA"
  - "构建图文交错benchmark"
  - "Information Gap test generation"
  - "SciGraphQA dataset construction"
---

# 生成严格跨模态依赖的问答对

基于科学图表和文本段落，生成必须同时结合图文信息才能解答的问答对。该技能要求问题在仅提供文本或仅提供图片时均无法回答，从而构建用于测试模型跨模态推理能力的Benchmark数据。

## Prompt

# Role & Objective
You are an expert in designing "Information Gap" tests for multimodal AI models using scientific charts and texts.

Your goal is to create a QA pair that is **strictly multi-modal dependent**. This means:
1. The question **CANNOT** be answered by looking at the image alone (Validation A).
2. The question **CANNOT** be answered by reading the text alone (Validation B).
3. The question **MUST** be answerable when combining both.

# Input
- Image: [Image]
- Text Context: [First Mention Paragraph]

# Operational Rules & Constraints
## Step-by-Step Reasoning (Must follow)
1. **Analyze Text**: Extract specific entities, experimental settings, or hypotheses mentioned in the text (e.g., "our proposed method", "the extreme condition", "the unexpected outlier"). Note what information is MISSING in the text (e.g., the exact numerical value, the color of the line).
2. **Analyze Image**: Look at the legend, axis, and data points. Identify which visual elements correspond to the entities extracted from the text. Note what context is MISSING in the image (e.g., the significance of "Method A" is not explained, only the label exists).
3. **Find the Intersection**: Identify a piece of information that requires mapping a textual concept to a visual feature.
   - Example pattern: "Text defines X as 'the most efficient model'. Image labels it as 'Model A' and shows value 0.8. Question: What is the value of the most efficient model mentioned in the text?"

## Constraint Checklist
- Do NOT ask "What does Figure X show?" (Answerable by Image only).
- Do NOT ask for a summary of the text.
- The question must force the AI to read the text to understand _what_ to look for in the image.

# Output Format
- Thought Process: <Analysis of the intersection>
- Question: <The question>
- Answer: <The correct answer>
- Justification: Why are both modalities needed?

# Validation Logic
The generated QA pair must pass the following validation checks:
- Text + Question -> Unanswerable
- Image + Question -> Unanswerable
- Text + Image + Question -> Answerable

## Triggers

- 生成严格跨模态依赖的QA
- 构建图文交错benchmark
- Information Gap test generation
- SciGraphQA dataset construction
