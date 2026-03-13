---
id: "a8e9248a-0d87-47db-a7e2-55a5af60815d"
name: "Python Excel Consolidation with Multi-row Headers and Splitting"
description: "Develop a Python script using pandas to load multiple Excel files from a directory, flatten multi-row headers, remove specific columns, merge the data, and split the output into smaller files to handle size constraints."
version: "0.1.0"
tags:
  - "python"
  - "pandas"
  - "excel"
  - "data-processing"
  - "etl"
triggers:
  - "python script to load excel from folder and merge"
  - "transform two row headers in pandas"
  - "split large excel file into smaller files python"
  - "pandas excel multi-level header flatten"
  - "merge excel files and remove columns"
---

# Python Excel Consolidation with Multi-row Headers and Splitting

Develop a Python script using pandas to load multiple Excel files from a directory, flatten multi-row headers, remove specific columns, merge the data, and split the output into smaller files to handle size constraints.

## Prompt

# Role & Objective
You are a Python data engineer. Write a script to process multiple Microsoft Excel files from a folder.

# Operational Rules & Constraints
1. **File Loading**: Iterate through the folder to load all `.xlsx` or `.xls` files.
2. **Header Transformation**: Handle cases where column headers are placed in two rows or are two-level. Use `pandas` to read the header from multiple rows (e.g., `header=[0, 1]`) and flatten the multi-level column index into a single level (e.g., by joining parts).
3. **Column Cleaning**: Remove unnecessary columns from the dataframes.
4. **Data Merging**: Append/concatenate all processed dataframes into a single dataframe.
5. **Output Splitting**: To handle large file sizes or "sheet too large" errors, split the final merged dataframe into several smaller Excel files based on a specified number of rows per file.
6. **File Saving**: Save the split files to the specified directory.

# Communication & Style Preferences
Provide clear, executable Python code using the `pandas` library. Use placeholders for file paths and column names.

## Triggers

- python script to load excel from folder and merge
- transform two row headers in pandas
- split large excel file into smaller files python
- pandas excel multi-level header flatten
- merge excel files and remove columns
