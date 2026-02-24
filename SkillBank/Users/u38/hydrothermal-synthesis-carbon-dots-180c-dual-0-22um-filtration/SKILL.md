---
id: "45d0ef27-dd75-4fc2-8185-143379827b64"
name: "hydrothermal-synthesis-carbon-dots-180c-dual-0.22um-filtration"
description: "A reusable, execution-grade protocol for hydrothermal synthesis of carbon dots (e.g., from citric acid and urea) that enforces a strict 180 °C reaction temperature to prevent PTFE liner deformation and mandates two non-optional 0.22 μm aqueous syringe filtrations — one post-reaction and one post-dialysis — as lab-mandated quality control steps."
version: "0.1.1"
tags:
  - "carbon-dots"
  - "hydrothermal-synthesis"
  - "lab-protocol"
  - "filtration"
  - "temperature-safety"
triggers:
  - "水热法合成碳点"
  - "碳点制备步骤"
  - "180度反应釜限制"
  - "必须两次0.22微米过滤"
  - "柠檬酸尿素体系执行细则"
---

# hydrothermal-synthesis-carbon-dots-180c-dual-0.22um-filtration

A reusable, execution-grade protocol for hydrothermal synthesis of carbon dots (e.g., from citric acid and urea) that enforces a strict 180 °C reaction temperature to prevent PTFE liner deformation and mandates two non-optional 0.22 μm aqueous syringe filtrations — one post-reaction and one post-dialysis — as lab-mandated quality control steps.

## Prompt

# Goal
Generate a fully executable, step-by-step laboratory procedure for hydrothermal synthesis of carbon dots using user-specified precursors (e.g., citric acid + urea), strictly adhering to thermal hardware limits and dual-filtration quality gates.

# Constraints & Style
- Reaction temperature MUST be exactly 180 °C — no higher, no rounding, no approximation; state "180 °C" unambiguously in all references.
- Hold time at 180 °C MUST default to 4 h unless explicitly overridden by user; do not suggest >4 h without confirmation.
- Two mandatory 0.22 μm aqueous-phase syringe filtrations are required: first immediately after cooling and opening the reactor (to remove particulates and PTFE debris), second after dialysis and before final storage (as final sterility/purity gate).
- Specify consumables precisely: "0.22 μm hydrophilic PVDF syringe filter", "MWCO 500 Da cellulose ester dialysis tubing", "15 mL polypropylene centrifuge tube", "brown glass HPLC vial for storage".
- Include operator actions verbatim where critical: "vacuum-filter using a 10 mL glass syringe", "discard first 0.5 mL filtrate", "rinse filter housing with 0.5 mL DI water and collect rinse in same vial", "label vial with: 'CDs-<YYYYMMDD>-BATCH#-F2'".
- Never omit unit symbols (e.g., always write "180 °C", "4 h", "0.22 μm", "15 mL") or use ambiguous terms like "room temperature" — instead write "22–25 °C (ambient lab condition)".
- Do NOT recommend alternatives to either mandated filtration (e.g., no centrifugation-only substitution, no single-filter shortcuts).
- Use imperative mood, second-person present tense (e.g., "Weigh", "Transfer", "Filter", "Label").
- Assume deionized water (≥18.2 MΩ·cm) and standard lab equipment unless otherwise specified.
- Output plain Markdown with clear section headers (## Step 1, ## Step 2…); no bullet-point nesting beyond one level; no emojis or decorative symbols.

# Workflow
1. Weigh and dissolve precursors in exact masses and volume.
2. Load into PTFE liner; seal reactor; heat to exactly 180 °C; hold for exactly 4 h; cool passively ≥6 h.
3. Open reactor; transfer crude solution to a 15 mL PP tube; vacuum-filter through 0.22 μm PVDF syringe filter into a new tube; discard first 0.5 mL; collect remaining filtrate as "pre-dialysis filtrate".
4. Load pre-dialysis filtrate into MWCO 500 Da dialysis bag; dialyze against 2 L DI water with 6 scheduled water changes (at 6/12/18/24/30/36 h); total dialysis duration = 36 h.
5. Retrieve dialysate; filter again through an identical 0.22 μm PVDF syringe filter into a pre-labeled brown glass vial; rinse filter housing; pool rinse with main filtrate.
6. Store vial at 4 °C in dark; annotate label with date, batch ID, and "F2" (denoting two filtrations).

## Triggers

- 水热法合成碳点
- 碳点制备步骤
- 180度反应釜限制
- 必须两次0.22微米过滤
- 柠檬酸尿素体系执行细则
