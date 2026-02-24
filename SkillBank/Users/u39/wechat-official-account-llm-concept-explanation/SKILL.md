---
id: "1c133c80-65d2-4494-8dc8-d7a6be69b808"
name: "wechat-official-account-llm-concept-explanation"
description: "A reusable skill for authoring WeChat Official Account articles that explain core LLM concepts (e.g., quantization, continual learning) to non-technical audiences—using plain conversational Chinese, concrete analogies, verifiable public sources, and strict avoidance of jargon, formulas, or decorative symbols."
version: "0.1.1"
tags:
  - "wechat"
  - "llm"
  - "public-science-communication"
  - "china-ai-deployment"
  - "china-ai-policy"
triggers:
  - "写一篇公众号解释大模型核心概念"
  - "用大白话讲清楚LLM关键技术"
  - "面向大众的LLM科普"
  - "微信公众号AI技术普及"
  - "怎么向非技术人员说明大模型能力边界"
---

# wechat-official-account-llm-concept-explanation

A reusable skill for authoring WeChat Official Account articles that explain core LLM concepts (e.g., quantization, continual learning) to non-technical audiences—using plain conversational Chinese, concrete analogies, verifiable public sources, and strict avoidance of jargon, formulas, or decorative symbols.

## Prompt

# Goal
Generate a WeChat Official Account (WxOA) article that explains a core LLM concept (e.g., quantization, continual learning) to general readers—no prior AI knowledge required—using only concrete analogies, real-world examples, and claims traceable to publicly available, authoritative sources.

# Constraints & Style
- Language: Plain, conversational Simplified Chinese; zero technical terms without immediate analogy (e.g., never say 'int4' or 'continual learning' alone—always pair with a physical or everyday comparison);
- Structure: Five-part flow — (1) relatable pain point or misconception, (2) simple core idea (with one consistent, scalable analogy), (3) tangible benefits or practical implications, (4) myth-busting (exactly three widespread misconceptions, each paired with an evidence-backed correction), (5) current China-relevant status (only officially released models, shipped products, or published policies—no 'in development' or speculation);
- No hallucination: Every technical or capability claim must be traceable to at least one publicly available source — e.g., Hugging Face model cards, official whitepapers (Qwen, GLM), MLPerf results, national regulations (Interim Measures for the Management of Generative AI Services), or disclosed product specs;
- Formatting: No markdown, no bold/italic/color, no emoji, no arrows (→), no decorative dividers (▍, ✅, ❌), no custom bullets — rely solely on line breaks, plain ASCII section headers (e.g., '### Why can’t your AI learn new terms mid-conversation?'), and sentence rhythm for emphasis;
- End with an authentic, low-barrier WeChat-style engagement hook — neutral, open-ended, and audience-focused (e.g., 'Which AI feature on your phone felt fastest? Tell us below.' or 'What’s a term you wish your AI understood better? Share below.');
- All numbers and capabilities must be cited to real benchmarks, shipped versions, or official documentation (e.g., 'Qwen2-7B-Int4 runs on Huawei Kirin 9000S' not 'quantized models run faster').

## Triggers

- 写一篇公众号解释大模型核心概念
- 用大白话讲清楚LLM关键技术
- 面向大众的LLM科普
- 微信公众号AI技术普及
- 怎么向非技术人员说明大模型能力边界
