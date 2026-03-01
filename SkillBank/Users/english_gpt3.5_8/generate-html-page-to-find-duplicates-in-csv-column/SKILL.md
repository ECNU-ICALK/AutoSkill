---
id: "c2aacc1e-24bb-4092-b68a-cdf817d4acfc"
name: "Generate HTML page to find duplicates in CSV column"
description: "Generate a production-ready HTML webpage with JavaScript to read a CSV file and find duplicate values in a specified column. Optionally style with Tailwind CSS, include UTF-8 support, proper linting, and documentation."
version: "0.1.0"
tags:
  - "html"
  - "javascript"
  - "csv"
  - "duplicates"
  - "tailwindcss"
triggers:
  - "generate html page to find duplicates in csv"
  - "create a webpage to detect duplicate entries in a csv column"
  - "build a tool to find duplicates in csv file"
  - "html javascript csv duplicate finder"
  - "csv column duplicate detection tool"
---

# Generate HTML page to find duplicates in CSV column

Generate a production-ready HTML webpage with JavaScript to read a CSV file and find duplicate values in a specified column. Optionally style with Tailwind CSS, include UTF-8 support, proper linting, and documentation.

## Prompt

# Role & Objective
Generate a self-contained HTML webpage with JavaScript that reads a user-uploaded CSV file and identifies duplicate values in a user-specified column. The output must be only code, runnable immediately, and production-ready.

# Communication & Style Preferences
- Output only the complete HTML code without any extra explanations or comments outside the code block.
- Use UTF-8 encoding for the HTML document.
- Include proper JSDoc-style documentation for JavaScript functions.
- Follow linting best practices for HTML and JavaScript.

# Operational Rules & Constraints
- The page must include a file input for CSV files and a text input for the column name.
- Use FileReader API to read the CSV as text with UTF-8 encoding.
- Parse CSV by splitting lines on newline and values on commas.
- Find the column index by matching the header name exactly.
- Identify duplicates using array filtering logic.
- Display results using browser alerts.
- If requested, include Tailwind CSS via CDN link; ensure the link is valid and functional.
- Ensure the code is production-ready with error handling for missing file or column.

# Anti-Patterns
- Do not include any explanatory text outside the code.
- Do not use external libraries except Tailwind CSS when requested.
- Do not assume CSV structure beyond comma-separated values.
- Do not output results to the console; use alerts.

# Interaction Workflow
1. Provide file input for CSV upload.
2. Provide text input for column name.
3. On button click, read and parse the CSV.
4. Validate column existence.
5. Extract column values and find duplicates.
6. Alert user with duplicates or a no-duplicates message.

## Triggers

- generate html page to find duplicates in csv
- create a webpage to detect duplicate entries in a csv column
- build a tool to find duplicates in csv file
- html javascript csv duplicate finder
- csv column duplicate detection tool
