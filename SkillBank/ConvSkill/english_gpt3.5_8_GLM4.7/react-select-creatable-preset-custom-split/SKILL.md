---
id: "6e8a9370-4e26-40b8-b046-9e1d36d70cca"
name: "React-Select Creatable Preset/Custom Split"
description: "Implement a react-hook-form Controller with React-Select Creatable to separate selected options into 'preset' and 'custom' arrays, handling creation and removal logic within the onChange handler."
version: "0.1.0"
tags:
  - "react"
  - "react-hook-form"
  - "react-select"
  - "form-logic"
  - "data-transformation"
triggers:
  - "react-select creatable split preset custom"
  - "react-hook-form controller separate default and new options"
  - "react-select output structure preset custom array"
  - "handle removal in onChange react-select creatable"
---

# React-Select Creatable Preset/Custom Split

Implement a react-hook-form Controller with React-Select Creatable to separate selected options into 'preset' and 'custom' arrays, handling creation and removal logic within the onChange handler.

## Prompt

# Role & Objective
Act as a React Frontend Engineer. Your task is to implement a form field using `react-hook-form` and `react-select` (Creatable) that separates selected values into two distinct arrays: `preset` (default options) and `custom` (user-created options).

# Operational Rules & Constraints
1. Use the `Controller` component from `react-hook-form` to wrap the select component.
2. Use the `Creatable` feature from `react-select`.
3. The form value must be an object with the structure: `{ preset: [...], custom: [...] }`.
4. Implement logic to distinguish between default options and user-created options to populate the correct array.
5. Handle the creation of new options by adding them to the `custom` array.
6. Handle the removal of options within the `onChange` handler. Do not rely on non-existent props like `onRemoveOption`. Ensure removal updates the correct array (`preset` or `custom`).
7. The `value` prop for the Select component should be a concatenation of the `preset` and `custom` arrays.

# Anti-Patterns
- Do not use props that do not exist in the library (e.g., `onRemoveOption`).
- Do not mix preset and custom options in a single array in the final output.

## Triggers

- react-select creatable split preset custom
- react-hook-form controller separate default and new options
- react-select output structure preset custom array
- handle removal in onChange react-select creatable
