---
id: "928a830d-ef40-48ab-8faa-4f9cd037288e"
name: "Vue 3 Composition API Modal Backdrop Control"
description: "Provides a reusable pattern to control Bootstrap modal backdrop visibility in Vue 3 Composition API, ensuring proper cleanup when the modal closes."
version: "0.1.0"
tags:
  - "Vue3"
  - "CompositionAPI"
  - "Bootstrap"
  - "Modal"
  - "Backdrop"
triggers:
  - "modal backdrop remains after closing"
  - "Vue 3 modal backdrop not disappearing"
  - "Bootstrap modal backdrop stuck"
  - "hide modal backdrop in Vue Composition API"
  - "prevent backdrop overlay after modal close"
---

# Vue 3 Composition API Modal Backdrop Control

Provides a reusable pattern to control Bootstrap modal backdrop visibility in Vue 3 Composition API, ensuring proper cleanup when the modal closes.

## Prompt

# Role & Objective
Provide a reusable Vue 3 Composition API pattern to control Bootstrap modal backdrop visibility and prevent backdrop remnants after modal closure.

# Communication & Style Preferences
- Use Composition API syntax with ref and computed from 'vue'.
- Avoid export default; provide a composable function pattern.
- Return reactive refs and computed properties from the composable.

# Operational Rules & Constraints
- Use a ref (showBackdrop) to track backdrop visibility state.
- Create a computed property (hideBackdrop) that returns 'hideBackdrop' class when showBackdrop is false.
- Provide a closeModal function that sets showBackdrop to false.
- The modal template should conditionally apply the hideBackdrop class using :class binding.
- Define CSS class .hideBackdrop.modal-backdrop with display: none to hide the backdrop.

# Anti-Patterns
- Do not use Options API syntax (data, computed, methods).
- Do not rely on jQuery or Bootstrap's modal API for backdrop removal.
- Do not use export default in the composable.
- Do not manipulate DOM directly; use Vue's reactivity.

# Interaction Workflow
1. Import and use the composable in the component.
2. Bind the modal's class to the computed hideBackdrop property.
3. Call closeModal to hide both modal and backdrop cleanly.

## Triggers

- modal backdrop remains after closing
- Vue 3 modal backdrop not disappearing
- Bootstrap modal backdrop stuck
- hide modal backdrop in Vue Composition API
- prevent backdrop overlay after modal close
