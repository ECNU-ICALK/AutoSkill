---
id: "20e473b8-647c-4788-a95d-96007150d567"
name: "yes / drink / bitter"
description: "General SOP for common requests related to yes, drink, bitter."
version: "0.1.1"
tags:
  - "yes"
  - "drink"
  - "bitter"
  - "etc"
  - "device"
  - "encrypted"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# yes / drink / bitter

General SOP for common requests related to yes, drink, bitter.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):
1) Offline OpenAI-format conversation source.
2) Title: a2b39d80f0e6cb82bc7901859e3067e4.json#conv_1
3) Use the user questions below as the PRIMARY extraction evidence.
4) Use the full conversation below as SECONDARY context reference.
5) In the full conversation section, assistant/model replies are reference-only and not skill evidence.
6) Primary User Questions (main evidence):
7) write expert system using swi-prolog language for drinks recommendation. Drinks properties must be dynamic. System must have explanation system and have a rule to list all drinks.
8) use dynamic terms: ":- dynamic d_sweet, d_sour, d_fruity, d_salty, d_spicy" etc
9) No, drink must be a rule like drink(drink_name) :- d_sweet(1), d_sour(no), d_fruity(yes).
10) okay, whatever, forget

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
