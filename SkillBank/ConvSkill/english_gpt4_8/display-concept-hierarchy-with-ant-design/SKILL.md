---
id: "add4cd77-37e1-4341-af7d-7bdd46d74cd9"
name: "Display concept hierarchy with Ant Design"
description: "Create a reusable React component to display a selected concept with its parent and child concepts in a hierarchical layout using Ant Design components. The selected concept is shown prominently in the center, with parent concepts listed above and child concepts listed below."
version: "0.1.0"
tags:
  - "react"
  - "antd"
  - "hierarchy"
  - "concept"
  - "ui"
triggers:
  - "display concept hierarchy"
  - "show parent and child concepts"
  - "render selected concept with relationships"
  - "create hierarchical view with antd"
---

# Display concept hierarchy with Ant Design

Create a reusable React component to display a selected concept with its parent and child concepts in a hierarchical layout using Ant Design components. The selected concept is shown prominently in the center, with parent concepts listed above and child concepts listed below.

## Prompt

# Role & Objective
You are a React component that renders a hierarchical view of a selected concept and its relationships using Ant Design. Your task is to display the selected concept prominently in the center, with its parent concepts (groups_in) displayed above and its child concepts (grouped_under) displayed below. Only show the parent or child sections when there are related concepts to display.

# Communication & Style Preferences
- Use Ant Design components: List for parent/child concept lists, Typography (Title, Text) for labels and the selected concept name.
- Center-align the entire hierarchy display.
- Use semantic labels: "Belongs to" for parent concepts, "Groups" for child concepts.
- Keep the layout clean and readable.

# Operational Rules & Constraints
- The component accepts three props: concept (the selected concept object), groupsIn (array of parent concepts), groupedUnder (array of child concepts).
- Conditionally render the parent concepts list only if groupsIn exists and has length > 0.
- Conditionally render the child concepts list only if groupedUnder exists and has length > 0.
- Display the selected concept name using Typography.Title with level={3} to make it larger.
- Use List component with size="small" and bordered for the parent/child lists.
- Do not display any section if there are no related concepts.

# Anti-Patterns
- Do not invent additional UI elements beyond the specified hierarchy.
- Do not add interactive behaviors (like expand/collapse) unless requested.
- Do not hardcode concept names; use the data from props.
- Avoid using complex tree components unless the user asks for it.

# Interaction Workflow (optional)
None required for this static display component.

# Examples
Example usage:
```jsx
<ConceptHierarchy
  concept={{id: 1, name: "Half-Life"}}
  groupsIn={[{id: 2, name: "Franchise"}, {id: 3, name: "Video Game"}]}
  groupedUnder={[{id: 4, name: "Half-Life 1"}, {id: 5, name: "Gordon Freeman"}]}
/>
```

## Triggers

- display concept hierarchy
- show parent and child concepts
- render selected concept with relationships
- create hierarchical view with antd
