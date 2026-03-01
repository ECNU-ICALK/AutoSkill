---
id: "03e0f14f-3b51-4256-832d-e843dfa19fa9"
name: "training_log_sop"
description: "General SOP for generating or analyzing training logs, incorporating metrics like loss, accuracy, precision, recall, and max accuracy across epochs."
version: "0.1.1"
tags:
  - "training"
  - "sop"
  - "metrics"
  - "loss"
  - "accuracy"
  - "precision"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
  - "Use when generating training logs or metrics."
examples:
  - input: "Break this into best-practice, executable steps."
---

# training_log_sop

General SOP for generating or analyzing training logs, incorporating metrics like loss, accuracy, precision, recall, and max accuracy across epochs.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):

# Log Format Template
Generate or parse logs using the following structure, ensuring all relevant metrics are populated:
Epoch <CURRENT>/<TOTAL>
<STEPS>/<TOTAL_STEPS> [==============================] - <TIME>s <MS>ms/step - loss: <LOSS> - accuracy: <ACC> - precision: <PREC> - recall: <REC> - max_acc: <MAX_ACC> - val_loss: <VAL_LOSS> - val_accuracy: <VAL_ACC> - val_precision: <VAL_PREC> - val_recall: <VAL_REC> - val_max_acc: <VAL_MAX_ACC> - lr: <LR>

# Workflow Instructions
For each step, include:
1. Action
2. Checks
3. Failure rollback/fallback plan

# Output Format
For each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.
- Use when generating training logs or metrics.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
