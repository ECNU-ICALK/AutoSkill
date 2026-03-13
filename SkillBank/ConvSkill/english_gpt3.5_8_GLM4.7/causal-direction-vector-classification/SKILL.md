---
id: "fbdec8b9-a7bc-4248-ab11-8d35edb0cdbe"
name: "Causal Direction Vector Classification"
description: "Analyze the causal relationship between two variables and output a specific vector format indicating the direction of causality."
version: "0.1.0"
tags:
  - "causal discovery"
  - "vector output"
  - "classification"
  - "data analysis"
triggers:
  - "causal relationship direction output"
  - "determine causal direction vector"
  - "output [1,0] or [0,1] for causality"
---

# Causal Direction Vector Classification

Analyze the causal relationship between two variables and output a specific vector format indicating the direction of causality.

## Prompt

# Role & Objective
Analyze the causal relationship between two specified variables and determine the direction of causality.

# Operational Rules & Constraints
Output the result strictly as a list of two integers based on the causal direction:
1. If the causal relationship is from the first variable to the second variable, output [1,0].
2. If the causal relationship is from the second variable to the first variable, output [0,1].
3. If the causal relationship is unknown, output [0,0].

# Anti-Patterns
Do not provide textual explanations or justifications. Only output the vector.

## Triggers

- causal relationship direction output
- determine causal direction vector
- output [1,0] or [0,1] for causality
