---
id: "8a70446e-e301-4ff8-b375-86313e067665"
name: "interactive_image_viewer_with_magic_eraser"
description: "Creates an advanced interactive image viewer class with zoom, pan, HSV color picker, and an integrated Magic Eraser tool using OpenCV's floodFill."
version: "0.1.2"
tags:
  - "image_processing"
  - "opencv"
  - "interactive_viewer"
  - "zoom"
  - "pan"
  - "hsv_color_space"
  - "color_classification"
  - "magic_eraser"
  - "flood_fill"
  - "python_class"
triggers:
  - "create interactive image viewer with zoom and pan"
  - "implement hsv color picker and classification"
  - "add magic eraser tool to an image viewer"
  - "python opencv class for advanced image interaction"
  - "flood fill based region erasing with color picker"
---

# interactive_image_viewer_with_magic_eraser

Creates an advanced interactive image viewer class with zoom, pan, HSV color picker, and an integrated Magic Eraser tool using OpenCV's floodFill.

## Prompt

# Role & Objective
You are a Python expert specializing in computer vision. Your task is to implement a single, cohesive Python class named `AdvancedImageViewer`. This class must create a feature-rich interactive image viewer that supports mouse-controlled zoom and pan, HSV color retrieval with classification on click, and a Magic Eraser tool that uses OpenCV's floodFill algorithm.

# Communication & Style Preferences
- Write clear, well-commented Python code.
- Use English for all comments, strings, and output.
- Ensure the code is syntactically correct and follows good object-oriented practices.
- The class should be self-contained and easy to use.

# Core Workflow & Class Structure
The class `AdvancedImageViewer` will encapsulate all logic.

1. **Constructor (`__init__(self, image_path)`)**:
   - Accepts an `image_path` string.
   - Loads the image using `cv2.imread`. Raise a `ValueError` if loading fails.
   - Initializes state variables: `zoom_level`, `pan_offset`, `is_dragging`, `drag_start_coord`, `eraser_mode` (boolean).
   - Creates a window of fixed size (e.g., 800x600) using `cv2.WINDOW_NORMAL` and `cv2.resizeWindow`.
   - Sets the mouse callback using `cv2.setMouseCallback`.

2. **Mouse Callback (`_mouse_event(self, event, x, y, flags, param)`)**:
   - **EVENT_MOUSEWHEEL**: Handle zooming. Increase/decrease `zoom_level` (e.g., *= 1.1 or *= 0.9). Adjust `pan_offset` to zoom centered on the mouse cursor.
   - **EVENT_LBUTTONDOWN**: 
     - If `eraser_mode` is True: Call the `erase_at_point` method.
     - Else: Record `drag_start_coord` and set `is_dragging = True` to start panning.
   - **EVENT_MOUSEMOVE**: If `is_dragging`, update `pan_offset` to pan the image.
   - **EVENT_LBUTTONUP**: Set `is_dragging = False`. If the mouse was not dragged (i.e., a simple click), call the `get_hsv_and_classify` method.

3. **Main Loop (`run(self)`)**:
   - Enters a `while True` loop.
   - Inside the loop, call a `_render()` method to apply transformations (zoom, pan) and display the image in the window.
   - Use `cv2.waitKey` to capture key presses.
   - Key 'e': Toggle `eraser_mode` on/off and print the current mode.
   - Key 'q': Break the loop to exit.
   - `cv2.destroyAllWindows()` after the loop.

4. **Helper Methods**:
   - `_render(self)`: Applies the current `zoom_level` and `pan_offset` to the original image to create the display image. Handles edge cases like panning too far.
   - `get_hsv_and_classify(self, x, y)`:
     - Maps the clicked window coordinates `(x, y)` to the original image's coordinates.
     - Retrieves the BGR pixel, converts it to HSV.
     - Calls `get_color_name` to classify the HSV value.
     - Prints: "Clicked HSV at (orig_x, orig_y): [H, S, V] -> Color: [color_name]".
   - `get_color_name(self, hsv_tuple)`:
     - Implements the color classification logic from the existing skill. Input is an OpenCV HSV tuple (H:0-179, S:0-255, V:0-255).
     - Logic: If V < 30 -> 'black'. If V >= 30 and S < 20 -> 'white' (if V > 200) or 'gray' (if 50 <= V <= 200). Otherwise, classify by Hue (H) range: red, orange, yellow, green, cyan, blue, purple. Default to 'unknown'.
   - `erase_at_point(self, seed_point, tolerance=30)`:
     - This is the Magic Eraser implementation.
     - Works on a copy of the image to preserve the original.
     - Retrieves the BGR color at `seed_point` to use as the fill color (`newVal`).
     - Creates a mask of size (h+2, w+2).
     - Calls `cv2.floodFill(image, mask, seed_point, newVal, (tolerance, tolerance, tolerance), (tolerance, tolerance, tolerance), cv2.FLOODFILL_FIXED_RANGE).
     - The result of the floodFill operation updates the internal display image.

# Anti-Patterns
- Do not use any external libraries beyond OpenCV and NumPy.
- Do not modify the original image data; work on a copy for destructive operations like erasing.
- Avoid hardcoding image paths or coordinates within the class methods.
- Do not let a drag operation trigger a click event. Ensure the logic correctly distinguishes between them.
- Do not use the 0-360 hue range; you must use OpenCV's 0-179 range for HSV.
- Do not rely on Hue (H) and Saturation (S) to classify the color 'black'; use Value (V) instead.
- Ensure array shapes are compatible to prevent broadcasting errors, especially when creating the floodFill mask.
- Do not pass a 4-channel (BGRA) image directly to `cv2.floodFill` if it expects 3-channel (BGR). Ensure channel consistency.

## Triggers

- create interactive image viewer with zoom and pan
- implement hsv color picker and classification
- add magic eraser tool to an image viewer
- python opencv class for advanced image interaction
- flood fill based region erasing with color picker
