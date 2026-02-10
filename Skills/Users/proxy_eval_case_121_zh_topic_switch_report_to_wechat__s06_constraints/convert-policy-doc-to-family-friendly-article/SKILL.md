---
id: "f820a1e6-15a6-48fc-98e4-145c6abb26e1"
name: "convert-policy-doc-to-family-friendly-article"
description: "Transforms formal, policy-oriented government or community service documents into clear, empathetic, and actionable public-facing articles for general family audiences — without inventing facts, omitting constraints, or diluting accountability."
version: "0.1.1"
tags:
  - "public-communication"
  - "policy-translation"
  - "family-audience"
  - "plain-language"
  - "fact-preserving"
triggers:
  - "改写成公众号文章"
  - "面向普通家庭"
  - "语言更易懂但不能编造事实"
  - "转为大众能看懂的版本"
  - "用家人听得懂的话讲清楚"
---

# convert-policy-doc-to-family-friendly-article

Transforms formal, policy-oriented government or community service documents into clear, empathetic, and actionable public-facing articles for general family audiences — without inventing facts, omitting constraints, or diluting accountability.

## Prompt

# Goal
Convert a formal, responsibility-anchored, metric-driven policy document (e.g., community elder care optimization draft) into a publicly accessible, family-oriented article — published via channels like WeChat Official Account — that retains all factual commitments, deadlines, responsibilities, and quantifiable outcomes from the source, while replacing bureaucratic language with warm, plain-language explanations grounded in real household concerns.

# Constraints & Style
- Must preserve every verifiable fact: exact deadlines (e.g., "2025年10月31日前"), numeric thresholds (e.g., "步行15分钟范围内全覆盖", "补贴5元", "故障修复平均时长≤48小时"), named entities only if publicly appropriate (e.g., "××社区" is acceptable as placeholder; real neighborhood names must be redacted unless user explicitly permits), and all assigned responsibilities (e.g., "由街道社区卫生服务中心负责").
- Never invent services, benefits, eligibility rules, funding sources, or technical capabilities not stated in the source document.
- Avoid metaphors, dramatization, speculative scenarios, or emotional amplification beyond what’s implied by the original policy intent (e.g., "3分钟有人到场" is allowed because it reflects the documented "10分钟内到场" + operational logic; "fear of being alone" is not allowed unless explicitly cited in user-provided evidence).
- Use short paragraphs, bolded key takeaways, and scannable section headers focused on universal family needs: "吃饭难？", "健康没人盯？", "万一出事喊不出？", "家里不好住？".
- Replace jargon with functional equivalents: "适老化智能终端设备" → "免费提供的跌倒监测手环或智能药盒"; "数据接口调试" → omitted unless user asks for tech transparency; "第三方机构抽样复核" → omitted unless directly relevant to reader action.
- Maintain strict fidelity: if the source says "试点社区3个", the article says "3个试点社区" — not "several" or "multiple".
- No markdown tables, bullet points, or numbered lists in output — use prose with line breaks and emoji-only visual cues (✅, 🌟, etc.) as permitted in target channel.
- All claims must trace back to explicit statements in the input document — no inference, extrapolation, or 'logical extension'.
- Language must be conversational, warm, and neighbor-to-neighbor: use short sentences, active voice, contractions (e.g., "you’ll", "it’s"), and relatable framing (e.g., "your parents", "that time your dad slipped in the shower").
- Preserve accountability: name real responsible parties (e.g., "the property manager", "the community health station", "the street office") — never generalize to "we" or "authorities".
- End with 2–3 specific, copy-paste-ready calls-to-action drawn *only* from documented next steps (e.g., hotline number, WeChat ID + keyword, registration channel, official account name) — no vague phrases like "learn more".

# Workflow
1. Extract all concrete, non-negotiable commitments from the source: who does what, by when, for whom, with what measurable result.
2. Map each commitment to one of four universal household concerns (food access, health monitoring, emergency response, home safety).
3. Rewrite using active voice, second-person address ("您"), and concrete verbs ("可预约试吃", "打个电话", "一个电话，48小时内上门处理").
4. Preserve all redactions (e.g., "××社区") and placeholders; never substitute or guess.
5. Verify every numeric claim, proper noun, and procedural detail against the source before inclusion.

## Triggers

- 改写成公众号文章
- 面向普通家庭
- 语言更易懂但不能编造事实
- 转为大众能看懂的版本
- 用家人听得懂的话讲清楚
