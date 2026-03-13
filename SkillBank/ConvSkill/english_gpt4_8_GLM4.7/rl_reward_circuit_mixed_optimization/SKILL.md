---
id: "364f2105-6445-41ec-8b4b-84727d396a2a"
name: "rl_reward_circuit_mixed_optimization"
description: "Implements a reinforcement learning reward function for analog circuit design that handles mixed minimization/maximization objectives using normalized differences, while incorporating transistor saturation tracking to ensure stability."
version: "0.1.3"
tags:
  - "RL"
  - "reward function"
  - "circuit optimization"
  - "mixed objectives"
  - "transistor saturation"
  - "python"
  - "self"
  - "policy"
  - "action"
triggers:
  - "calculate reward function for reinforcement learning"
  - "RL reward condition with normalized difference"
  - "mixed optimization reward calculation"
  - "reward logic for transistor saturation"
  - "implement circuit environment reward function"
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# rl_reward_circuit_mixed_optimization

Implements a reinforcement learning reward function for analog circuit design that handles mixed minimization/maximization objectives using normalized differences, while incorporating transistor saturation tracking to ensure stability.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: ae325e3c206735467f9648f983310cdd.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) My Objective:
8) We aim to optimize the '7' objective performance metric values of 'area', 'power dissipation', 'DC gain', 'Slew rate', '3db frequency', 'Unity gain bandwidth', and 'Phase margin' (multi-objectives) of a pre-determined two stage operational amplifier circuit topology. We need to optimally configure/tune the design device parameters (device dimensions and values, as variables) such as transistor dimensions ['L1', 'L3', 'L5', 'L6', 'L7', 'W1', 'W3', 'W5', 'W6', 'W7'], Bias currents ['Ib'], Bias voltages ['Vb'], and values of the passive devices ['Cc', 'Cl', 'Rp'] associated in the circuit design, in a such a way that the resulting design satisfies the predetermined performance measures (design specifications). In this overall construction of optimization process, the pre-determined performance measures are considered as constraints as well as target optimization metrics to configure the optimized design device parameter values.
9) For my objectives, I need to implement the reinforcement learning (RL) code with multiple output heads Graph neural networks on multigraphs, GNN is embedded by the technique of hybrid MPNN-RGAT architecture that contains the message passing attention mechanism. Here GNN is with in the agent the action and rewards are performed from the following requirement, for this requirement suggest me the best optimization techniques that take actions and generate rewards and to update the parameters.
10) Environment: My environment is the Cadence virtuoso simulator, where I am simulating the pre-designed fixed circuit topology. I am accessing the simulator available in the local server through the OCEAN skill command controlled by python programming. The environment gets the input variables for the design device parameters ['L1', 'L3', 'L5', 'L6', 'L7', 'W1', 'W3', 'W5', 'W6', 'W7', 'Ib', 'Cc'] from the agent and gives the output performance metrics ['area', 'power dissipation', 'DC gain', 'Slew rate', '3db frequency', 'Unity gain bandwidth', 'Phase margin'] corresponding to the given input variables. Circuit topology is fixed, only the design device parameters present in the schematic are variables to be optimally configure to met the desired output performance metrics.

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- calculate reward function for reinforcement learning
- RL reward condition with normalized difference
- mixed optimization reward calculation
- reward logic for transistor saturation
- implement circuit environment reward function
- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
