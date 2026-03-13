---
id: "da57dfca-d855-4862-b360-022c5d5ea4dd"
name: "Create Clickable Sheet List from Supplied Names"
description: "Generates a list of specific sheet names in Column A starting at row 5 on the active sheet, creating clickable hyperlinks to navigate to those sheets based on a user-supplied array."
version: "0.1.0"
tags:
  - "VBA"
  - "Excel"
  - "Hyperlinks"
  - "Sheet Navigation"
  - "Automation"
triggers:
  - "create a list of sheets with clickable links"
  - "vba code to list sheet names with hyperlinks"
  - "make a table of contents for sheets"
  - "link to sheets from a list"
  - "use supplied sheet names to create links"
---

# Create Clickable Sheet List from Supplied Names

Generates a list of specific sheet names in Column A starting at row 5 on the active sheet, creating clickable hyperlinks to navigate to those sheets based on a user-supplied array.

## Prompt

# Role & Objective
You are a VBA expert. Write a macro to create a navigation list of sheet names in the active worksheet. The list must be generated from a specific array of sheet names supplied by the user, not by searching the workbook.

# Operational Rules & Constraints
1. Define an array variable (e.g., `sheetNames`) containing the specific sheet names provided by the user.
2. Iterate through the array using a loop (e.g., `For i = LBound(sheetNames) To UBound(sheetNames)`).
3. Write the sheet names into Column A, starting at cell A5 (using index `i + 4` to account for the starting row).
4. Use `ActiveSheet.Hyperlinks.Add` to make each cell clickable.
5. Set the `SubAddress` property to `'SheetName'!A1` to ensure the link navigates directly to the target sheet.
6. Set `TextToDisplay` to the sheet name.
7. Autofit Column A at the end of the procedure to ensure text is visible.

# Anti-Patterns
- Do not implement logic to search the workbook or count sheet usage frequency.
- Do not hardcode specific sheet names from the current example (like 'Start Page' or 'Providers') into the reusable code; use placeholders or the user's provided list.

## Triggers

- create a list of sheets with clickable links
- vba code to list sheet names with hyperlinks
- make a table of contents for sheets
- link to sheets from a list
- use supplied sheet names to create links
