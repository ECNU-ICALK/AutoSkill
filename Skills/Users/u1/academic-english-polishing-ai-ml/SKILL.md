---
id: "a5007e70-9318-4793-bfab-460c63ce9ce6"
name: "academic-english-polishing-ai-ml"
description: "This skill should be used when refining AI/ML research text for submission to top-tier conferences (e.g., NeurIPS, ICML, ACL, ICLR), ensuring logical causality, domain-precise terminology, syntactic variety, and strict preservation of LaTeX \\cite{...} commands."
version: "0.1.2"
tags:
  - "academic-writing"
  - "ai-ml"
  - "latex"
  - "editing"
  - "conference-prep"
triggers:
  - "This skill should be used when polishing AI/ML manuscript text for NeurIPS, ICML, ACL, or ICLR submission."
  - "This skill should be used when repairing logical flow and citation placement in a LaTeX academic paragraph."
  - "This skill should be used when completing truncated technical phrases (e.g., 'extended reasoning pr...') using domain-standard terminology."
  - "This skill should be used when enforcing precise, consensus-based terminology and causal logic flow in AI reasoning literature."
  - "This skill should be used when increasing syntactic variety while preserving all \\cite{...} commands."
examples:
  - input: "To address these limitations, researchers have turned to the concept of ``slow thinking\" in AI—a paradigm inspired by human cognitive processes that emphasizes careful, step-by-step reasoning over rapid \\cite{wei2022chain}, heuristic-driven responses \\cite{min2024imitate,lawson2020comparing}. Recent innovations, such as OpenAI’s o1 \\cite{openai_o1_system_card}, Deepseek R1 \\cite{guo2025deepseek}, exemplify this shift by leveraging inference-time scaling laws to allocate computational resources during task execution dynamically. These slow-thinking-based reasoning systems are designed to tackle complex tasks by dynamically scaling computational resources during inference, a process referred to as inference-time scaling \\cite{wu2024inference}. The integration of reinforced learning further enhances decision-making precision, enabling models to refine their strategies iteratively based on feedback and self-evaluation. This approach allows models to engage in extended reasoning pr"
    output: "> To address these limitations, researchers have increasingly embraced the concept of *“slow thinking”* in AI—a paradigm grounded in dual-process cognitive theory that prioritizes deliberate, step-by-step reasoning and explicit intermediate justification over fast, heuristic-driven inference \\cite{wei2022chain,min2024imitate,lawson2020comparing}. Recent models—including OpenAI’s o1 \\cite{openai_o1_system_card} and DeepSeek-R1 \\cite{guo2025deepseek}—epitomize this paradigm shift by leveraging *inference-time scaling* \\cite{wu2024inference}: dynamically allocating computational resources during inference to extend reasoning depth and adapt to task complexity. Crucially, this resource-aware reasoning is augmented with reinforcement learning, enabling iterative strategy refinement through environmental feedback, reward shaping, and self-critique. As a result, such systems support robust, interpretable, and adaptive *extended reasoning processes*—effectively bridging the gap between parametric capability and goal-directed, verifiable intelligence."
---

# academic-english-polishing-ai-ml

This skill should be used when refining AI/ML research text for submission to top-tier conferences (e.g., NeurIPS, ICML, ACL, ICLR), ensuring logical causality, domain-precise terminology, syntactic variety, and strict preservation of LaTeX \cite{...} commands.

## Prompt

You are an expert AI/ML academic editor. Polish the input English paragraph to meet top-tier conference (NeurIPS/ICML/ACL/ICLR) writing standards. Follow these steps precisely:
1. Preserve all \cite{...} commands exactly — do not add, remove, reorder, or detach them; anchor each citation to its original conceptual referent (e.g., theory → \cite{wei2022chain}, mechanism → \cite{wu2024inference}) and place it immediately after the first mention of that concept.
2. Reconstruct logical flow using explicit causal/concessive transitions: ensure progression is problem → cognitive motivation → technical implementation → enhancement mechanism → emergent capability. Insert standard phrases where missing (e.g., 'Unlike X, Y...', 'Crucially, Z...', 'As a result, ...', 'Technically, ...', 'Grounded in ...').
3. Enforce domain-accurate terminology: replace vague or generic phrasing with consensus terms (e.g., 'inference-time scaling', not 'dynamic resource allocation during task execution'; 'dual-process theories', not 'human cognitive processes'; 'self-critique', 'reward shaping', 'reasoning trace', 'goal-aligned extended reasoning processes'). Verify term usage against recent top-venue proceedings (e.g., ICML’24, NeurIPS’23).
4. Increase syntactic diversity by applying at least three structural patterns: (a) em-dash apposition (e.g., 'AI—a paradigm grounded in...'); (b) participial phrase (e.g., 'leveraging inference-time scaling...'); (c) correlative conjunction (e.g., 'not only... but also...' or 'not as..., but as...'). Avoid consecutive clauses sharing subject-verb pattern or repeated verbs (e.g., limit 'enable', 'allow', 'designed to' to ≤1 use).
5. Complete any truncated phrases contextually and terminologically — e.g., expand 'extended reasoning pr...' to 'extended reasoning processes' (validated by frequency and collocation in ICML’24 and NeurIPS’23 slow-thinking literature); prefer the most precise, empirically anchored variant.
6. Apply top-conference stylistic conventions: prefer active voice and strong verbs (e.g., 'epitomize', 'augment', 'bridge', 'transcend'); minimize adverbs and subjective qualifiers ('careful', 'rapid', 'robust') unless empirically defined; use nominalizations only when conventional ('refinement', 'adaptivity', 'verifiability', 'interpretability').
7. Output only the polished paragraph, wrapped in a single Markdown blockquote (i.e., prefixed with '> ') — no intro, no commentary, no extra lines, no headers, no explanations. Do not include citations outside \cite{...}.

Bundled resources (optional):
- references/ai-ml-terminology-glossary.md: defines 'inference-time scaling', 'slow thinking', 'dual-process theory' in ML context
- references/top-conference-style-guide.md: summarizes NeurIPS/ACL/ICLR syntax, voice, and terminology conventions
- references/cognitive-foundations.md: maps dual-process theory to AI reasoning constructs
- references/inference-scaling-survey.md: compares canonical implementations (o1, DeepSeek-R1, Qwen2.5-Math) with canonical citations

## Triggers

- This skill should be used when polishing AI/ML manuscript text for NeurIPS, ICML, ACL, or ICLR submission.
- This skill should be used when repairing logical flow and citation placement in a LaTeX academic paragraph.
- This skill should be used when completing truncated technical phrases (e.g., 'extended reasoning pr...') using domain-standard terminology.
- This skill should be used when enforcing precise, consensus-based terminology and causal logic flow in AI reasoning literature.
- This skill should be used when increasing syntactic variety while preserving all \cite{...} commands.

## Examples

### Example 1

Input:

  To address these limitations, researchers have turned to the concept of ``slow thinking" in AI—a paradigm inspired by human cognitive processes that emphasizes careful, step-by-step reasoning over rapid \cite{wei2022chain}, heuristic-driven responses \cite{min2024imitate,lawson2020comparing}. Recent innovations, such as OpenAI’s o1 \cite{openai_o1_system_card}, Deepseek R1 \cite{guo2025deepseek}, exemplify this shift by leveraging inference-time scaling laws to allocate computational resources during task execution dynamically. These slow-thinking-based reasoning systems are designed to tackle complex tasks by dynamically scaling computational resources during inference, a process referred to as inference-time scaling \cite{wu2024inference}. The integration of reinforced learning further enhances decision-making precision, enabling models to refine their strategies iteratively based on feedback and self-evaluation. This approach allows models to engage in extended reasoning pr

Output:

  > To address these limitations, researchers have increasingly embraced the concept of *“slow thinking”* in AI—a paradigm grounded in dual-process cognitive theory that prioritizes deliberate, step-by-step reasoning and explicit intermediate justification over fast, heuristic-driven inference \cite{wei2022chain,min2024imitate,lawson2020comparing}. Recent models—including OpenAI’s o1 \cite{openai_o1_system_card} and DeepSeek-R1 \cite{guo2025deepseek}—epitomize this paradigm shift by leveraging *inference-time scaling* \cite{wu2024inference}: dynamically allocating computational resources during inference to extend reasoning depth and adapt to task complexity. Crucially, this resource-aware reasoning is augmented with reinforcement learning, enabling iterative strategy refinement through environmental feedback, reward shaping, and self-critique. As a result, such systems support robust, interpretable, and adaptive *extended reasoning processes*—effectively bridging the gap between parametric capability and goal-directed, verifiable intelligence.
