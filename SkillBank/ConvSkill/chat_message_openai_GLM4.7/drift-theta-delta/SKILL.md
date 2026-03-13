---
id: "bc859ad3-272f-453f-ae5d-00c6b55dc2d6"
name: "drift / theta / delta"
description: "General SOP for common requests related to drift, theta, delta."
version: "0.1.0"
tags:
  - "drift"
  - "theta"
  - "delta"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# drift / theta / delta

General SOP for common requests related to drift, theta, delta.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) section{Near-Reference Restricted Adaptation
2) label{sec:near_reference_restricted
3) We study near-reference adaptation in which a strong reference checkpoint $\theta_0$ is adapted to improve supervised fine-tuning (SFT
4) while limiting functional drift from the reference model
5) Let $\pi_\theta(\cdot|x)$ denote the model distribution. We measure drift by
6) begin{equation
7) D_{\mathrm{ref}}(\theta
8) mathbb{E}_{x}\Big[\mathrm{KL}\big(\pi_{\theta}(\cdot|x)\ \|\ \pi_{\theta_0}(\cdot|x)\big)\Big
9) label{eq:dref_def
10) end{equation

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
