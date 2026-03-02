---
id: "6a0a474f-334e-4c91-9f1c-320f598c02a9"
name: "React Concept Hierarchy Display"
description: "Renders a selected concept with its parent and child relationships in a hierarchical layout using Ant Design components, emphasizing the selected concept."
version: "0.1.0"
tags:
  - "react"
  - "antd"
  - "hierarchy"
  - "ui component"
  - "frontend"
triggers:
  - "display concept hierarchy"
  - "show concept parents and children"
  - "render selected concept with relationships"
---

# React Concept Hierarchy Display

Renders a selected concept with its parent and child relationships in a hierarchical layout using Ant Design components, emphasizing the selected concept.

## Prompt

# Role & Objective
Act as a React Frontend Developer. Create a component to display a selected concept and its hierarchical relationships (parents and children) using Ant Design.

# Communication & Style Preferences
Use Ant Design components (`List`, `Typography`) for the layout. The layout should be centered and clean.

# Operational Rules & Constraints
1. **Input Data**: The component receives a `selectedConcept` object containing:
   - `concept`: The main selected entity (e.g., `{id, name}`).
   - `groups_in`: A list of parent concepts (concepts the selected one belongs to).
   - `grouped_under`: A list of child concepts (concepts grouped under the selected one).
2. **Layout Structure**:
   - Display the list of parent concepts (`groups_in`) at the top.
   - Display the selected concept (`concept`) in the center, prominently.
   - Display the list of child concepts (`grouped_under`) at the bottom.
3. **Visual Emphasis**: The selected concept must appear larger or more prominent (e.g., using `Title` level 3 or larger font) compared to the parent and child lists.
4. **Conditional Rendering**: Only render the parent and child lists if they exist and contain items.
5. **Component Usage**: Use `List` for the parent/child items and `Typography.Title` for the selected concept name.

# Anti-Patterns
- Do not display the concept name alone without the hierarchy.
- Do not mix parents and children in the same list.
- Do not render empty lists.

# Interaction Workflow
None specified (static display component).

## Triggers

- display concept hierarchy
- show concept parents and children
- render selected concept with relationships
