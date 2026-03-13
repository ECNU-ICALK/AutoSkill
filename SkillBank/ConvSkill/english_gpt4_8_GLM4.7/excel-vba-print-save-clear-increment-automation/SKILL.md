---
id: "975d5f38-0856-4d04-bacf-4e7f7408e662"
name: "Excel VBA Print-Save-Clear-Increment Automation"
description: "Generates VBA code for an Excel button that executes a specific workflow: printing 3 copies with unique cell marks, saving a copy with a dynamic filename, clearing a data range, incrementing a counter, displaying a message, and closing the workbook."
version: "0.1.0"
tags:
  - "vba"
  - "excel"
  - "automation"
  - "printing"
  - "macro"
triggers:
  - "vba code for button1 on sheet1"
  - "print 3 copies with x mark in specific cells"
  - "save copy of file in path C:\\avize"
  - "clear cells value form range B16:G45"
  - "change value from cell D2 to D2+1"
---

# Excel VBA Print-Save-Clear-Increment Automation

Generates VBA code for an Excel button that executes a specific workflow: printing 3 copies with unique cell marks, saving a copy with a dynamic filename, clearing a data range, incrementing a counter, displaying a message, and closing the workbook.

## Prompt

# Role & Objective
You are a VBA developer. Write a VBA subroutine for a button on Sheet1 that executes the following specific sequence of actions.

# Operational Rules & Constraints
1. **Printing Loop**: Implement a loop that runs 3 times to print the file:
   - Iteration 1: Place an 'x' mark in cell C58, print the file, then clear the 'x' from C58.
   - Iteration 2: Place an 'x' mark in cell D59, print the file, then clear the 'x' from D59.
   - Iteration 3: Place an 'x' mark in cell E60, print the file, then clear the 'x' from E60.
2. **Save Copy**: Save a copy of the file to the path `C:\avize\`. The filename must be constructed using the values from cell F4 and cell D2.
3. **Clear Data**: Clear the values in the cell range B16:G45.
4. **Increment Value**: Change the value of cell D2 to be equal to D2 + 1.
5. **Message Box**: Display a message box with the text "urmatorul aviz are valoarea" followed by the new value of D2.
6. **Save and Close**: Save the current file and close the workbook automatically.
7. **Syntax**: Use straight double quotes (`"`) for strings and standard apostrophes (`'`) for comments to avoid syntax errors.

# Anti-Patterns
- Do not use smart quotes or curly apostrophes.
- Do not omit the final save and close steps.
- Do not forget to clear the 'x' marks after each print iteration.

## Triggers

- vba code for button1 on sheet1
- print 3 copies with x mark in specific cells
- save copy of file in path C:\avize
- clear cells value form range B16:G45
- change value from cell D2 to D2+1
