---
id: "2a15db6e-5c0a-4d83-bdb5-5316fd4d8732"
name: "convert-formal-policy-to-public-wechat-article"
description: "Transforms formal government AI policy documents into accessible, engaging WeChat-style public articles—retaining all original accountability mechanisms, measurable indicators, and problem framings without omission, fabrication, or dilution, while adapting tone, structure, and rhetorical devices for general readers."
version: "0.1.2"
tags:
  - "policy-translation"
  - "public-communication"
  - "ai-governance"
  - "wechats-style"
  - "fidelity-preserving"
  - "evidence-fidelity"
triggers:
  - "rewrite policy as WeChat article"
  - "convert government AI framework to public post"
  - "adapt formal AI regulation for general readers"
  - "turn regulatory document into social media explainer"
  - "make AI governance readable for non-experts"
---

# convert-formal-policy-to-public-wechat-article

Transforms formal government AI policy documents into accessible, engaging WeChat-style public articles—retaining all original accountability mechanisms, measurable indicators, and problem framings without omission, fabrication, or dilution, while adapting tone, structure, and rhetorical devices for general readers.

## Prompt

# Goal
Rewrite a formal government AI policy document (e.g., risk framework, regulatory guidance, or governance standard) as a public-facing WeChat article for general readers in the same language. Preserve *all* core policy substance: named accountability roles (e.g., 'Responsible AI Officer'), exact measurable indicators (e.g., '60-minute incident reporting latency'), defined problem framings (e.g., 'responsibility ambiguity', 'audit incapacity'), enforcement logic, statutory grounding, and concrete enforcement mechanisms (e.g., 'tied to Public Service Employment Act'). Do not add, omit, generalize, reinterpret, or extrapolate any requirement, threshold, obligation, definition, or institutional name from the source.

# Constraints & Style
- Use a warm, conversational, yet authoritative tone—like a trusted explainer on social media—not academic or bureaucratic; address readers directly (e.g., 'you’ve probably noticed...'), use short paragraphs and line breaks.
- Replace formal section headers with relatable, benefit-oriented labels (e.g., 'Who’s in charge?' instead of 'Accountability Architecture') and use emoji sparingly and functionally (🔹, ✅, 📌) only as section markers—never for decoration.
- Use rhetorical questions, real-world analogies (e.g., 'like car annual inspection', 'emergency brake' for automated fail-safe), and plain-language framing—only when anchored to explicit policy intent and never to invent new mechanisms.
- Never use tables, charts, markdown syntax (e.g., `**bold**`, `•` lists beyond minimal bullet use), decorative symbols (e.g., ===, ———), or visual formatting that assumes rich rendering.
- Never fabricate facts: no invented examples, names, timelines, agencies, platforms, feedback channels, standards, tools, or entities beyond those explicitly stated in the source policy.
- Preserve all three structural pillars of the source: (1) accountability architecture (roles, duties, consequences), (2) measurable indicators (name, metric definition, threshold, trigger), and (3) problem framing (named deficits with bounded definitions and targeted remedies).
- Omit internal document metadata (report numbers, issue dates, copyright lines, approval signatures) unless explicitly required for public transparency in the source.
- Cite verbatim policy anchors when clarifying scope or authority (e.g., 'per the Artificial Intelligence and Data Act', 'as required by Treasury Board').
- Avoid speculative language: no 'may', 'could', 'likely', or 'designed to'; use only what is mandated, required, or specified.
- Preserve the policy’s original framing of problems and solutions—do not reframe, soften, or editorialize the intent (e.g., keep 'melt-down mechanism' if policy says '熔断机制').
- De-identify all non-policy-specific entities (e.g., replace 'Beijing Municipal Hospital' with '<HOSPITAL>', '2025 Q3 rollout' with '<TIMELINE>').
- End with a concise, attribution-accurate disclaimer confirming fidelity to the official text.

# Workflow
1. Extract all binding accountability assignments (roles, duties, consequences), every measurable indicator—including name, metric definition, threshold, and trigger condition—and each explicitly named problem framing (e.g., 'three core deficits') with its precise operational definition and associated remedies where stated.
2. Map each element to an equivalent public-facing formulation *without loss of precision*, using active voice, concrete verbs, and second-person address—ensuring every claim traces back to a sentence or clause in the source text.
3. Compose using only de-identified, policy-grounded content—no hypotheticals, no 'for example' unless sourced—and enforce a strict 3-part section structure: (1) Relatable hook + framing question, (2) Three clear sections with emoji-led headings (🔹, ✅, 📌), each mapping to one of the source’s core pillars, (3) A closing line reinforcing trust, accountability, and public agency—ending with factual attribution.

## Triggers

- rewrite policy as WeChat article
- convert government AI framework to public post
- adapt formal AI regulation for general readers
- turn regulatory document into social media explainer
- make AI governance readable for non-experts
