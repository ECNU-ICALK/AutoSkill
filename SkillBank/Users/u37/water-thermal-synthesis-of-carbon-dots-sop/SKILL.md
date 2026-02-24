---
id: "79bdf0df-42c8-4960-b7ff-6c084d918285"
name: "water-thermal-synthesis-of-carbon-dots-sop"
description: "A fully executable, safety-critical standard operating procedure for hydrothermal synthesis of carbon dots using citric acid–urea, strictly constrained to ≤180 °C reaction temperature and mandating 0.22 μm filtration as the final, non-omissible purification step."
version: "0.1.0"
tags:
  - "carbon-dots"
  - "hydrothermal-synthesis"
  - "sop"
  - "lab-safety"
  - "nanomaterials"
triggers:
  - "写一个水热法合成碳点的可执行步骤"
  - "生成碳点合成标准操作流程"
  - "细化到实验室可直接执行的合成方案"
  - "制定180度上限的碳点水热SOP"
  - "强制0.22微米过滤的碳点制备流程"
---

# water-thermal-synthesis-of-carbon-dots-sop

A fully executable, safety-critical standard operating procedure for hydrothermal synthesis of carbon dots using citric acid–urea, strictly constrained to ≤180 °C reaction temperature and mandating 0.22 μm filtration as the final, non-omissible purification step.

## Prompt

# Goal
Generate a lab-ready, step-by-step Standard Operating Procedure (SOP) for hydrothermal synthesis of carbon dots (CDs) from citric acid and urea — with zero tolerance for temperature excursions above 180 °C, and with 0.22 μm membrane filtration explicitly required as the final, mandatory purification and quality-control step.

# Constraints & Style
- Temperature: Absolute maximum = 180.0 °C; no rounding or approximation — if equipment cannot hold ±0.5 °C at 180 °C, default to 179.5 °C. Preheating and ramping must be specified (e.g., preheat oven to 175 °C, then ramp to 180.0 °C at ≤3 °C/min).
- Reactor filling: Max 65% volume capacity (not 70%) to prevent PTFE liner deformation under thermal expansion.
- Cooling: Must specify natural cooling duration (≥12 h to ambient), with explicit prohibition of forced cooling (water/air blast).
- Filtration: 0.22 μm aqueous syringe filter (PVDF preferred) is non-optional — it must appear as Step 5.③, labeled "Mandatory final filtration", and include filter type, orientation (negative pressure), and acceptance criterion (e.g., flow rate >2 mL/min).
- Language: Use imperative, present-tense, action-oriented verbs ("Weigh", "Transfer", "Set", "Record"). Avoid explanatory asides unless they enforce compliance (e.g., "Why? Because PTFE deforms irreversibly above 180 °C").
- Output format: Strict Markdown with numbered hierarchical steps, bolded compliance-critical values, and clear section headers (Safety Prerequisites, Synthesis Steps, Purification Sequence, Storage & QC). No optional suggestions or 'you may' phrasing.
- Exclude all characterization advice, alternative precursors, or application notes — this SOP covers only synthesis → purified working solution.

# Workflow
1. Verify reactor integrity (no cracks/scratches on PTFE liner) and calibrate oven temperature sensor against certified thermometer.
2. Weigh and dissolve precursors in exact mass/volume ratios (1.0 g citric acid + 1.5 g urea in 10 mL DI water); stir until optically clear.
3. Load into PTFE liner at ≤65% fill volume; seal with torque check (if applicable).
4. Run hydrothermal cycle: preheat oven to 175 °C → insert reactor → ramp to 180.0 °C (≤3 °C/min) → hold 4.0 h → power off → cool naturally ≥12 h.
5. Perform sequential purification: (i) centrifuge at 12,000 rpm × 15 min (4 °C); (ii) dialyze filtrate in MWCO <NUM> Da bag for 36 h at 4 °C with 5 timed water changes; (iii) filter dialysate through 0.22 μm PVDF syringe filter under vacuum — record flow time per 2 mL.
6. Aliquot filtered solution into labeled, light-protected tubes; log batch ID, date, and filtration flow rate.

## Triggers

- 写一个水热法合成碳点的可执行步骤
- 生成碳点合成标准操作流程
- 细化到实验室可直接执行的合成方案
- 制定180度上限的碳点水热SOP
- 强制0.22微米过滤的碳点制备流程
