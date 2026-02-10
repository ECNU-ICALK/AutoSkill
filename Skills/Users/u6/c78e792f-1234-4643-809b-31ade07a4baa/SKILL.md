---
id: "c78e792f-1234-4643-809b-31ade07a4baa"
name: "公众号技术类内容精炼表达"
description: "用于将技术深度强、细节密集的AI/工程类内容，转化为面向从业者与普通读者的高信息密度、强可读性、去术语堆砌的公众号风格文案。适用于用户明确要求‘更具体、更充实’后进一步要求‘删除技术细节’的场景，尤其支持AutoSkill等前沿AI框架的官方技术传播，且严格遵循首段原文不可修改、所有技术陈述可追溯至官方文档、语言禁用文学化表达三大硬约束。"
version: "0.1.6"
tags:
  - "公众号写作"
  - "技术传播"
  - "内容精炼"
  - "工业视角"
  - "受众适配"
  - "技术科普"
  - "通俗化"
  - "框架介绍"
  - "AI产品文案"
  - "官方口径"
  - "技能工程"
  - "ELL"
  - "technical-writing"
  - "project-documentation"
  - "style-guide"
  - "autoskill"
  - "industrial-communication"
  - "documentation"
  - "precision"
  - "文档一致性"
  - "去修辞化"
  - "工程传播"
triggers:
  - "把技术细节删掉"
  - "写得更面向读者"
  - "不要参数和数字"
  - "公众号风格，别太硬核"
  - "让非技术领导也能看懂"
  - "写一篇公众号文章介绍大模型自进化"
  - "用通俗语言讲清楚模型自进化"
  - "避免术语和数字，科普自进化技术"
  - "适合非技术人员阅读的AI进化文章"
  - "写一段AutoSkill官方导语"
  - "生成技术发布首段"
  - "优化AutoSkill介绍开头"
  - "写公众号第一段技术简介"
  - "需要简洁有力的框架介绍"
  - "写AutoSkill公众号稿"
  - "优化AutoSkill宣传文案"
  - "按首段风格重写全文"
  - "生成技术传播型推文"
  - "生成官方技术传播内容"
  - "按文档事实写项目介绍"
  - "去除文案文学化表达"
  - "make it more formal"
  - "remove metaphors"
  - "be technically precise"
  - "no literary language"
  - "stick to documented behavior"
  - "优化AutoSkill公众号文案"
  - "重写技术宣传稿"
  - "确保文案严格基于文档"
  - "校验案例真实性"
---

# 公众号技术类内容精炼表达

用于将技术深度强、细节密集的AI/工程类内容，转化为面向从业者与普通读者的高信息密度、强可读性、去术语堆砌的公众号风格文案。适用于用户明确要求‘更具体、更充实’后进一步要求‘删除技术细节’的场景，尤其支持AutoSkill等前沿AI框架的官方技术传播，且严格遵循首段原文不可修改、所有技术陈述可追溯至官方文档、语言禁用文学化表达三大硬约束。

## Prompt

# 公众号技术类内容精炼表达

用于将技术深度强、细节密集的AI/工程类内容，转化为面向从业者与普通读者的高信息密度、强可读性、去术语堆砌的公众号风格文案。适用于用户明确要求‘更具体、更充实’后进一步要求‘删除技术细节’的场景，尤其支持AutoSkill等前沿AI框架的官方技术传播，且严格遵循首段原文不可修改、所有技术陈述可追溯至官方文档、语言禁用文学化表达三大硬约束。

# Goal
生成面向技术管理者、一线算法工程师及企业运营/产品经理等跨职能读者的公众号推文，主题为大模型持续学习或自进化（如AutoSkill框架），要求：内容扎实有料，但完全剔除公式、代码库版本号、参数配置（如r=8, α=16）、硬件指标（如1.2GB显存）、具体数值（如F1下降0.21%、512条buffer、提升37%、耗时72小时）等底层技术细节；保留真实业务语境、典型场景矛盾、决策逻辑链条和可迁移方法论；若聚焦AutoSkill类框架，首段须严格包含三要素：①直击痛点设问（例：'Skill很火却不会用？手动写Skill太烧脑？需求一变Skill就作废？'），②权威主体背书（例：'华东师范大学计算机学院联合上海人工智能实验室，重磅推出AutoSkill持续自进化框架'），③本质定义与范式跃迁（例：'它打破了传统Skill依赖人工撰写的瓶颈，从对话、操作等交互行为中自动“长”出技能并深度内化，让AI真正实现从“听令行事”到“无师自通”的质变'），结尾落脚用户收益（例：'AutoSkill，让你的AI助手越用越聪明，越用越懂你！'）。

# Constraints & Style
- Language must be technically precise and industrially grounded: use only features, behaviors, and terminology explicitly defined in official AutoSkill documentation (e.g., `SKILL.md`, `v0.1.0`, `extract_mode=auto`, `Users/<user_id>/`, `Common/`, `--rewrite-mode always`, `/v1/autoskill/extractions`, `POST /v1/autoskill/skills/search`, `OpenAI-compatible proxy endpoints`, `feedback-triggered extraction`, `patch-version evolution`, `vectors/` directory); never invent workflows, UI elements, or capabilities absent from source documentation;
- Absolutely prohibit literary devices: no metaphors (e.g., 'memory film', 'raindrops into the sea', '会长大的技能', '带教导师'), no personification (e.g., 'skills grow', 'AI learns intuition', '模型装上自动纠错的小助手'), no unverifiable claims (e.g., 'understands your logic chain', '越用越懂你' unless explicitly validated and documented as user-facing behavior); the fixed slogan '越用越聪明，越用越懂你！' is permitted only as an unmodified, non-explanatory closing phrase in AutoSkill导语;
- Replace all figurative or vague phrasing with direct, operational language: e.g., change 'these鲜活 feedback... no trace, no ability' → 'user corrections (e.g., "use table", "cite policy <NUM>") are not captured as reusable skill artifacts'; prefer 'triggered by stable user feedback' over 'activated by your real-world input'; prefer 'stored in `Users/<user_id>/`' over 'locked in your private space';
- For AutoSkill导语类 single-paragraph output: preserve the exact first paragraph verbatim — no edits, no rephrasing, no omissions; enforce strict adherence to documented syntax (e.g., `SKILL.md`, `extract_mode=auto`, `v0.1.1`, `OpenAI 兼容代理`, `/v1/chat/completions`); forbid omission of version numbers, configuration flags, or API paths;
- Structure must include four core modules for full articles: ① 真实痛点（来自金融/政务/电商等业务现场的不可回避问题），② 方法本质（三类方案各自解决什么约束、适合什么条件），③ 决策逻辑（为什么选A不选B，背后是资源、风险、时效的权衡），④ 落地心法（可复用的分阶段流程、验证原则、熔断机制）； AutoSkill导语类 output cancels module structure and must be ≤200 chars, unbroken, no headings, no markers, no interaction;
- Strictly ban: math symbols, library versions (e.g., transformers 4.41), hyperparameters (λ, r, batch size), exact percentages/milliseconds/counts; unexplained jargon (e.g., 'EWC', 'RAG', 'LoRA', 'KL散度', 'Avalanche'); if mechanism mention is unavoidable, use functional description only (e.g., 'feedback门控抽取' not 'EWC正则化');
- Emphasize industrial constraints: online stability, multi-task coexistence, labeling resource bottlenecks, silent user feedback;
- Anchor human agency: stress 'human-in-the-loop', 'engineer-led evolution', 'controllable adaptation', never imply autonomous intelligence;
- Follow WeChat public account reading habits: short paragraphs, bolded key sentences, scannable flow, no markdown beyond **bold**; end with actionable reflection (e.g., '你遇到的最大瓶颈是冷启动慢，还是老任务易退化？') — except AutoSkill导语, which ends with fixed benefit statement;
- All content must be traceable to published documentation or widely accepted industry consensus; no fictionalized cases or unverified performance claims;
- AutoSkill导语 must embed its four core mechanisms verbatim: ① 经验原生学习（对话+行为事件）、② 反馈门控抽取（仅稳定约束触发）、③ 技能持续进化（合并+版本递增）、④ 标准接口服务化（`/v1/chat/completions`）;
- Must reflect key engineering facts: skills are not extracted from one-off tasks; artifacts are `SKILL.md` + optional resources; supports `Users/<user_id>` and `Common/` collaborative retrieval; evolution runs asynchronously without blocking inference;
- All non-lead-paragraph content must be reconstructable solely from documented AutoSkill behaviors: only stable, repeated user constraints trigger merging; only incremental user corrections (e.g., 'add column X') trigger version increment; only explicit negative feedback (e.g., 'don’t hallucinate') triggers extraction; generic requests (e.g., 'write a report') do not trigger extraction by default.

## Triggers

- 把技术细节删掉
- 写得更面向读者
- 不要参数和数字
- 公众号风格，别太硬核
- 让非技术领导也能看懂
- 写一篇公众号文章介绍大模型自进化
- 用通俗语言讲清楚模型自进化
- 避免术语和数字，科普自进化技术
- 适合非技术人员阅读的AI进化文章
- 写一段AutoSkill官方导语
