---
id: "0d2691ca-3271-4ec6-9c28-6fdf75f097eb"
name: "write-accessible-ai-explainer-for-public"
description: "Generates clear, non-technical explanations of AI concepts for general audiences, prioritizing real-world relevance, avoiding jargon and hallucination, and anchoring claims in observable use cases."
version: "0.1.0"
tags:
  - "ai-literacy"
  - "public-communication"
  - "anti-hallucination"
  - "explanation-design"
  - "chinese-audience"
triggers:
  - "写一篇面向大众的AI科普文章"
  - "用大白话解释XX技术"
  - "公众号文章：讲清楚XX是什么"
  - "避免术语，讲给老人孩子也能懂"
  - "技术前沿但表达要接地气"
---

# write-accessible-ai-explainer-for-public

Generates clear, non-technical explanations of AI concepts for general audiences, prioritizing real-world relevance, avoiding jargon and hallucination, and anchoring claims in observable use cases.

## Prompt

# Goal
Explain an AI/ML concept (e.g., quantization, fine-tuning, RAG,幻觉 mitigation) to a non-technical public audience via a WeChat Official Account article — using only plain language, concrete analogies, verified real-world examples, and zero speculative or exaggerated claims.

# Constraints & Style
- Language: Modern standard Chinese; no English terms without immediate plain-Chinese explanation (e.g., '量化' → '数字表示方式的转换', not 'int8');
- Tone: Calm, grounded, trustworthy — like a knowledgeable civil servant explaining policy to neighbors;
- Structure: Start with relatable user experiences (not definitions); explicitly name and debunk common misconceptions early;
- No hallucination: Never invent tools, companies, benchmarks, or unverified outcomes (e.g., no 'X company achieved 99.2% accuracy'; instead: 'some education apps report faster startup and lower memory use after optimization');
- No markdown, no bold/italic/emoji — pure copy-paste-ready text for WeChat editor;
- Anchor every technical point in tangible impact: speed, cost, privacy, reliability, or accessibility — e.g., 'enables offline use on rural tablets', 'reduces app startup from 8s to 1.2s', 'keeps health queries on-device'.

# Workflow
1. Identify the core concept and its *observable effect* on end users (not internal mechanics);
2. Name one widespread misconception — then refute it with a concrete, verifiable contrast;
3. Explain *why* the technique exists — tie directly to real constraints (power, cost, latency, data sovereignty);
4. Describe how it’s applied — not as math, but as intentional trade-off engineering ('keep precision where it matters, compress where error is harmless');
5. Close with 2–3 specific, anonymized examples of where it’s already in use — all drawn from publicly documented deployments or vendor-confirmed case studies (no hypotheticals).

## Triggers

- 写一篇面向大众的AI科普文章
- 用大白话解释XX技术
- 公众号文章：讲清楚XX是什么
- 避免术语，讲给老人孩子也能懂
- 技术前沿但表达要接地气
