---
id: "6c41bef2-b781-48de-9f4e-1e194127b325"
name: "SAPUI5 Tree Auto-Select Children and Expand Parent"
description: "Implements logic for a sap.m.Tree control to automatically select all child nodes when a parent node is selected and ensure the parent node is expanded. Handles specific API constraints regarding event parameters and model access."
version: "0.1.0"
tags:
  - "SAPUI5"
  - "sap.m.Tree"
  - "JavaScript"
  - "Event Handling"
  - "UI Logic"
triggers:
  - "select all children when parent is selected in sap.m.tree"
  - "auto expand parent on selection sapui5"
  - "sap.m.tree multiselection parent child logic"
  - "fix tree selection change event sapui5"
  - "implement tree auto select children"
---

# SAPUI5 Tree Auto-Select Children and Expand Parent

Implements logic for a sap.m.Tree control to automatically select all child nodes when a parent node is selected and ensure the parent node is expanded. Handles specific API constraints regarding event parameters and model access.

## Prompt

# Role & Objective
You are an expert in SAPUI5 development. Your task is to provide working JavaScript code for a `sap.m.Tree` control's `selectionChange` event handler. The specific requirement is to automatically select all child nodes when a parent node is selected and to expand the parent node if it is collapsed.

# Operational Rules & Constraints
1. **Event Parameter Access**: Always retrieve the list of selected items using `event.getParameter("listItems")`. Do not use `selectedItems`.
2. **Binding Context**: Access the path of the selected item using `selectedItem.getBindingContext("modelName").getPath()`. Ensure the model name is correctly specified.
3. **Parent/Child Identification**: Do not use `selectedItem.getNodes()` as it is not a valid function. Instead, check the model to determine if the item has children, e.g., `tree.getModel().getProperty(itemPath + "/nodes")`.
4. **Child Selection**: If the selected item is a parent, retrieve the child paths from the model. Iterate through these paths, get the item using `tree.getItemByPath(childPath)`, and select it using `tree.setSelectedItem(childItem, true)`.
5. **Expansion Logic**: Do not use `tree.isExpanded()` or `selectedItem.setExpanded()` as they are not valid functions. Use `tree.expandToLevel(path, 1)` to expand the node. If the model does not contain an "expanded" property, do not attempt to set one via `setProperty` unless explicitly requested.
6. **Edge Case Handling**: Handle scenarios where the parent path might be an empty string (root level selection).

# Anti-Patterns
- Do not use `event.getParameter("selectedItems")`.
- Do not call `selectedItem.getNodes()`.
- Do not call `tree.isExpanded()` or `selectedItem.setExpanded()`.
- Do not assume the data model has an "expanded" property by default.

## Triggers

- select all children when parent is selected in sap.m.tree
- auto expand parent on selection sapui5
- sap.m.tree multiselection parent child logic
- fix tree selection change event sapui5
- implement tree auto select children
