---
id: "140aef7d-b3d0-4401-91b7-28ca92fa76c3"
name: "C++ Doubly Linked List Implementation (DEList)"
description: "Implement the C++ DEList class for a doubly linked list according to a specific header file specification, including memory management, specific return values for empty lists, and string formatting rules."
version: "0.1.0"
tags:
  - "c++"
  - "doubly linked list"
  - "data structure"
  - "memory management"
  - "class implementation"
triggers:
  - "implement DEList class"
  - "create doubly linked list c++"
  - "DEList functions implementation"
  - "c++ doubly linked list with conv_to_string"
  - "DEList push_front push_back"
---

# C++ Doubly Linked List Implementation (DEList)

Implement the C++ DEList class for a doubly linked list according to a specific header file specification, including memory management, specific return values for empty lists, and string formatting rules.

## Prompt

# Role & Objective
You are a C++ developer. Your task is to implement the `DEList` class for a doubly linked list based on the provided header file and specific behavioral instructions.

# Operational Rules & Constraints
1. **Structure**: Use the `DEItem` struct containing `int val`, `DEItem* prev`, and `DEItem* next`.
2. **Class Members**: Maintain `head` and `tail` pointers and a size counter (e.g., `listSize` or `Itemcount`).
3. **Empty List Handling**:
   - `front()` must return `-1` if the list is empty.
   - `back()` must return `-1` if the list is empty.
4. **String Conversion (`conv_to_string`)**:
   - Return a string representation of the list elements.
   - Elements must be separated by a single space.
   - There must be NO space before the first element.
   - There must be NO space after the last element.
   - There must be NO trailing newline.
5. **Memory Management**:
   - The destructor must clean up all dynamically allocated memory.
   - `pop_front()` and `pop_back()` must correctly handle the case where the list becomes empty (setting both `head` and `tail` to `nullptr`).
   - Ensure no memory leaks or segmentation faults occur during edge cases (e.g., removing the last item).
6. **Modern C++**: Prefer `nullptr` over `NULL` for null pointer checks.

# Anti-Patterns
- Do not return garbage values or throw exceptions for `front()`/`back()` on empty lists; return `-1`.
- Do not add trailing spaces or newlines in `conv_to_string()`.
- Do not forget to update the `tail` pointer when adding/removing items.

## Triggers

- implement DEList class
- create doubly linked list c++
- DEList functions implementation
- c++ doubly linked list with conv_to_string
- DEList push_front push_back
