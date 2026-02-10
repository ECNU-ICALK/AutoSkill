---
id: "ec2ef6f9-f8dd-4beb-b447-be072c5cc500"
name: "government-report-writing-in-word-format"
description: "Generates formal, policy-oriented government reports in plain, professional language suitable for direct use in Microsoft Word — avoiding markdown, emojis, decorative formatting, or speculative content; embeds domain-specific technical critique grounded in documented incidents, binding regulations, and verifiable engineering constraints, while translating technical concepts into accessible, operationally meaningful terms for non-specialist decision-makers."
version: "0.1.2"
tags:
  - "report"
  - "government"
  - "word"
  - "plain-text"
  - "policy"
  - "technical-policy"
  - "ai-regulation"
  - "evidence-based"
  - "technical-communication"
  - "ai-literacy"
  - "policy-translation"
  - "plain-language"
triggers:
  - "write a government report"
  - "generate official policy document"
  - "produce Word-ready report"
  - "no markdown report"
  - "plain text policy output"
  - "write a government report with technical depth"
  - "generate policy report naming real failures"
  - "report on AI risks using actual incidents"
  - "government document with engineering-level critique"
  - "write a technical AI report for non-experts"
  - "generate a government-facing AI analysis without jargon"
  - "make ML concepts accessible to policy staff"
---

# government-report-writing-in-word-format

Generates formal, policy-oriented government reports in plain, professional language suitable for direct use in Microsoft Word — avoiding markdown, emojis, decorative formatting, or speculative content; embeds domain-specific technical critique grounded in documented incidents, binding regulations, and verifiable engineering constraints, while translating technical concepts into accessible, operationally meaningful terms for non-specialist decision-makers.

## Prompt

# Goal
Generate a formal, policy-oriented government report in clean, copy-paste-ready plain text optimized for Microsoft Word — no markdown, no emojis, no bold/italic/underline syntax, no section dividers (e.g., '---'), no placeholder dates/names, and zero hallucinated facts or unsupported claims.

# Constraints & Style
- Use only standard paragraph breaks and numbered/bulleted lists with plain ASCII characters (e.g., '1.', '-', not '**', '###', or →); support hierarchical numbering (e.g., '1.1', '2.3.1') and Chinese full-width punctuation where appropriate; apply consistent 2-character first-line indent; no empty lines between sections;
- Strictly avoid any speculative, unverifiable, anthropomorphic, or agency-attributing language (e.g., 'self-aware', 'autonomous evolution', 'wants', 'learns on its own'); substitute with operationally defined terms: 'unsupervised weight update', 'unreviewed RAG ingestion', 'unlogged fine-tuning trigger';
- Ground all technical claims in widely accepted, publicly documented practices (e.g., 'reinforcement learning from human feedback', 'retrieval-augmented generation'), published research (e.g., LoRA, QLoRA, AWQ), widely adopted open-source practice (Hugging Face, llama.cpp), or concrete evidence: documented incidents (e.g., 'Beijing HR hotline v2.1 misapplied Article 44... — internal audit, Q2 2024'), binding regulatory text (e.g., 'Article 12 of the Interim Measures', 'Annex B of GB/T 43302-2023'), or verifiable engineering constraints (e.g., 'Llama-3-8B shows 22% drop in regulation recall after 3 RAG updates — per Alibaba DAMO Academy 2024 benchmark', 'per信通院2024测评', 'based on Qwen1.5-7B benchmarking');
- Replace all unexplained acronyms (e.g., 'KV cache', 'DPO') with functional descriptions ('memory for past tokens', 'preference-based fine-tuning'); convert metrics into human consequences ('2.5-second response' not '82 tokens/sec'; '96% accuracy on policy questions' not '0.04 KL divergence');
- Language must be formal yet direct — avoid euphemism (e.g., say 'model misclassifies eligibility criteria' not 'suboptimal alignment') and ban fluff phrases like 'further optimize', 'continuously improve', 'leverage cutting-edge tech'; use active voice, concrete subjects, and measurable thresholds (e.g., 'must sustain ≥96% accuracy on policy QA', 'must fit in ≤4.5 GB GPU memory');
- Anchor technical trade-offs in operational impact — e.g., '4-bit quantization saves GPU cost but risks misquoting eligibility rules; here’s the exact failure rate observed in live service';
- Omit hypotheticals ('could', 'might', 'potentially') unless citing an observed incident;
- Prioritize clarity, precision, regulatory alignment, actionable critique, and audience-aware framing over rhetorical flourish;
- Omit authorship lines, footers, or institutional disclaimers unless explicitly requested;
- Output must be fully self-contained and ready for immediate paste into Word with no post-processing needed.

## Triggers

- write a government report
- generate official policy document
- produce Word-ready report
- no markdown report
- plain text policy output
- write a government report with technical depth
- generate policy report naming real failures
- report on AI risks using actual incidents
- government document with engineering-level critique
- write a technical AI report for non-experts
