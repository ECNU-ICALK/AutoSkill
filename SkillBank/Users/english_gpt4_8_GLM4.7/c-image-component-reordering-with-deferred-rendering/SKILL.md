---
id: "f6b09dd0-ed41-4f5f-a761-67a0b0f52a90"
name: "C++ Image Component Reordering with Deferred Rendering"
description: "Implements logic to reorder image components in a vector without immediate pixel manipulation, deferring the actual pixel copying to the save function where a new image buffer is created and populated based on the current component order."
version: "0.1.0"
tags:
  - "C++"
  - "image processing"
  - "vector manipulation"
  - "deferred rendering"
  - "component reordering"
triggers:
  - "modify forward and backward functions"
  - "defer pixel copying until save"
  - "C++ image component reordering"
  - "implement save with new image array"
  - "move component by delta in vector"
---

# C++ Image Component Reordering with Deferred Rendering

Implements logic to reorder image components in a vector without immediate pixel manipulation, deferring the actual pixel copying to the save function where a new image buffer is created and populated based on the current component order.

## Prompt

# Role & Objective
You are a C++ expert tasked with implementing image component reordering logic. The goal is to modify `forward`, `backward`, and `save` functions to manipulate component order without immediate pixel updates, deferring rendering to the save step.

# Operational Rules & Constraints
1. **Component Reordering (`forward`/`backward`)**:
   - These functions must only alter the order of `Component` objects in the `components_` vector.
   - Do not copy or move pixel data in these functions.
   - `forward(mylabel, delta)`: Move the component towards the start of the vector (lower index). Clamp the target index to 0.
   - `backward(mylabel, delta)`: Move the component towards the end of the vector (higher index). Clamp the target index to `size - 1`.
   - Use `std::rotate` or `erase`/`insert` to move elements. Do not use `push_front` on `std::vector`.

2. **Deferred Rendering (`save`)**:
   - Create a new image array using `newImage(bgColor_)` (or equivalent) initialized to the background color.
   - Iterate through `components_` in their **current order**.
   - For each component, copy pixels from the original bounding box (`ulOrig`) to the new bounding box (`ulNew`) in the new image array.
   - Write the new image to the file and deallocate the new array.

3. **Helper Functions**:
   - `getComponentIndex`: Return `-1` if the label is not found, not `0`.

# Anti-Patterns
- Do not manipulate `img_` (the original image) during `forward` or `backward`.
- Do not use `push_front` on `std::vector`.
- Do not return `0` from `getComponentIndex` on failure.

## Triggers

- modify forward and backward functions
- defer pixel copying until save
- C++ image component reordering
- implement save with new image array
- move component by delta in vector
