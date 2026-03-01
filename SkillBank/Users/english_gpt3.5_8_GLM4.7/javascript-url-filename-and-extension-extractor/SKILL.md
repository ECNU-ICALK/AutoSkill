---
id: "a3741b82-b6dc-48ea-a3f3-1cd444b9d95a"
name: "JavaScript URL Filename and Extension Extractor"
description: "Extracts the file name and extension from a URL string in JavaScript, applying specific formatting rules including URL decoding, uppercase extension without a dot, and a default fallback extension."
version: "0.1.0"
tags:
  - "javascript"
  - "url parsing"
  - "file extraction"
  - "string manipulation"
triggers:
  - "extract filename and extension from url in javascript"
  - "javascript get file extension from link"
  - "parse url filename and extension"
  - "url decode filename javascript"
---

# JavaScript URL Filename and Extension Extractor

Extracts the file name and extension from a URL string in JavaScript, applying specific formatting rules including URL decoding, uppercase extension without a dot, and a default fallback extension.

## Prompt

# Role & Objective
Act as a JavaScript developer. Create a function to extract the file name and extension from a given URL string based on specific formatting and logic requirements.

# Operational Rules & Constraints
1. **Filename Format**: The returned filename must include the file extension (e.g., `document.pdf`).
2. **URL Decoding**: The filename must be URL-decoded (e.g., convert `%20` to spaces) using `decodeURIComponent`.
3. **Extension Format**: The returned extension must be in uppercase.
4. **Extension Punctuation**: The returned extension must NOT include the leading dot (`.`).
5. **Default Fallback**: If the URL does not contain a detectable extension, the extension must default to `HTM`.
6. **Robustness**: The function should handle standard URLs and URLs with query parameters or complex paths.

# Output Contract
Provide a JavaScript code snippet containing the function and usage examples demonstrating the rules above.

## Triggers

- extract filename and extension from url in javascript
- javascript get file extension from link
- parse url filename and extension
- url decode filename javascript
