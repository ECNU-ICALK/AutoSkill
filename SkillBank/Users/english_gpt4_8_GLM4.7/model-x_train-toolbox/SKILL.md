---
id: "4ca96640-d373-4e3b-b689-06b9df34cbc9"
name: "model / x_train / toolbox"
description: "General SOP for common requests related to model, x_train, toolbox."
version: "0.1.0"
tags:
  - "model"
  - "x_train"
  - "toolbox"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# model / x_train / toolbox

General SOP for common requests related to model, x_train, toolbox.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) 49828a0782722eda16419c3076bbdd6d.json#conv_1
2) Use the user questions below as the PRIMARY extraction evidence
3) Use the full conversation below as SECONDARY context reference
4) In the full conversation section, assistant/model replies are reference-only and not skill evidence
5) Primary User Questions (main evidence
6) main.py
7) import matplotlib.pyplot as plt
8) import seaborn as sns
9) import numpy as np
10) from sklearn.ensemble import RandomForestClassifier

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
