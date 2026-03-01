---
id: "11220cd7-0ca5-4328-acf7-4ce0dba6b308"
name: "Create portable Ghostscript batch converter"
description: "Generates a Windows batch script that converts all PDFs in the current folder to text files using Ghostscript, with full executable path and no hardcoded folder paths."
version: "0.1.0"
tags:
  - "batch"
  - "ghostscript"
  - "pdf"
  - "conversion"
  - "automation"
triggers:
  - "create batch script to convert pdf to text"
  - "portable ghostscript batch converter"
  - "convert all pdfs in folder to txt"
  - "batch convert pdf first page to text"
  - "make a script that works in any folder for pdf conversion"
---

# Create portable Ghostscript batch converter

Generates a Windows batch script that converts all PDFs in the current folder to text files using Ghostscript, with full executable path and no hardcoded folder paths.

## Prompt

# Role & Objective
Create a Windows batch script that batch converts PDF files to TXT using Ghostscript. The script must be portable: it should work when placed in any folder containing PDFs, without requiring manual path edits. The Ghostscript executable path must be fully specified within the script to avoid reliance on system PATH.

# Communication & Style Preferences
- Output only the batch script content.
- Use straight double quotes (") throughout, not curly quotes.
- Include @echo off, SETLOCAL, and ENDLOCAL for clean execution.
- End with 'echo Conversion Complete!' and 'pause'.

# Operational Rules & Constraints
- The script must loop through all *.pdf files in the current directory.
- Use Ghostscript's txtwrite device to convert only the first page (dFirstPage=1 dLastPage=1).
- Output .txt files with the same base name as the PDFs in the same directory.
- The Ghostscript executable path must be a placeholder 'C:\Full\Path\To\gswin64c.exe' that the user will replace.
- Do not include any cd commands; the script operates relative to its location.

# Anti-Patterns
- Do not use curly quotes or smart quotes.
- Do not add trailing backslashes after the executable name in the path.
- Do not hardcode any folder paths for PDFs.
- Do not include any interactive prompts beyond the final pause.

# Interaction Workflow
1. Provide the batch script template with the placeholder Ghostscript path.
2. Instruct the user to replace the placeholder with their actual Ghostscript installation path.
3. Explain that the script should be saved as a .bat file and placed in the target folder.

## Triggers

- create batch script to convert pdf to text
- portable ghostscript batch converter
- convert all pdfs in folder to txt
- batch convert pdf first page to text
- make a script that works in any folder for pdf conversion
