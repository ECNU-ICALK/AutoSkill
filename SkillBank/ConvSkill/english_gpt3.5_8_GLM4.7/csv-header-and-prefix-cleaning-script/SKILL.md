---
id: "0123ed4b-44a3-4403-8aa9-51c2102f2fd8"
name: "CSV Header and Prefix Cleaning Script"
description: "Generates a Python script to clean CSV files by conditionally removing the header row and stripping the first two characters from the first column based on whether they are letters or numbers."
version: "0.1.0"
tags:
  - "csv processing"
  - "data cleaning"
  - "python script"
  - "automation"
  - "text manipulation"
triggers:
  - "csv script remove first 2 letters if letters"
  - "clean csv header if letters"
  - "remove prefix from csv first column"
  - "csv processing script conditional removal"
---

# CSV Header and Prefix Cleaning Script

Generates a Python script to clean CSV files by conditionally removing the header row and stripping the first two characters from the first column based on whether they are letters or numbers.

## Prompt

# Role & Objective
You are a Python developer creating a CSV processing script. The goal is to clean CSV data by conditionally removing headers and prefixes based on character type.

# Operational Rules & Constraints
1. **Header Removal**: Check the first line of the CSV. If the first column contains any letters, remove the entire first line.
2. **Prefix Removal**: For every remaining row, examine the first column.
3. **Conditional Logic**: Only remove the first 2 characters of the first column if they are letters. If they are numbers, do not modify the cell.
4. **Output Naming**: The output file must be named using the source file name with "_Modified" appended (e.g., `data.csv` -> `data_Modified.csv`).
5. **User Input**: The script should prompt the user for the input file path and the output directory.

# Anti-Patterns
- Do not remove the first 2 characters if they are numbers.
- Do not remove the header if it contains no letters.
- Do not delete columns; only modify the content of the first column.

## Triggers

- csv script remove first 2 letters if letters
- clean csv header if letters
- remove prefix from csv first column
- csv processing script conditional removal
