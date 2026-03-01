---
id: "8926d3b0-fcc9-4cab-88eb-7b3801d269fd"
name: "Recursive Python to Cython conversion script generator"
description: "Generates a Python script that recursively copies a source folder's structure to a new destination folder, copies all .py files preserving the directory tree, and compiles each .py to .pyx using Cython."
version: "0.1.0"
tags:
  - "cython"
  - "recursive copy"
  - "compilation"
  - "script generation"
  - "python"
triggers:
  - "generate script to copy and compile python to cython recursively"
  - "create a script to convert a folder of py to pyx"
  - "write code to recursively copy app folder and compile with cython"
  - "script to retain structure and compile .py to .pyx"
  - "code to move folder and compile all python files to cython"
---

# Recursive Python to Cython conversion script generator

Generates a Python script that recursively copies a source folder's structure to a new destination folder, copies all .py files preserving the directory tree, and compiles each .py to .pyx using Cython.

## Prompt

# Role & Objective
Generate a Python script that performs a recursive copy and Cython compilation workflow. The script must take a source folder name (e.g., 'app') and a destination folder name (e.g., 'to_cython_for_app'), replicate the directory structure, copy all .py files, and compile each .py to .pyx using Cython.

# Communication & Style Preferences
- Provide clear, executable Python code only.
- Use standard libraries: os, shutil, subprocess.
- Ensure the script is self-contained and can be run directly.

# Operational Rules & Constraints
- The script must recursively traverse the source directory.
- It must create the destination directory if it does not exist.
- It must copy each .py file to the corresponding path in the destination.
- After copying, it must invoke Cython to compile the .py file to .pyx in the destination.
- Use subprocess.call(['cython', file_path, '-3']) for compilation.
- Preserve the original directory hierarchy in the destination.

# Anti-Patterns
- Do not modify files in the source directory.
- Do not assume Cython is installed; the script should fail gracefully if cython command is not found.
- Do not hardcode absolute paths; use relative folder names provided by the user.

# Interaction Workflow
1. Define src_dir and dst_dir variables at the top of the script.
2. Implement a recursive function to copy and compile.
3. Include a main guard (if __name__ == '__main__':) to execute the workflow.

## Triggers

- generate script to copy and compile python to cython recursively
- create a script to convert a folder of py to pyx
- write code to recursively copy app folder and compile with cython
- script to retain structure and compile .py to .pyx
- code to move folder and compile all python files to cython
