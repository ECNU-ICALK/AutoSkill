---
id: "46e6c38e-0fc9-407a-bd6d-88d7aa4d90f3"
name: "Excel VBA File Renaming based on Hyperlinks and Status"
description: "A VBA macro to rename files linked in an Excel sheet by adding a 'PRO' prefix, based on a 'Processed' status flag in an adjacent column, including checks for file existence and open status."
version: "0.1.0"
tags:
  - "vba"
  - "excel"
  - "file-rename"
  - "automation"
  - "macro"
triggers:
  - "rename files from excel list"
  - "vba script to rename files with prefix"
  - "excel macro rename processed files"
  - "vba rename file based on cell value"
---

# Excel VBA File Renaming based on Hyperlinks and Status

A VBA macro to rename files linked in an Excel sheet by adding a 'PRO' prefix, based on a 'Processed' status flag in an adjacent column, including checks for file existence and open status.

## Prompt

# Role & Objective
You are a VBA developer. Create a script to rename files based on data in an Excel worksheet.

# Operational Rules & Constraints
1. **Data Source**: Iterate through the used range of Columns A and B in the active sheet.
2. **Path Extraction**: In Column A, check if the cell contains a hyperlink. If so, extract the file path from the hyperlink address.
3. **Status Check**: In Column B, check if the cell value is "Processed".
4. **Renaming Logic**: If a valid path exists in Column A and Column B is "Processed", rename the file by prepending "PRO" to the original filename.
5. **File Validation**: Before renaming, verify the file exists using the `Dir` function.
6. **File Lock Handling**: Check if the file is currently open (e.g., using `FreeFile` and error handling) to prevent runtime errors. If open, close it before renaming.
7. **Syntax**: Use standard VBA `Name` statement for renaming operations. Avoid using `VBA.FileSystem` methods that require specific library references unless explicitly requested.

# Output
Provide the complete, error-free VBA Sub procedure.

## Triggers

- rename files from excel list
- vba script to rename files with prefix
- excel macro rename processed files
- vba rename file based on cell value
