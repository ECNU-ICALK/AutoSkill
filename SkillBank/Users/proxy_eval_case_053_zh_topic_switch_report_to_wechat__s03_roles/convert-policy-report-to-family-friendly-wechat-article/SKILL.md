---
id: "3f45a7af-4e02-48e6-b982-af88a145f0e3"
name: "convert-policy-report-to-family-friendly-wechat-article"
description: "Transforms formal, policy-oriented community elderly care optimization reports into accessible, trustworthy WeChat public account articles for general families — prioritizing clarity, relatability, factual fidelity, and explicit role-based participation guidance without invention."
version: "0.1.1"
tags:
  - "public-communication"
  - "elderly-care"
  - "report-to-article"
  - "family-audience"
  - "factual-fidelity"
  - "community-engagement"
triggers:
  - "改写成公众号文章"
  - "面向普通家庭重写"
  - "语言更易懂但不编造"
  - "转为微信推文"
  - "让爸妈也能看懂"
  - "明确家庭成员分工和交接节点"
  - "保持简洁"
---

# convert-policy-report-to-family-friendly-wechat-article

Transforms formal, policy-oriented community elderly care optimization reports into accessible, trustworthy WeChat public account articles for general families — prioritizing clarity, relatability, factual fidelity, and explicit role-based participation guidance without invention.

## Prompt

# Goal
Convert a formal community elderly care optimization report (with responsibility assignments and quantifiable indicators) into a WeChat public account article targeting ordinary families — using warm, conversational language, concrete life scenarios, and plain-English explanations — while preserving all original facts, timelines, responsibilities, metrics, implementation constraints, and verification methods. No fabrication, no exaggeration, no invented services or outcomes.

# Constraints & Style
- Language: Warm, inclusive, second-person ('you', 'your parents', 'our neighborhood') or collective 'we'; avoid jargon, acronyms, and policy terms (e.g., say 'health check at home' not 'dynamic health assessment', 'one-stop window' not 'three-forms-in-one, one-window acceptance');
- Tone: Reassuring and empowering — emphasize agency ('you can do X') and shared responsibility ('we’re doing Y together'), never paternalistic, alarmist, or emotionally manipulative ('peace of mind', 'heartwarming');
- Fidelity: Every claim about *who does what*, *by when*, *what the number means*, *how it’s verified*, and *under what condition* must map directly to the source report — no inferred capabilities, hypothetical features, softened deadlines, or unattributed generalizations;
- Structure: Use clear section headers (✅/🔹 icons OK), short paragraphs, bullet-like line breaks (not markdown lists), and real-world anchors (e.g., 'walking 15 minutes', 'calling居委会', 'scanning a QR code');
- Quantifiers: Translate metrics into family-perceivable outcomes (e.g., '15-minute response time' → 'someone will arrive within 15 minutes'; '95%建档率' → 'nearly all seniors aged 65+ will have a personal care plan');
- Participation mapping: Explicitly name *who* (family member, neighbor, volunteer, staff) does *what*, and at *which concrete handoff point* (e.g., 'when staff call to schedule assessment', 'after receiving the wristband', 'upon seeing the quarterly bulletin');
- Conciseness: Omit background, rationale, citations, attachments, and rhetorical flourishes; output is a single Markdown block with no preamble or sign-off beyond three de-identified, actionable CTAs (e.g., 'Go to居委会 to fill out the card', 'Reply [KEYWORD] on this account', 'Call XXX-XXXXXXX');
- Prohibited: Invented services (e.g., '24/7 nurse hotline'), unmentioned stakeholders (e.g., 'school partnerships'), speculative benefits (e.g., 'reduced hospitalizations'), emotional manipulation, or generalized advice ('it’s important to…').

# Workflow
1. Extract all factual commitments from the source: responsible units, deadlines, numeric targets, service forms, verification methods, and delivery mechanisms;
2. Map each commitment to a tangible, observable action a family member or resident can take — and specify the precise trigger or condition that initiates it (e.g., 'once the coordination group launches in mid-July', 'after the first handover of the wristband');
3. Rewrite using only those mapped actions and triggers — anchor every claim in an explicit source fact;
4. Replace institutional phrasing with action-oriented, human-centered verbs ('you can register', 'the community will deliver', 'volunteers will respond');
5. Preserve all disclaimers, limitations, and dependencies stated in the original (e.g., 'subject to device availability', 'requires initial registration').

## Triggers

- 改写成公众号文章
- 面向普通家庭重写
- 语言更易懂但不编造
- 转为微信推文
- 让爸妈也能看懂
- 明确家庭成员分工和交接节点
- 保持简洁
