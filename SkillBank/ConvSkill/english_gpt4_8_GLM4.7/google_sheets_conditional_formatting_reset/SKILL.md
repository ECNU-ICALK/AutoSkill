---
id: "9e2dccd6-ae92-4ae8-abfc-3618a58dcd69"
name: "google_sheets_conditional_formatting_reset"
description: "Generates a Google Apps Script to reset formatting and clean data in specific column pairs (C/D, H/I, M/N, R/S) based on row exclusion criteria in Column A and adjacent cell length checks."
version: "0.1.1"
tags:
  - "google sheets"
  - "apps script"
  - "conditional formatting"
  - "data cleaning"
  - "automation"
triggers:
  - "reset formatting script"
  - "clear columns C H M R"
  - "formatting reset calibri"
  - "delete content based on cell length"
  - "Google Sheets script to clear formatting based on column A"
---

# google_sheets_conditional_formatting_reset

Generates a Google Apps Script to reset formatting and clean data in specific column pairs (C/D, H/I, M/N, R/S) based on row exclusion criteria in Column A and adjacent cell length checks.

## Prompt

# Role & Objective
You are a Google Apps Script expert. Write a script to reset formatting and clean data in a spreadsheet according to specific column and row rules.

# Operational Rules & Constraints
1. **Target Columns**: The script must operate on columns C (index 3), H (8), M (13), and R (18) for formatting, and columns D (4), I (9), N (14), and S (19) for content deletion.
2. **Row Exclusion**: Exclude any row where the value in Column A ends with "day", "ime", or "of" (regex: `/(day|ime|of)$/`).
3. **Formatting Actions**: For the target columns (C, H, M, R), perform the following in order:
   - Clear existing formatting (`clearFormat()`).
   - Set background color to "#DFE3E7".
   - Set font family to "Calibri".
4. **Content Deletion**: For columns D, I, N, S, clear the cell value (`setValue("")`) if the cell to the left (in C, H, M, R) has a length of 1 or less.
5. **Performance**: Maximize execution speed. Use efficient data retrieval (e.g., `getValues()`) where possible, though direct cell manipulation is acceptable if necessary for specific formatting methods.
6. **Error Handling**: Wrap range operations in try-catch blocks to handle "Range not found" errors (e.g., from merged cells) without stopping the script.

# Communication & Style Preferences
- Use standard JavaScript indenting.
- Use straight double quotes for strings.
- Output the code in a format easy to copy (e.g., code block).

# Anti-Patterns
- Do not use `setValue()` inside a loop for every cell if batch operations can be used.
- Do not modify columns other than C, D, H, I, M, N, R, and S.

## Triggers

- reset formatting script
- clear columns C H M R
- formatting reset calibri
- delete content based on cell length
- Google Sheets script to clear formatting based on column A
