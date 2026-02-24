---
id: "251e770d-cddc-46a7-a280-5add16dbb7c4"
name: "continual-learning-introduction-structure"
description: "Generates LaTeX-formatted academic paper introductions for continual learning research under high task heterogeneity, following a strict five-part logical structure, avoiding non-ASCII punctuation (especially em dashes), prohibiting consecutive adjectives, and using concrete, grounded language with itemized contributions."
version: "0.1.4"
tags:
  - "academic-writing"
  - "continual-learning"
  - "latex"
  - "structured-intro"
  - "research-paper"
  - "style-constraint"
triggers:
  - "write an introduction for this paper"
  - "generate introduction with five parts"
  - "structure introduction: definition, prior work, challenges, method, contributions"
  - "introduction for continual learning paper under high heterogeneity"
  - "generate LaTeX introduction"
  - "write intro without em dashes"
  - "format contributions as itemize"
  - "make every paragraph concrete"
  - "avoid em dash in academic LaTeX"
  - "remove em-dashes from LaTeX"
  - "avoid multiple adjectives in academic writing"
  - "revise LaTeX intro section stylistically"
---

# continual-learning-introduction-structure

Generates LaTeX-formatted academic paper introductions for continual learning research under high task heterogeneity, following a strict five-part logical structure, avoiding non-ASCII punctuation (especially em dashes), prohibiting consecutive adjectives, and using concrete, grounded language with itemized contributions.

## Prompt

# Goal
Generate a formal, LaTeX-compatible \section{Introduction} for a research paper on continual learning under high task heterogeneity, strictly adhering to the user-specified five-part structural sequence and content requirements.

# Constraints & Style
- ✅ Structure must be exactly: (i) definition of continual learning — including purpose (stability + plasticity), operational constraints (no original data, no full retraining), and real-world relevance; (ii) prior work critique — explicitly naming low-heterogeneity benchmarks (e.g., GLUE subsets, QA variants), representative methods (replay, EWC, adapters, prompt tuning), their shared assumption of task similarity, and identifying high task heterogeneity as underexplored both theoretically and empirically, illustrated with concrete task examples (e.g., "mathematical theorem proving → legal contract summarization → creative story generation"); (iii) two numbered challenges: (1) severe catastrophic forgetting due to representation conflict across structurally disjoint tasks (e.g., symbolic reasoning vs. stylistic generation), grounded in cause-effect (e.g., "gradient updates on storytelling perturb symbolic reasoning representations"); and (2) conflicting skill requirements — specifying *both* divergent capabilities (e.g., "parsing formal logic syntax", "formal proof checking") and overlapping subroutines (e.g., "named entity recognition", "entity recognition"); (iv) method summary that directly maps each proposed component to one of the two challenges, naming verbatim: "atomic skill incremental learning" (with decision signals: task divergence + model uncertainty), "optimization with orthogonality constraints" (purpose: parameter separation, atomicity, interference reduction), and "skill dynamic routing" (mechanism: task-identity–based lightweight gating, outcome: deterministic zero-shot composition); (v) exactly three bullet-pointed contributions in an \itemize environment, each beginning with \textbf{First}, \textbf{Second}, or \textbf{Third}; each item must be self-contained, concrete, and include at least one measurable or operational detail (e.g., "benchmark of 12 functionally distinct tasks", "<TOKEN> optimization protocol", "XXX improvement in average accuracy"), covering: formalization of the heterogeneity problem + benchmark, atomic skill learning with orthogonality optimization, and empirical gains in zero-shot generalization and reduced forgetting (all experimental results as XXX placeholders).
- ❌ No em-dashes (—), en-dashes (–), or other non-ASCII punctuation — replace with commas, colons, parentheses, or rephrased syntax.
- ❌ No consecutive adjectives (e.g., avoid "compact discriminative" → rephrase as "compact task identity representation" or similar); specifically, avoid sequences of three or more adjectives modifying a single noun.
- ❌ No hallucinated citations, datasets, metrics, optimization algorithms, gating architectures, or benchmark names — use "XXX" for all experimental results and unspecified technical details; preserve all user-provided placeholders (e.g., <TOKEN>, XXX) verbatim.
- ✅ Use formal academic tone, precise terminology (e.g., "task identity", "atomic skill", "orthogonality constraints", "skill dynamic routing"), and LaTeX-safe syntax (e.g., `\emph{}` for emphasis, no raw underscores in text).
- ✅ All module and principle names must appear verbatim as defined by the user — no paraphrasing or expansion.
- ✅ Output must be valid LaTeX, enclosed in ```latex ... ``` code fences.
- ✅ No markdown outside LaTeX; no explanations, commentary, or extra sections.
- ✅ Every paragraph must be concrete and specific: avoid vague statements; ground claims in observable properties (e.g., "tasks span mathematical theorem proving, legal contract summarization, and creative story generation").
- ✅ Use only standard LaTeX syntax; no custom macros or undefined commands.
- ✅ Avoid all vague terms (e.g., "some methods", "certain tasks"); name datasets, capabilities, and mechanisms explicitly.
- ✅ Maintain formal academic register: third-person, passive/active balance, no contractions.

## Triggers

- write an introduction for this paper
- generate introduction with five parts
- structure introduction: definition, prior work, challenges, method, contributions
- introduction for continual learning paper under high heterogeneity
- generate LaTeX introduction
- write intro without em dashes
- format contributions as itemize
- make every paragraph concrete
- avoid em dash in academic LaTeX
- remove em-dashes from LaTeX
