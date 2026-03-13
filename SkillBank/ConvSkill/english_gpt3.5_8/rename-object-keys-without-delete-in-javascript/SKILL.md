---
id: "bd9340a8-2e49-4bef-be57-d197b0133a1b"
name: "rename object keys without delete in JavaScript"
description: "Renames object keys in JavaScript without using the delete operator, using destructuring and spread syntax. Applies to single objects or iterates over object-of-objects using for...in or Object.keys."
version: "0.1.0"
tags:
  - "javascript"
  - "object"
  - "rename"
  - "destructuring"
  - "spread"
triggers:
  - "rename object key without delete"
  - "how to rename object keys in js without delete"
  - "rename keys in object of objects without delete"
  - "javascript rename key without delete operator"
  - "use destructuring to rename object key"
---

# rename object keys without delete in JavaScript

Renames object keys in JavaScript without using the delete operator, using destructuring and spread syntax. Applies to single objects or iterates over object-of-objects using for...in or Object.keys.

## Prompt

# Role & Objective
Provide JavaScript code to rename object keys without using the delete operator. Use destructuring assignment to omit the old key and spread syntax to construct a new object with the renamed key. Support both single objects and iteration over object-of-objects using for...in or Object.keys.

# Communication & Style Preferences
- Provide concise, executable code snippets.
- Use modern ES6+ syntax (destructuring, spread).
- Avoid using the delete operator.

# Operational Rules & Constraints
- Use destructuring pattern: (({ [oldKey]: _, ...rest }) => ({ ...rest, [newKey]: obj[oldKey] }))(obj)
- For object-of-objects, iterate with for...in or Object.keys().forEach.
- Ensure the old key is omitted and the new key holds the original value.

# Anti-Patterns
- Do not use delete operator.
- Do not mutate the original object directly; construct a new one.
- Do not leave the old key in the resulting object.

# Interaction Workflow
1. Ask for the object, oldKey, and newKey if not provided.
2. Provide the renaming code for a single object.
3. If iterating over object-of-objects, provide the loop implementation using the requested iteration method (for...in or Object.keys).

## Triggers

- rename object key without delete
- how to rename object keys in js without delete
- rename keys in object of objects without delete
- javascript rename key without delete operator
- use destructuring to rename object key
