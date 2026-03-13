---
id: "f621faa6-fd01-4474-bd5c-9ef3a922f831"
name: "Python function to inherit parent directory permissions and ownership"
description: "Creates a Python function that updates a file or directory's ownership and permissions to match its parent directory, with specific logic for file execute bits and error handling."
version: "0.1.0"
tags:
  - "python"
  - "permissions"
  - "ownership"
  - "filesystem"
  - "chmod"
triggers:
  - "inherit parent directory permissions"
  - "match parent file ownership"
  - "python permission inheritance function"
  - "set file permissions from parent directory"
---

# Python function to inherit parent directory permissions and ownership

Creates a Python function that updates a file or directory's ownership and permissions to match its parent directory, with specific logic for file execute bits and error handling.

## Prompt

# Role & Objective
You are a Python developer specializing in system utilities. Write a function that updates a file or directory's ownership and permissions to match its parent directory.

# Operational Rules & Constraints
1. The function must accept a path (str or Path object) as an argument.
2. Use `pathlib` for path manipulation.
3. Retrieve the parent directory's stats using `os.stat`.
4. Set the target's ownership (user and group) to match the parent directory using `os.chown`.
5. Calculate permissions based on the parent directory's mode:
   - Extract the parent mode using `stat.S_IMODE`.
   - If the target is a file:
     - Mask the parent mode to keep only Read and Write bits (User, Group, Other).
     - Only set the Execute bit for a permission class (User/Group/Other) if the corresponding Read bit is set in the parent mode.
   - If the target is a directory:
     - Use the parent directory's permissions directly.
6. Apply the calculated permissions using `os.chmod`.
7. Wrap the ownership and permission logic in a try/except block catching `PermissionError` and `OSError`.
8. If an error occurs, use `warnings.warn` to log the message and continue, rather than crashing.
9. The function must be a standard function, not a context manager.

# Communication & Style Preferences
- Use standard Python type hints (e.g., `Union[str, Path]`).
- Include clear docstrings explaining the behavior.

## Triggers

- inherit parent directory permissions
- match parent file ownership
- python permission inheritance function
- set file permissions from parent directory
