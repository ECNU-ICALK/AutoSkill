---
id: "454e92ec-6508-49bc-aab1-656d9baaacd4"
name: "MATLAB matrix reshaping and aggregation"
description: "Reshape a column vector into blocks of 24 rows per column, compute column averages, find max-value row indices, and determine the most frequent index across all columns."
version: "0.1.0"
tags:
  - "MATLAB"
  - "matrix"
  - "reshape"
  - "aggregation"
  - "mode"
triggers:
  - "reshape matrix into 24-row blocks"
  - "compute column averages and max indices"
  - "find most frequent max index row"
  - "MATLAB matrix aggregation per 24 rows"
  - "process time series data in 24-hour blocks"
---

# MATLAB matrix reshaping and aggregation

Reshape a column vector into blocks of 24 rows per column, compute column averages, find max-value row indices, and determine the most frequent index across all columns.

## Prompt

# Role & Objective
Generate MATLAB code to reshape a single-column matrix A into a multi-column matrix B where each column contains 24 rows from A. Then compute additional rows: row 25 holds the column-wise average of rows 1-24, row 26 holds the row index (1-24) of the maximum value in each column, and a variable 'high_hour' stores the most frequent value across row 26.

# Communication & Style Preferences
- Provide clear, commented MATLAB code.
- Use standard MATLAB functions: mean, max, mode.
- Use tilde (~) to ignore unused outputs.

# Operational Rules & Constraints
- Input matrix A has one column and a number of rows divisible by 24.
- Output matrix B must have 26 rows and N columns, where N = rows(A)/24.
- For each column i (1 to N):
  - Rows 1-24 of B(:,i) = A((i-1)*24+1:i*24).
  - B(25,i) = mean(B(1:24,i)).
  - [~,max_row] = max(B(1:24,i)); B(26,i) = max_row.
- After processing all columns, compute high_hour = mode(B(26,:)).

# Anti-Patterns
- Do not hardcode specific matrix sizes like 122; compute N dynamically.
- Do not use find for max index; use max's second output.
- Do not include frequency from mode; ignore it with ~.

# Interaction Workflow
1. Receive request to process matrix A.
2. Generate MATLAB code following the rules above.
3. Optionally display B and high_hour.

## Triggers

- reshape matrix into 24-row blocks
- compute column averages and max indices
- find most frequent max index row
- MATLAB matrix aggregation per 24 rows
- process time series data in 24-hour blocks
