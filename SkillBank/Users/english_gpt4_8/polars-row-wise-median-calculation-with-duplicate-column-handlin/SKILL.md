---
id: "11ce65b5-8e16-430e-9399-81b95fe54ae0"
name: "Polars row-wise median calculation with duplicate column handling"
description: "Calculate row-wise median across multiple columns in Polars DataFrame using a 3-step approach that avoids alias conflicts in loops and handles duplicate columns gracefully."
version: "0.1.0"
tags:
  - "polars"
  - "row-wise"
  - "median"
  - "dataframe"
  - "duplicate-handling"
triggers:
  - "calculate row-wise median polars"
  - "polars median across columns"
  - "avoid duplicate column error polars"
  - "row aggregation polars"
  - "median without alias polars"
---

# Polars row-wise median calculation with duplicate column handling

Calculate row-wise median across multiple columns in Polars DataFrame using a 3-step approach that avoids alias conflicts in loops and handles duplicate columns gracefully.

## Prompt

# Role & Objective
Calculate row-wise median across specified columns in a Polars DataFrame while avoiding duplicate column errors in iterative processes.

# Communication & Style Preferences
- Use clear, step-by-step code blocks
- Avoid using .alias() in the first calculation line to prevent duplicate column errors in loops
- Handle column existence checks explicitly

# Operational Rules & Constraints
1. Use a 3-step approach:
   a) Calculate median values without aliasing in the first line
   b) Create a Series or handle the result appropriately
   c) Add the result back to the DataFrame
2. Before adding the new column, check if it exists and drop if necessary
3. Use only Polars operations, no pandas conversion
4. Use pl.concat_list() to combine columns for row-wise operations
5. Use .arr.median() for median calculation on the concatenated list

# Anti-Patterns
- Do not use .alias() in the calculation expression when inside loops
- Do not use pandas conversion methods
- Do not create intermediate named columns that might conflict
- Do not use .transpose() for row-wise operations

# Interaction Workflow
1. Check if target column exists and drop if present
2. Calculate row-wise median using pl.concat_list() and .arr.median()
3. Add the result to DataFrame using with_columns() or hstack()
4. Clean up any temporary columns if created

## Triggers

- calculate row-wise median polars
- polars median across columns
- avoid duplicate column error polars
- row aggregation polars
- median without alias polars
