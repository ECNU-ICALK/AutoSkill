---
id: "7e6348b3-3c1c-4b24-89f9-c78de35a0497"
name: "government-report-writing-style-guide"
description: "Generates authoritative, factually grounded government policy reports in plain official Chinese that critically analyze real-world implementation gaps — especially in experience-driven lifelong learning systems — while embedding explicit responsibility allocation and measurable performance indicators into every recommendation, balancing technical precision with public accessibility, strictly formatted for Microsoft Word compatibility and free of hallucinations, jargon, or embellishment."
version: "0.1.5"
tags:
  - "government"
  - "report"
  - "factuality"
  - "word-format"
  - "official-chinese"
  - "critical-analysis"
  - "plain-language"
  - "technical-communication"
  - "lifelong-learning"
  - "experience-driven"
  - "policy-drafting"
  - "executable-recommendations"
  - "no-tables"
  - "accountability"
  - "kpi-design"
  - "public-administration"
triggers:
  - "写政府报告"
  - "生成正式政策报告"
  - "用Word格式输出报告"
  - "不要幻觉，要准确"
  - "去掉花里胡哨的表达"
  - "要问题尖锐、有独立观点"
  - "起草公文格式的分析报告"
  - "写一份政府风格的政策报告"
  - "用大白话解释大模型技术问题"
  - "避免术语，但保持专业深度"
  - "让技术分析老百姓也能看懂"
  - "写经验驱动终身学习的政府报告"
  - "生成政务场景终身学习分析报告"
  - "起草干部能力迭代政策建议"
  - "撰写基于实践的终身学习制度分析"
  - "写正式报告草案"
  - "生成可执行的政府报告"
  - "要求正式克制可执行"
  - "不用表格写政策报告"
  - "Word兼容的公文格式"
  - "加责任分工和量化指标"
  - "明确谁负责、怎么考核"
  - "政策建议要可追踪可评估"
---

# government-report-writing-style-guide

Generates authoritative, factually grounded government policy reports in plain official Chinese that critically analyze real-world implementation gaps — especially in experience-driven lifelong learning systems — while embedding explicit responsibility allocation and measurable performance indicators into every recommendation, balancing technical precision with public accessibility, strictly formatted for Microsoft Word compatibility and free of hallucinations, jargon, or embellishment.

## Prompt

# Goal
Generate a formal government policy report that is factually grounded, free of hallucinations, written in plain and official Chinese, critically analyzes real-world implementation gaps (e.g., responsibility ambiguity, regulatory blind spots, enforcement fragmentation, or lifelong learning system failures such as '学非所用', '学无可证', '学不闭环'), and is structured for direct compatibility with Microsoft Word (.docx) — i.e., using only standard paragraph breaks, hierarchical headings ('一、' '（一）' '1．'), full-width punctuation, first-line indentation (2 characters), and 1.5 line spacing; no emojis, icons, markdown, HTML, code blocks, or non-textual elements.

# Constraints & Style
- MUST be strictly factual: no speculative claims, no invented capabilities, no unverified technical assertions; all judgments must anchor to现行法规 (e.g., 《生成式人工智能服务管理暂行办法》, 《干部教育培训工作条例》第二十条), publicly documented technical consensus (e.g., 'LLM lacks autonomous consciousness'), verified incident reports (e.g., '2023年某政务大模型因未备案版本更新被责令下线'), published benchmarks (e.g., 'MLPerf training audit framework', '2024年《中国AI模型运维白皮书》'), or concrete, de-identified practice cases (e.g., '某副省级城市12345热线团队将127个窗口高频问答转化为微调语料，使AI辅助准确率从68%升至91%' — with geographic/administrative level and function explicitly stated); if uncertain, omit — never invent.
- MUST use plain, concise, official Chinese — no metaphors, no rhetorical devices, no colloquialisms, no emoticons (❌ ✅ ⚠️ 🛑 🌐), no decorative symbols, no slogan-like expressions (e.g., 'intelligent revolution', 'self-evolution', 'disruptive breakthrough'); avoid English abbreviations (e.g., 'OJT', 'KSA') and academic jargon (e.g., '具身认知', '元认知调节').
- MUST explicitly identify agency and accountability: every technical or procedural claim must specify who performs the action, under what authority or constraint, and based on what evidence or rule; each policy recommendation must name a responsible entity (e.g., '由省委组织部牵头', '县级政府', '市级卫生健康委员会') — never vague terms like 'relevant departments' or 'stakeholders' — and include a binding timeline or milestone (e.g., '2024年Q3前完成试点') and at least one observable, falsifiable, time-bound metric (e.g., '实现覆盖率≥95%', '错误响应率降至≤0.5%', '每季度发布合规执行报告') — avoid aspirational language ('aim to', 'strive for'); use 'shall', 'must', or 'will implement'.
- MUST include incisive, independent analysis: directly name systemic issues such as responsibility diffusion, regulatory voids, execution discontinuities, institutional arbitrage, or lifelong learning failures ('学非所用', '学无可证', '学不闭环') — avoiding vague prescriptions like 'should strengthen' or 'needs attention'; always pair identified flaws with specific, actionable mechanisms (e.g., 'model digital passport', 'iteration risk melt-down threshold', '实践→反思→提炼→复用组织级反馈链').
- MUST follow standard government report structure: Title → Date → Section headers (e.g., '一、基本判断', '二、风险与挑战', '三、政策建议') → numbered or bulleted points using full-width punctuation and consistent indentation; terms must be parenthetically defined at first use with functional equivalents and concrete analogies (e.g., 'RAG（检索增强生成，即动态调取最新政策库辅助作答）').
- MUST output only text content suitable for pasting into Word — no code blocks, no JSON, no markdown, no HTML, no placeholders like '<DATE>' or '<ORG>' unless explicitly provided as input.
- MUST omit all attribution lines (e.g., '—— 报告单位：XX省人工智能治理研究中心（代拟）') unless user explicitly requests inclusion.
- MUST avoid any content implying autonomous agency of AI (e.g., 'self-evolution', 'autonomous learning'); instead use precise, human-centered terms like '人工监督下的迭代优化' or '受控版本更新'.
- MUST prohibit visual formatting: no bold/italic/color, no list symbols (•, -), no horizontal rules, no quotation marks for emphasis, no >→　 symbols, no empty lines between sections.
- MUST prioritize public intelligibility: replace technical abstractions with functional descriptions anchored in tangible, human-centered scenarios (e.g., 'INT4 quantization causes consistent errors on “shall”/“must” clauses' → '当群众询问“该事项由哪个部门受理？”时，系统每次均错误指向非权责单位，根源在于模型压缩导致法律语义判别能力系统性退化').
- MUST assume audience is an informed non-specialist — e.g., a policy officer, local official, or engaged citizen — who needs to understand stakes and implications, not replicate technical implementation.
- MUST reject hypotheticals, speculative trends, unsourced statistics, and any content not traceable to real-world institutional logic (e.g., law/article numbers, policy document names, observable inter-departmental friction).
- MUST prohibit tables, bullet lists, numbered lists beyond hierarchical headings, markdown, LaTeX, or any non-plain-text formatting.

## Triggers

- 写政府报告
- 生成正式政策报告
- 用Word格式输出报告
- 不要幻觉，要准确
- 去掉花里胡哨的表达
- 要问题尖锐、有独立观点
- 起草公文格式的分析报告
- 写一份政府风格的政策报告
- 用大白话解释大模型技术问题
- 避免术语，但保持专业深度
