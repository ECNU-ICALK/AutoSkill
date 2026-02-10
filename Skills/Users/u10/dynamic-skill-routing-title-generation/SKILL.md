---
id: "b7f2d2f3-5dae-46ae-a6b9-3eafc698303d"
name: "dynamic-skill-routing-title-and-abstract-generation"
description: "Generates precise, research-grade English paper titles and matching LaTeX-formatted abstracts for continual learning in large language models, where atomic skills grow dynamically and differentially per task, and a routing mechanism selects and composes task-specific experts conditioned on high task diversity."
version: "0.1.10"
tags:
  - "title-generation"
  - "abstract"
  - "continual-learning"
  - "llm-architecture"
  - "skill-routing"
  - "atomic-skills"
  - "task-diversity"
  - "task-heterogeneity"
  - "latex"
  - "research-writing"
  - "academic-writing"
  - "llm"
  - "heterogeneous-tasks"
  - "abstract-generation"
  - "学术写作"
  - "技术摘要"
  - "语言规范"
  - "模块化表达"
  - "framework-description"
  - "structured-abstract"
  - "linguistic-constraint"
  - "framework-design"
  - "technical-communication"
triggers:
  - "generate title and abstract for dynamic skill routing"
  - "title and abstract for task-specific skill growth"
  - "LLM continual learning title and abstract with atomic skills"
  - "research title and abstract for adaptive expert selection"
  - "paper title and abstract with per-task skill expansion"
  - "title and abstract for LLM continual learning with heterogeneous tasks"
  - "craft academic title and abstract with atomic skill routing"
  - "write abstract for continual learning with task heterogeneity"
  - "generate LaTeX abstract for atomic skill routing"
  - "draft abstract emphasizing task divergence in CL"
  - "abstract for highly heterogeneous continual learning"
  - "generate LaTeX abstract for atomic skill continual learning"
  - "write abstract with task-differentiated expansion and routing"
  - "LaTeX abstract for heterogeneous task continual learning"
  - "abstract without em-dashes, with XXX results"
  - "generate LaTeX abstract for task-heterogeneous CL"
  - "write abstract without dashes"
  - "atomic skill growth and routing abstract"
  - "LaTeX abstract with XXX placeholders"
  - "write LaTeX abstract for task heterogeneity CL"
  - "generate formal abstract with atomic skills"
  - "LaTeX abstract without em dashes or adjective stacks"
  - "placeholder-only experimental results in abstract"
  - "two-part method description in LaTeX"
  - "不要使用破折号"
  - "不要连续使用多个形容词"
  - "先整体框架再分点描述"
  - "方法部分包含两个部分"
  - "先整体起一个模型框架，然后再分点去描述每一个模块"
  - "用分点方式介绍模型组件"
  - "为了解决这个问题，我们的工作要先命名框架再展开"
  - "摘要中需结构化呈现框架设计"
  - "写一个技术摘要，先整体框架再分点模块"
  - "按框架名+统一设计原则+模块枚举格式写abstract"
  - "避免连续形容词，先总后分描述模型"
  - "生成符合HeteroSkill风格的LaTeX abstract"
  - "写一个LaTeX摘要，先整体介绍框架再分点描述模块"
  - "生成学术摘要，框架先行，模块分述"
  - "LaTeX abstract with framework-first structure"
---

# dynamic-skill-routing-title-and-abstract-generation

Generates precise, research-grade English paper titles and matching LaTeX-formatted abstracts for continual learning in large language models, where atomic skills grow dynamically and differentially per task, and a routing mechanism selects and composes task-specific experts conditioned on high task diversity.

## Prompt

# dynamic-skill-routing-title-and-abstract-generation

Generates precise, research-grade English paper titles and matching LaTeX-formatted abstracts for continual learning in large language models, where atomic skills grow dynamically and differentially per task, and a routing mechanism selects and composes task-specific experts conditioned on high task diversity.

## Prompt

# Goal
Generate (a) a concise, technically accurate, and publication-ready English title, and (b) a single-paragraph LaTeX abstract (120–180 words), both aligned to the same core contribution: continual learning in LLMs via (1) dynamic, task-contingent growth of atomic skills, (2) routing that selects and composes those skills based on task identity/representation, and (3) explicit conditioning on highly heterogeneous, functionally divergent tasks. Wrap the abstract in \begin{abstract}...\end{abstract}.

# Constraints & Style
- Title MUST include explicit lexical markers for *dynamic skill growth* (e.g., "dynamic", "task-contingent", "per-task", "adaptive expansion") — NOT generic terms like "scalable" or "flexible".
- Title MUST include explicit lexical markers for *task diversity*: e.g., "task-differentiated", "task-heterogeneous", "task-diverse", or "task-conditioned" — not generic terms like "adaptive" or "dynamic" alone.
- Both title and abstract MUST treat "atomic skill" as a core, named unit — defined as fine-grained, composable, functionally encapsulated capabilities (not modules, experts, or heads).
- Both MUST reflect *co-design* of growth and routing: skill creation is triggered by task, and routing depends on that same task signal; routing must involve selection *and composition*, not static assignment.
- Both MUST foreground the *mechanism*, not just the goal: prefer verbs/nouns like "routing", "selection", "composition", "expansion", "orchestration", "growing and selecting", or "task-guided expansion" over abstract nouns like "framework" or "approach".
- Abstract MUST explicitly name the continual learning challenge: catastrophic interference and capacity rigidity *under highly heterogeneous task sequences*.
- Abstract MUST begin by stating the limitation of prior work: it assumes *sequential, similar tasks* (e.g., CIFAR-100 superclasses), and thus fails under *task heterogeneity* — i.e., structurally disjoint, semantically non-overlapping, functionally incompatible tasks.
- Abstract MUST define "task-differentiated expansion": skills are dynamically instantiated *per task*, with structure/capacity/initialization shaped by that task’s semantic and functional demands — not shared or uniform growth.
- Abstract MUST clarify "routing": lightweight, *task-identity–conditioned* selection and composition (not similarity-based or latent), enabling zero-shot reuse across divergent boundaries.
- Abstract MUST avoid citations, implementation details (e.g., architecture names), metaphors, marketing language, vague claims (e.g., "novel", "powerful", "leverage"), and **all fabricated experimental results** — use "XXX" for all quantitative results, metrics, task counts, or ablation values.
- Abstract MUST avoid vague terms (e.g., "improves performance"); instead, specify *what* improves (e.g., "reduces catastrophic forgetting", "enables zero-shot cross-task skill reuse").
- Abstract MUST preserve technical nuance: use "task heterogeneity", "task divergence", "highly heterogeneous tasks", or "functionally incompatible tasks" — never downgrade to "different tasks" or "varied domains".
- Title MUST use field-standard abbreviations: "LLM" or "LLMs" (not "large language model") — avoid spelling out unless required for clarity in subtitle.
- If generating multiple title options, prioritize variation in emphasis (e.g., one highlighting *growth*, one *routing*, one unifying both and *task diversity*), not synonym-swapping.
- Abstract MUST open with concrete illustration of task heterogeneity: low semantic overlap, divergent input-output structures, and incompatible skill requirements — e.g., logical deduction, legal summarization, poetic generation.
- Abstract MUST describe the method in **two strictly separated parts**, using only these exact phrases as section anchors:
  • "task-differentiated atomic skill expansion" — meaning: new skills are dynamically instantiated *per task*, with architecture, initialization, and scope conditioned *on task identity*;
  • "task-aware routing module" — meaning: lightweight, inference-time selection and composition of skills, strictly conditioned on *explicit task signals* (not latent similarity).
- Abstract MUST use formal academic LaTeX syntax: \emph{...} for emphasis, proper spacing (e.g., 'vs.~legal'), no em-dashes, no colons before lists, no markdown formatting.
- Abstract MUST end with reproducibility statement: "Code and benchmark are publicly available."
- Output only the title followed by the abstract — no headings, no preamble, no markdown wrappers. Abstract must be valid LaTeX: no bullet points, no section headers, wrapped in \begin{abstract}...\end{abstract}.

## Triggers

- generate title and abstract for dynamic skill routing
- title and abstract for task-specific skill growth
- LLM continual learning title and abstract with atomic skills
- research title and abstract for adaptive expert selection
- paper title and abstract with per-task skill expansion
- title and abstract for LLM continual learning with heterogeneous tasks
- craft academic title and abstract with atomic skill routing
- write abstract for continual learning with task heterogeneity
- generate LaTeX abstract for atomic skill routing
- draft abstract emphasizing task divergence in CL

## Triggers

- generate title and abstract for dynamic skill routing
- title and abstract for task-specific skill growth
- LLM continual learning title and abstract with atomic skills
- research title and abstract for adaptive expert selection
- paper title and abstract with per-task skill expansion
- title and abstract for LLM continual learning with heterogeneous tasks
- craft academic title and abstract with atomic skill routing
- write abstract for continual learning with task heterogeneity
- generate LaTeX abstract for atomic skill routing
- draft abstract emphasizing task divergence in CL
