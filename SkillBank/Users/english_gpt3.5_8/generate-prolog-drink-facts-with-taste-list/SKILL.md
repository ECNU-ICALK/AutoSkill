---
id: "3d0cd35e-15b8-43f5-a1b3-494287463405"
name: "Generate Prolog drink facts with taste list"
description: "Generates SWI-Prolog facts for drinks in the format drink(Name, [Tastes]) :- yes(Taste1), yes(Taste2), ... based on provided drink names and their taste descriptions."
version: "0.1.0"
tags:
  - "prolog"
  - "drinks"
  - "taste"
  - "facts"
  - "generation"
triggers:
  - "generate prolog drink facts"
  - "write drink facts in prolog"
  - "create drink(Name, [Tastes]) :- yes(Taste) facts"
  - "format drinks as prolog rules with taste list"
  - "output prolog facts for drinks with tastes"
---

# Generate Prolog drink facts with taste list

Generates SWI-Prolog facts for drinks in the format drink(Name, [Tastes]) :- yes(Taste1), yes(Taste2), ... based on provided drink names and their taste descriptions.

## Prompt

# Role & Objective
Generate SWI-Prolog facts for drinks using the exact format: drink(Name, [Tastes]) :- yes(Taste1), yes(Taste2), ... Each drink fact must include a list of tastes in the head and corresponding yes/1 goals in the body. Do not include any comments starting with %.

# Communication & Style Preferences
- Output only the Prolog facts, one per line.
- Use lowercase for drink names and tastes.
- Separate facts with a blank line.

# Operational Rules & Constraints
- The head must be drink(Name, [Taste1, Taste2, ...]).
- The body must list yes(Taste) for each taste in the list.
- Ensure the order of tastes in the list matches the order in the body.
- Do not include any explanatory text or comments.

# Anti-Patterns
- Do not add comments or annotations.
- Do not use dynamic declarations or additional predicates.
- Do not include any formatting beyond the facts themselves.

# Interaction Workflow
1. Receive a list of drinks with their taste descriptions.
2. For each drink, create a fact in the specified format.
3. Output all facts consecutively.

## Triggers

- generate prolog drink facts
- write drink facts in prolog
- create drink(Name, [Tastes]) :- yes(Taste) facts
- format drinks as prolog rules with taste list
- output prolog facts for drinks with tastes
