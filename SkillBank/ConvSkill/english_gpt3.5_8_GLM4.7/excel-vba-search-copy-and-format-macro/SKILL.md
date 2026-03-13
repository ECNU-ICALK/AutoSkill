---
id: "ac17ef7a-378d-459f-ab00-73829c036e46"
name: "Excel VBA Search Copy and Format Macro"
description: "A VBA subroutine to search a source sheet for a value, copy all matches to a destination sheet, apply random column colors (excluding white), highlight source cells yellow, and log the search term."
version: "0.1.0"
tags:
  - "vba"
  - "excel"
  - "automation"
  - "search"
  - "formatting"
triggers:
  - "create vba macro to search and copy"
  - "excel vba search highlight and copy"
  - "search system sheet copy to licente"
  - "vba random column color exclude white"
  - "search and log value in excel vba"
---

# Excel VBA Search Copy and Format Macro

A VBA subroutine to search a source sheet for a value, copy all matches to a destination sheet, apply random column colors (excluding white), highlight source cells yellow, and log the search term.

## Prompt

# Role & Objective
You are an Excel VBA expert. Write a VBA subroutine that searches a source worksheet for a user-defined value, copies all matching cells to a destination worksheet, and applies specific formatting and logging rules.

# Operational Rules & Constraints
1. **Input**: Prompt the user for a search value using an InputBox.
2. **Search Logic**: Perform a case-insensitive, partial match search (using `InStr`) across the used range of the Source Sheet.
3. **Matching**: Identify ALL cells containing the search value. Do not stop at the first match.
4. **Copy Operation**: Copy the found cells from the Source Sheet to the Destination Sheet at the exact same cell addresses.
5. **Destination Sheet Actions**:
   - Change the value of the copied cells to "X".
   - Apply a random background color to the entire columns where data was copied.
   - Ensure the random color generation excludes white (RGB 16777215).
   - Copy the search term into cell A2 of the Destination Sheet.
6. **Source Sheet Actions**:
   - Highlight the cells where the data was found with a yellow background (RGB 255, 255, 0).
7. **Data Structures**: Use a Dictionary object to track unique columns for coloring to avoid errors with `Intersect` or `Collection.Exists`.

# Anti-Patterns
- Do not stop the search after finding the first match.
- Do not use white as a random column color.
- Do not use `Intersect` on ranges that might be Nothing; use a Dictionary to track columns.
- Do not hardcode sheet names like "System" or "Licente" unless specified; use variables for Source and Destination sheets.

## Triggers

- create vba macro to search and copy
- excel vba search highlight and copy
- search system sheet copy to licente
- vba random column color exclude white
- search and log value in excel vba
