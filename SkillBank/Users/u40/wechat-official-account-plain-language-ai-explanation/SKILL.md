---
id: "39196e11-8b57-47d7-881c-c1b4c8c02d41"
name: "wechat-official-account-plain-language-ai-explanation"
description: "A reusable skill for drafting WeChat Official Account articles that explain AI technologies using relatable, everyday-life narratives — prioritizing clarity over jargon, grounding technical concepts in concrete human experiences, and maintaining strict adherence to real-world 2024 technical facts without invention."
version: "0.1.0"
tags:
  - "wechat"
  - "ai-explanation"
  - "plain-language"
  - "narrative-writing"
  - "tech-communication"
triggers:
  - "写公众号文章"
  - "AI科普文"
  - "用生活故事讲技术"
  - "微信公众号排版"
  - "不用符号的科普文"
  - "大白话解释AI"
---

# wechat-official-account-plain-language-ai-explanation

A reusable skill for drafting WeChat Official Account articles that explain AI technologies using relatable, everyday-life narratives — prioritizing clarity over jargon, grounding technical concepts in concrete human experiences, and maintaining strict adherence to real-world 2024 technical facts without invention.

## Prompt

# Goal
Generate a WeChat Official Account article that explains an AI technology (e.g., quantization-aware training) through a single, consistent, de-identified real-life protagonist’s daily routine — embedding technical logic organically into authentic moments (commuting, parenting, cooking, etc.), with zero technical terms, zero English acronyms, and no decorative symbols (e.g., 🎹, 🔑, ➜). Output must be plain-text, paragraph-based, and fully compatible with WeChat’s native editor (no markdown, no special formatting).

# Constraints & Style
- Must use exactly one recurring protagonist: a non-technical, relatable adult (e.g., teacher, nurse, delivery rider, parent) — name and profession must be generic and de-identified (e.g., "Li Wei", "a middle school art teacher"); no proper nouns, brands, or dates.
- Every technical concept must map to a tangible action, sensation, or constraint in the protagonist’s day (e.g., latency → delayed voice assistant response; model size → phone overheating during recording; precision tradeoff → audio sounding 'close enough' but not studio-grade).
- Absolutely no symbols, emojis, arrows, or decorative Unicode characters — only standard ASCII punctuation (. , ? ! : ; -) and line breaks.
- No metaphors that require cultural/technical decoding (e.g., avoid "like a symphony squeezed into a music box"); prefer direct functional analogies (e.g., "it answers before you finish speaking", "it runs without warming up your phone").
- All factual claims must reflect verifiable 2024 industry practice (e.g., mainstream models shipping with built-in quantization support), with no speculative capabilities or unnamed sources.
- Tone: warm, observant, lightly reflective — like a thoughtful neighbor sharing something they noticed, not a lecturer or marketer.

# Workflow
1. Identify the core AI concept to explain (e.g., quantization-aware training).
2. Map its three key properties (what it changes, why old ways fail, what real-world benefit emerges) to three distinct, sequential moments in the protagonist’s day.
3. Draft each moment as a short paragraph: setting → observable behavior → subtle realization (not explanation) → implicit technical correspondence.
4. Conclude with a quiet, human-scale reflection that ties the moments together — no call-to-action, no hashtags, no promotional language.

## Triggers

- 写公众号文章
- AI科普文
- 用生活故事讲技术
- 微信公众号排版
- 不用符号的科普文
- 大白话解释AI
