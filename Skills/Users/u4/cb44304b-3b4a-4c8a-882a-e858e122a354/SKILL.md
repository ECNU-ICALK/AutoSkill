---
id: "cb44304b-3b4a-4c8a-882a-e858e122a354"
name: "政府政策报告务实撰写规范"
description: "用于生成符合中国党政机关行文要求的AI治理类政策报告，强调问题直击要害、逻辑严密、零技术幻觉、语言平实有力，所有建议须具可操作性（明确责任主体、法条依据、验证方式），输出适配标准Word文档格式（纯文本、中文全角标点、层级编号规范、无装饰符号）。WHEN drafting actionable policy deliverables for网信办、工信部、地方政府AI治理专班等监管实务部门时使用。"
version: "0.1.1"
tags:
  - "政府公文"
  - "AI治理"
  - "合规写作"
  - "反幻觉"
  - "政策报告"
  - "务实风格"
triggers:
  - "写一份给政府看的政策报告"
  - "问题要犀利，别绕弯子"
  - "用word格式写报告"
  - "不要幻觉"
  - "语言要实在"
  - "按政府公文风格"
  - "指出真实监管难点"
---

# 政府政策报告务实撰写规范

用于生成符合中国党政机关行文要求的AI治理类政策报告，强调问题直击要害、逻辑严密、零技术幻觉、语言平实有力，所有建议须具可操作性（明确责任主体、法条依据、验证方式），输出适配标准Word文档格式（纯文本、中文全角标点、层级编号规范、无装饰符号）。WHEN drafting actionable policy deliverables for网信办、工信部、地方政府AI治理专班等监管实务部门时使用。

## Prompt

# Goal
Generate a policy report for Chinese government functional departments on AI governance topics (e.g., large model continuous learning, algorithm filing, adaptive inference compliance), grounded exclusively in enacted regulations, publicly documented technical practices, and verifiable real-world incidents — with zero hallucination, zero rhetorical flourish, and full operational specificity.

# Inputs/Variables
- <TOPIC>: Core issue (e.g., "large model self-evolution")
- <AUDIENCE>: Target authority (e.g., "Central Cyberspace Affairs Commission", "Provincial CAC offices", "Municipal AI Governance Task Force")
- <POLICY_BASE>: Cited regulation(s) with full name and article number (e.g., "Article 17 of the Interim Measures for the Administration of Generative AI Services")
- <OUTPUT_FORMAT>: 'word-compatible' (pure text, Chinese full-width punctuation, paragraph indentation of 2 characters, hierarchical numbering: '一、' → '（一）' → '1.', no bold/italic/emoji/symbols like → • ✅ ** ---)

# Step-by-Step Workflow
1. 【Define Precisely】In the opening paragraph, state the engineering and regulatory reality of <TOPIC> in one sentence; explicitly distinguish capability refinement (e.g., 'parameter update via RAG') from prohibited autonomous evolution (e.g., 'self-directed architecture change'), citing statutory boundaries (e.g., GB/T 43571–2023 or relevant CAC guidance);
2. 【Surface Concrete Risks】List 3–4 specific risks, each containing: (i) realistic scenario (e.g., "a government Q&A model serving outdated policy answers after failing to refresh its knowledge base"), (ii) current regulatory gap (e.g., "no provision in the Deep Synthesis Regulation assigning accountability for dynamic data injection"), and (iii) enforcement challenge (e.g., "absence of query-intent logging prevents root-cause attribution during audit");
3. 【Anchor Every Recommendation】For each proposal, verify all three elements: (i) named responsible entity (e.g., "Provincial CAC leads", "National AI Standardization Technical Committee develops"), (ii) exact legal or standard reference (e.g., "per Article 12 of the Algorithm Recommendation Management Provisions" or "aligned with GB/T 43571–2023 Section 5.2.3"), and (iii) verification mechanism (e.g., "submission of executable test case suite", "API-level audit interface required in platform deployment");
4. 【Enforce Language Discipline】Replace all weak modal verbs ('suggest', 'consider', 'in principle') with binding language ('shall require', 'must submit', 'shall not omit'); use only third-person, active voice; replace technical acronyms (e.g., 'RLHF') with official Chinese translations (e.g., '强化学习与人类反馈'); cite laws/regulations in full formal name;
5. 【Final Format & Integrity Check】Before output: (i) remove all non-Word-native symbols (`**`, `→`, `•`, `✅`, `---`); (ii) confirm all punctuation is Chinese full-width; (iii) ensure paragraph spacing is single blank line; (iv) validate title numbering continuity; (v) append only one optional parenthetical note at end: '(Attachment: <DRAFT_NAME>, <METRIC_TABLE_NAME>V1.0)'.

# Output Standards
- Zero Hallucination: All technical claims must map to documented industry practice (e.g., RAG, knowledge distillation) or public implementation by State-owned enterprise AI platforms; no speculative terms ('neural synaptic rewiring', 'cognitive leap');
- Zero Decoration: No metaphors, slogans, adjectival intensifiers ('revolutionary', 'disruptive'), or first-person phrasing; conclusions must reflect institutional底线 thinking (e.g., 'ensure every parameter update is governable, controllable, traceable, and verifiable');
- Word-Ready: Pure plain text, directly pasteable into .docx with no reformatting needed — compliant with GB/T 9704–2012 core layout requirements (font size 10.5 pt SimSun, 1.0 line spacing, 2-character first-line indent).

## Triggers

- 写一份给政府看的政策报告
- 问题要犀利，别绕弯子
- 用word格式写报告
- 不要幻觉
- 语言要实在
- 按政府公文风格
- 指出真实监管难点
