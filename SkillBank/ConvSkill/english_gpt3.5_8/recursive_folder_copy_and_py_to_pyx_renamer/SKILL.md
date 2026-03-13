---
id: "8926d3b0-fcc9-4cab-88eb-7b3801d269fd"
name: "recursive_folder_copy_and_py_to_pyx_renamer"
description: "Recursively copy a source folder to a new destination while preserving directory structure, renaming all .py files to .pyx, and creating the destination if it does not exist."
version: "0.1.1"
tags:
  - "cython"
  - "recursive copy"
  - "rename"
  - "script generation"
  - "python"
  - "folder"
triggers:
  - "copy folder recursively and rename .py to .pyx"
  - "retain structure and copy .py as .pyx"
  - "recursive copy with extension rename"
  - "create new folder and copy .py as .pyx"
  - "script to recursively copy and rename py files"
---

# recursive_folder_copy_and_py_to_pyx_renamer

Recursively copy a source folder to a new destination while preserving directory structure, renaming all .py files to .pyx, and creating the destination if it does not exist.

## Prompt

# Role & Objective
Generate a Python script that performs a recursive copy and file renaming workflow. The script must take a source folder name (e.g., 'app') and a destination folder name (e.g., 'to_cython_for_app'), replicate the directory structure, copy all .py files, and rename them to .pyx in the new location.

# Constraints & Style
- Provide clear, executable Python code only.
- Use standard libraries: os, shutil.
- Ensure the script is self-contained and can be run directly.
- Use os.makedirs with exist_ok=True for directory creation.
- Use os.walk for recursive traversal.
- Use shutil.copy2 to preserve file metadata.

# Core Workflow
1. Define configurable source_dir and new_dir variables at the top of the script.
2. Ensure the new_dir exists using os.makedirs(new_dir, exist_ok=True).
3. Walk the source_dir with os.walk.
4. For each .py file, construct the full destination path, preserving the relative structure and renaming the file extension to .pyx.
5. Create any necessary intermediate destination subdirectories.
6. Copy the file from source to destination using shutil.copy2.
7. Include a main guard (if __name__ == '__main__':) to execute the workflow.

# Anti-Patterns
- Do not modify files in the source directory.
- Do not hardcode absolute paths; use relative folder names provided by the user.
- Do not flatten the directory structure; preserve the original hierarchy.
- Do not rename non-.py files.
- Do not attempt to compile files with Cython; the task is to copy and rename only.

## Triggers

- copy folder recursively and rename .py to .pyx
- retain structure and copy .py as .pyx
- recursive copy with extension rename
- create new folder and copy .py as .pyx
- script to recursively copy and rename py files
