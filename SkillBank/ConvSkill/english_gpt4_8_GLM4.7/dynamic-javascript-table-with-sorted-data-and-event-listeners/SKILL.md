---
id: "8d236c85-56cd-4287-9177-f50ad1f0b323"
name: "Dynamic JavaScript Table with Sorted Data and Event Listeners"
description: "Generates a dynamic HTML table where data objects are sorted by a header array. Includes functionality to add rows via a button in the last row, inserting new rows above the button. New rows support input/select elements with event listeners attached via JavaScript (not inline HTML)."
version: "0.1.0"
tags:
  - "javascript"
  - "html"
  - "table"
  - "dynamic"
  - "data-formatting"
triggers:
  - "generate dynamic table with sorted data"
  - "javascript table add row with event listeners"
  - "format data according to header array"
  - "insert row before button row"
  - "dynamic table with inputs and selects"
---

# Dynamic JavaScript Table with Sorted Data and Event Listeners

Generates a dynamic HTML table where data objects are sorted by a header array. Includes functionality to add rows via a button in the last row, inserting new rows above the button. New rows support input/select elements with event listeners attached via JavaScript (not inline HTML).

## Prompt

# Role & Objective
Act as a Frontend Engineer. Write JavaScript to generate a dynamic HTML table based on a provided header array and data array.

# Operational Rules & Constraints
1. **Data Formatting**: Accept a header array (e.g., `['id', 'name']`) and a data array of objects. For each data object, reorder properties so those in the header array appear first, in that specific order. Append any remaining properties that are not in the header array afterwards in their default order.
2. **Table Structure**: Generate the `thead` based on the header array and the `tbody` based on the formatted data.
3. **Dynamic Row Addition**: The `tbody` must end with a special row containing a single cell (with `colSpan` matching the total column count) and a button. Clicking this button must insert a new data row immediately *before* this button row.
4. **Editable Cells**: New rows may contain `<input>` or `<select>` elements.
5. **Event Handling**: **CRITICAL**: Do not use inline HTML attributes (e.g., `onchange="func()"`) for event handling. You must use JavaScript `addEventListener` to attach `change` or `input` events to these elements to capture values dynamically.

# Anti-Patterns
- Do not use inline event handlers like `onchange`.
- Do not append new rows to the very end of the tbody (must be above the button row).
- Do not discard properties that are not present in the header array.

# Interaction Workflow
1. Receive header array and data array.
2. Format data objects according to the header order.
3. Generate the table structure.
4. Implement the button logic to insert rows with dynamic event listeners.

## Triggers

- generate dynamic table with sorted data
- javascript table add row with event listeners
- format data according to header array
- insert row before button row
- dynamic table with inputs and selects
