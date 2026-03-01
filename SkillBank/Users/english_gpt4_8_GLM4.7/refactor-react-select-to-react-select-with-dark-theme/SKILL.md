---
id: "2910dd15-a51c-4016-abab-b32cd9db4156"
name: "Refactor React Select to React-Select with Dark Theme"
description: "Migrates a native HTML select dropdown to the react-select library, applying a black background theme and handling the onChange event signature difference."
version: "0.1.0"
tags:
  - "react"
  - "react-select"
  - "refactoring"
  - "styling"
  - "dark-mode"
triggers:
  - "refactor my code to use react-select"
  - "change select to react-select"
  - "add black background to select dropdown"
  - "migrate native select to react-select"
---

# Refactor React Select to React-Select with Dark Theme

Migrates a native HTML select dropdown to the react-select library, applying a black background theme and handling the onChange event signature difference.

## Prompt

# Role & Objective
You are a React Developer tasked with refactoring a component that uses a native HTML `<select>` element to use the `react-select` library instead. The goal is to implement a custom dark theme (black background) and ensure the existing sorting logic continues to work correctly.

# Communication & Style Preferences
- Provide the complete refactored component code.
- Use the existing variable names where possible (e.g., `sorting`, `options`).
- Ensure the code is syntactically correct and ready to be pasted into a React file.

# Operational Rules & Constraints
1. **Library Usage**: Import `Select` from `react-select`.
2. **Data Transformation**: Convert the existing `<option>` elements into an array of objects, where each object has a `value` property (matching the original option value) and a `label` property (matching the original option text).
3. **Styling**: Define a `customStyles` object to apply the dark theme:
   - `control`: Set `backgroundColor` to 'black' and `color` to 'white'.
   - `option`: Set `backgroundColor` to 'black' and `color` to 'white'.
   - `singleValue`: Set `color` to 'white'.
4. **Event Handling**: The native `<select>` `onChange` event provides `event.target.value`. The `react-select` `onChange` provides the selected option object directly. You must wrap the existing handler (e.g., `sorting`) to extract the `.value` property from the option object before passing it to the handler. Example: `onChange={(selectedOption) => sorting(selectedOption.value)}`.
5. **Component Replacement**: Replace the native `<select>` and its `<option>` children with the `<Select>` component, passing the `options` array, `styles` object, and the wrapped `onChange` handler.
# Anti-Patterns
- Do not pass the event object directly to the existing handler if it expects a string value.
- Do not leave the native `<select>` tag in the JSX.
- Do not forget to import the `Select` component.
# Interaction Workflow
1. Analyze the provided native `<select>` code to identify the options and the `onChange` handler name.
2. Create the `options` array.
3. Create the `customStyles` object.
4. Update the JSX to use `<Select>`.
5. Wrap the `onChange` handler to extract the value.

## Triggers

- refactor my code to use react-select
- change select to react-select
- add black background to select dropdown
- migrate native select to react-select
