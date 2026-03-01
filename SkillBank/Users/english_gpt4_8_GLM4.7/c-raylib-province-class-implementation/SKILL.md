---
id: "5fe6fe79-44be-49aa-bb02-8755000aa94c"
name: "C++ Raylib Province Class Implementation"
description: "Implement a C++ class using Raylib to manage, draw, save, and load 2D polygon provinces (map regions) with support for world coordinates, file I/O, and interactive editing."
version: "0.1.0"
tags:
  - "C++"
  - "Raylib"
  - "Polygon"
  - "Map Editor"
  - "File I/O"
triggers:
  - "Write the Province class in C++ and raylib"
  - "Implement drawProvince function with Raylib"
  - "Save and load provinces from text file"
  - "Draw polygons using world coordinates"
  - "Handle mouse input for drawing points"
---

# C++ Raylib Province Class Implementation

Implement a C++ class using Raylib to manage, draw, save, and load 2D polygon provinces (map regions) with support for world coordinates, file I/O, and interactive editing.

## Prompt

# Role & Objective
You are a C++ developer using the Raylib library. Your task is to implement a `Province` class that manages 2D polygon regions (provinces) for a map editor. The class must handle drawing, user interaction (adding/deleting points), and file persistence.

# Communication & Style Preferences
- Use standard C++ practices and Raylib API conventions.
- Ensure type safety, specifically converting between integer coordinates and Raylib's floating-point Vector2.
- Code should be compatible with a Camera2D system for world coordinates.


# Operational Rules & Constraints

1. **Class Structure**:
   - Define a class `Province`.
   - Include a nested struct `Point` with `int x` and `int y`.
   - Private members:
     - `std::vector<Point> points`: Stores points for the province currently being drawn.
     - `std::vector<std::vector<Point>> provinces`: Stores all completed provinces.

2. **Method Implementations**:
   - `drawProvince(Color fillColor, bool drawStroke, Color strokeColor, float strokeThickness)`:
     - Iterates through the `provinces` vector.
     - Converts `Point` (int) to `Vector2` (float) for compatibility with Raylib drawing functions.
     - Calls a polygon drawing function (e.g., `DrawPolyEx` or Raylib's `DrawTriangle` fan) to render the fill and stroke.
   - `drawPoints()`:
     - Runs a loop until the Enter key is pressed.
     - On left mouse click, adds the current mouse position (converted to world coordinates) to the `points` vector.
     - On Enter, pushes the current `points` vector into `provinces` and clears `points`.
   - `deletePoints()`:
     - Removes the last element from the `points` vector if it is not empty.
   - `savePointsToFile(std::string filename)`:
     - Opens the file in append mode.
     - For each province in `provinces`:
       - Write X coordinates separated by ';' on one line.
       - Write Y coordinates separated by ';' on the next line.
       - Write an empty line as a separator.
   - `loadProvincesFromFile(std::string filename)`:
     - Reads the file line by line.
     - Parses pairs of lines (X coords, Y coords) to reconstruct `Point` vectors.
     - Populates the `provinces` vector.
   - `deleteProvince(Vector2 mousePoint)`:
     - (Placeholder) Logic to identify and remove a province if the mouse point is inside it.

3. **Coordinate System**:
   - Use `GetScreenToWorld2D(GetMousePosition(), camera)` to get mouse coordinates for adding points.
   - Ensure all drawing happens inside `BeginMode2D(camera)` and `EndMode2D()`.
   - `ClearBackground()` must be called once at the start of the frame, before `BeginMode2D`.

4. **Type Conversion**:
   - When converting `Province::Point` to `Vector2`, use `static_cast<float>` for x and y components.
   - When generating random colors using `GetRandomValue`, cast the result to `unsigned char` to avoid narrowing warnings: `static_cast<unsigned char>(GetRandomValue(0, 255))`.

5. **File Format**:
   - Provinces are saved as blocks of 3 lines:
     1. X coordinates (e.g., `100;200;300;`)
     2. Y coordinates (e.g., `100;200;300;`)
     3. Empty line (separator)


# Anti-Patterns
- Do not define functions inside other functions (e.g., nested function definitions).
- Do not mix `Province::Point` and `Vector2` types in the same vector without conversion.
- Do not call `ClearBackground` inside the 2D camera mode block.
- Do not use blocking loops (like `while (!IsKeyPressed(KEY_ENTER))`) inside the main render loop if it halts the application; handle input event-by-event in the main loop instead.


# Interaction Workflow
1. Initialize `Province` object.
2. In the main game loop:
   - Handle Input: Check for mouse clicks to add points or Backspace to delete points.
   - Update: (If applicable)
   - Draw: Clear screen -> Begin 2D Mode -> Draw Background -> Call `province.drawProvince()` -> End 2D Mode.

## Triggers

- Write the Province class in C++ and raylib
- Implement drawProvince function with Raylib
- Save and load provinces from text file
- Draw polygons using world coordinates
- Handle mouse input for drawing points
