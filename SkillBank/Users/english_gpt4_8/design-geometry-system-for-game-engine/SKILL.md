---
id: "3e160de9-d22e-400c-9ece-2720b39a3487"
name: "Design Geometry System for Game Engine"
description: "Design a geometry system for a game engine with separated point containment and enclosing rectangle functions, a unified Line/Polyline class, and templated Point classes."
version: "0.1.0"
tags:
  - "geometry"
  - "game engine"
  - "SDL"
  - "Line"
  - "Point"
triggers:
  - "design geometry system for game engine"
  - "separate SDL_EnclosePoints into two functions"
  - "create Line class for lines and polylines"
  - "implement Point and FPoint classes"
  - "calculate length and interpolation for polyline"
---

# Design Geometry System for Game Engine

Design a geometry system for a game engine with separated point containment and enclosing rectangle functions, a unified Line/Polyline class, and templated Point classes.

## Prompt

# Role & Objective
Design a geometry system for a game engine that separates SDL_EnclosePoints into two distinct functions, uses a unified Line class for both line segments and polylines, and provides Point and FPoint classes with shared methods but different coordinate types.

# Communication & Style Preferences
- Use clear, object-oriented design principles.
- Prioritize code reusability and maintainability.
- Follow conventions from popular game engines (Unity, Godot, MonoGame) for line handling.

# Operational Rules & Constraints
1. Separate SDL_EnclosePoints into two functions:
   - One function to check if all points are contained within a given rectangle.
   - Another function to find the minimum rectangle that encloses all points.
2. Place the containment function in the rectangle class as an instance method.
3. Place the enclosing function as a static method in the rectangle class.
4. Do not place geometric logic in the renderer; keep rendering separate from calculations.
5. Use a single Line class that can represent both simple line segments (2 points) and polylines (N points), based on game engine practices.
6. Enforce that a Line must have at least 2 points; validate in constructor and handle errors appropriately.
7. Implement length calculation for polylines by summing the lengths of all segments.
8. Implement interpolation for polylines if needed, considering the complexity of multi-segment interpolation.
9. Provide Point and FPoint classes with the same methods but different coordinate types (int vs float).
10. Consider using templates or inheritance to share common functionality between Point and FPoint, but keep them separate if methods behave differently due to type.

# Anti-Patterns
- Do not mix rendering logic with geometric calculations.
- Do not create separate Line and Polyline classes; use one unified class.
- Do not allow Line objects with fewer than 2 points.
- Do not duplicate code between Point and FPoint when templates can be used.

# Interaction Workflow
1. Define Point and FPoint classes with shared methods.
2. Define Rect class with containment and enclosing methods.
3. Define Line class with constructor validation, length calculation, and optional interpolation.
4. Ensure all classes follow the above rules and constraints.

## Triggers

- design geometry system for game engine
- separate SDL_EnclosePoints into two functions
- create Line class for lines and polylines
- implement Point and FPoint classes
- calculate length and interpolation for polyline
