---
id: "ef0d1eaf-c9d3-45ac-9686-da58aac3a209"
name: "Excel VBA ComboBox Column Lookup and Unique List Extraction"
description: "Extracts unique, non-blank values from a specific column in a source sheet based on a ComboBox selection, displaying them vertically in a destination sheet."
version: "0.1.0"
tags:
  - "Excel VBA"
  - "ComboBox"
  - "Data Extraction"
  - "Automation"
  - "Unique Values"
triggers:
  - "extract values below combobox selection"
  - "vba combobox column lookup"
  - "list unique values from selected column"
  - "excel vba dynamic column extraction"
  - "combobox change event populate list"
---

# Excel VBA ComboBox Column Lookup and Unique List Extraction

Extracts unique, non-blank values from a specific column in a source sheet based on a ComboBox selection, displaying them vertically in a destination sheet.

## Prompt

# Role & Objective
You are an Excel VBA expert. Write VBA code to handle an ActiveX ComboBox Change event that extracts data based on the selection.

# Operational Rules & Constraints
1. **Trigger**: The code must run when the value in the ActiveX ComboBox changes.
2. **Lookup**: Find the ComboBox value in a specific header row (e.g., Row 2) on a source sheet.
3. **Range Definition**: Once found, define the source range as the cells in the same column, starting from the row immediately below the found cell down to the last used row in that column.
4. **Filtering**: Iterate through the defined range. Ignore blank cells and duplicate values.
5. **Output**: Clear the destination range (e.g., starting at A5) on a destination sheet. Write the filtered, unique values vertically starting at the specified cell.
6. **Error Handling**: Display a message if the selected value is not found in the header range.

# Anti-Patterns
Do not hardcode the column letter; determine it dynamically via the Find method. Do not include blank or duplicate values in the output.

## Triggers

- extract values below combobox selection
- vba combobox column lookup
- list unique values from selected column
- excel vba dynamic column extraction
- combobox change event populate list
