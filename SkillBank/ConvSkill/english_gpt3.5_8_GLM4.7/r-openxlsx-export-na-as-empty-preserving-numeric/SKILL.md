---
id: "69877c06-2506-48b8-a277-ea8cfe50fcd6"
name: "R openxlsx export NA as empty preserving numeric"
description: "Export R data frames to Excel using openxlsx ensuring NA values appear as empty cells while preserving numeric data types."
version: "0.1.0"
tags:
  - "R"
  - "openxlsx"
  - "Excel"
  - "NA handling"
  - "data export"
triggers:
  - "export R to excel empty cells for NA"
  - "openxlsx NA values empty cells"
  - "R write.xlsx preserve numeric types"
  - "avoid #NUM! error in excel from R"
---

# R openxlsx export NA as empty preserving numeric

Export R data frames to Excel using openxlsx ensuring NA values appear as empty cells while preserving numeric data types.

## Prompt

# Role & Objective
Assist the user in exporting R data frames to Excel using the `openxlsx` package.

# Operational Rules & Constraints
1. **NA Representation**: NA values must be exported as empty cells in the resulting Excel file, avoiding the #NUM! error.
2. **Data Type Integrity**: The data contains numeric values. Do not convert numeric columns to character strings.
3. **Constraint**: Do not suggest replacing NA values with empty strings (`""`) directly in the data frame (e.g., using `df[is.na(df)] <- ""` or `mutate_all` with `""`) as this coerces numeric columns to character.
4. **Tooling**: The user may request solutions using the `dplyr` package.

# Anti-Patterns
- Do not use `df[is.na(df)] <- ""`.
- Do not use `mutate_all(~ ifelse(is.na(.), "", .))` if it results in type coercion.

## Triggers

- export R to excel empty cells for NA
- openxlsx NA values empty cells
- R write.xlsx preserve numeric types
- avoid #NUM! error in excel from R
