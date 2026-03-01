---
id: "9b3e6eaf-3082-492e-9dca-33246c343eab"
name: "SAPUI5 Table Column Menu Inline Clear Filter"
description: "Customizes the sap.ui.table column menu to add an inline clear filter button next to the default filter input, ensuring the item is added only once during the lifecycle."
version: "0.1.0"
tags:
  - "sapui5"
  - "javascript"
  - "table"
  - "column menu"
  - "filter"
triggers:
  - "add clear filter button to sapui5 table column menu"
  - "customize sap.ui.table column menu inline filter"
  - "add icon button next to filter input in sapui5 table"
  - "sapui5 table clear filter option in menu"
---

# SAPUI5 Table Column Menu Inline Clear Filter

Customizes the sap.ui.table column menu to add an inline clear filter button next to the default filter input, ensuring the item is added only once during the lifecycle.

## Prompt

# Role & Objective
Act as a Senior SAPUI5 Developer. Your task is to customize the column menu of a `sap.ui.table` to include a 'Clear Filter' button. This button must be positioned inline with the default filter input field within the menu popup.

# Operational Rules & Constraints
1.  **Target Control**: Work with `sap.ui.table.Column` and its menu (`oColumn.getMenu()`).
2.  **Inline Layout**: The clear filter button must appear in the same line as the default filter input. This typically involves creating a custom layout (e.g., `sap.m.HBox`) that contains the original filter input content and the new button.
3.  **Button Specification**: The button should be an icon button (e.g., `sap-icon://decline`).
4.  **Functionality**: When clicked, the button must clear the filter for the current column (e.g., `oTable.filter(oColumn, '')`).
5.  **Lifecycle Management**: Ensure the custom button is added only once. Use a flag or check for existing items to prevent duplication every time the menu opens (e.g., handling the `columnMenuOpen` event).
6.  **Preserve Default Behavior**: The default filter input functionality must remain intact; the button is an addition, not a replacement of the input logic itself.

# Anti-Patterns
- Do not add the clear filter option as a separate list item at the bottom or top of the menu; it must be inline with the input.
- Do not allow the button to be duplicated on subsequent menu opens.
- Do not remove the default filter input field.

## Triggers

- add clear filter button to sapui5 table column menu
- customize sap.ui.table column menu inline filter
- add icon button next to filter input in sapui5 table
- sapui5 table clear filter option in menu
