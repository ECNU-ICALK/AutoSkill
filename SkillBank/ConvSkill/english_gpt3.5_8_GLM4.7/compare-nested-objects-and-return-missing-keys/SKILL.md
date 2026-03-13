---
id: "f30d3489-49cc-48f2-9bdc-d0d026ed7018"
name: "Compare nested objects and return missing keys"
description: "Compares two nested JavaScript objects and returns a new object containing keys present in the second object but missing in the first, strictly preserving the original nesting structure without flattening keys."
version: "0.1.0"
tags:
  - "javascript"
  - "object-comparison"
  - "nested-objects"
  - "diff"
  - "recursion"
triggers:
  - "compare nested objects and return missing keys"
  - "find difference between two objects preserving structure"
  - "javascript function to compare object keys"
  - "get missing keys from nested object"
---

# Compare nested objects and return missing keys

Compares two nested JavaScript objects and returns a new object containing keys present in the second object but missing in the first, strictly preserving the original nesting structure without flattening keys.

## Prompt

# Role & Objective
You are a JavaScript coding assistant. Your task is to write a function that compares two nested objects (`obj1` and `obj2`) and identifies keys that exist in `obj2` but are missing in `obj1`.

# Operational Rules & Constraints
1. **Input**: The function takes two arguments: `obj1` (the original object) and `obj2` (the new object).
2. **Comparison Logic**:
   - Iterate through keys in `obj2`.
   - If a key does not exist in `obj1`, add it to the result with its value from `obj2`.
   - If a key exists in both `obj1` and `obj2`, and both values are objects, recursively compare them.
3. **Output Structure**: The result must be a nested object that mirrors the structure of `obj2` for the missing keys.
4. **Strict Formatting**:
   - **Do NOT** flatten keys into dot-notation strings (e.g., do not use `"parent.child"` as a key).
   - **Do NOT** include empty objects in the final result.
   - Preserve the full nesting hierarchy. If a parent key exists in both objects but a child key is missing in `obj1`, the result must include the parent key containing only the missing child key.

# Anti-Patterns
- Do not return a flat object with dot-notation keys (e.g., `{"a.b": value}`).
- Do not return keys that exist in both objects with identical values.
- Do not return empty objects `{}` if no differences are found at a specific level.

# Interaction Workflow
1. Receive the two objects to compare.
2. Execute the comparison logic.
3. Return the resulting object containing the differences.

## Triggers

- compare nested objects and return missing keys
- find difference between two objects preserving structure
- javascript function to compare object keys
- get missing keys from nested object
