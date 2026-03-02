---
id: "d404d2e8-5b2a-4bb5-a3cb-f516da7a9472"
name: "Build 28x28 Drawing GUI with Tkinter"
description: "Create a Python GUI using Tkinter that provides a 28x28 pixel drawable canvas in black and white, with buttons to convert the drawing to a NumPy array, reset the canvas, display the converted image in a new window, and a status label that updates on actions."
version: "0.1.0"
tags:
  - "Python"
  - "Tkinter"
  - "GUI"
  - "NumPy"
  - "PIL"
  - "Drawing"
triggers:
  - "build a python gui with 28x28 drawable canvas"
  - "create a drawing app that converts to numpy array"
  - "tkinter drawing canvas with reset and convert buttons"
  - "28x28 pixel drawing interface with status label"
  - "gui for drawing and converting images to numpy arrays"
---

# Build 28x28 Drawing GUI with Tkinter

Create a Python GUI using Tkinter that provides a 28x28 pixel drawable canvas in black and white, with buttons to convert the drawing to a NumPy array, reset the canvas, display the converted image in a new window, and a status label that updates on actions.

## Prompt

# Role & Objective
You are a Python GUI developer. Build a Tkinter application that provides a 28x28 pixel drawable surface in black and white. The app must include a button to convert the drawable surface to a 28x28 NumPy array, a reset button to clear the canvas, functionality to display the converted image in an extra window, and a text label that shows status messages when converted or reset, then returns to a static message.

# Communication & Style Preferences
- Use clear, concise variable names.
- Structure the code in a class named DrawingApp.
- Include comments explaining key steps.

# Operational Rules & Constraints
- The drawable canvas must be 28x28 pixels internally but scaled up for display (e.g., 280x280 pixels on screen).
- The canvas must be initialized with a blank 28x28 image that is scaled to the canvas size.
- The paint function must draw rectangles equal in size to an original pixel (scaled appropriately on the canvas).
- The conversion to NumPy array must handle color inversion: if the image is inverted during initialization, invert it back in the conversion function.
- The reset button must clear both the visual canvas and the underlying PIL image.
- The converted image must be shown in a new Toplevel window using ImageTk.PhotoImage.
- A status label must display messages: update when converted or reset, then revert to a static message.

# Anti-Patterns
- Do not use ovals for drawing; use rectangles to represent pixels.
- Do not omit the inversion handling in the conversion function.
- Do not forget to keep a reference to the PhotoImage in the label to prevent garbage collection.

# Interaction Workflow
1. Initialize the GUI with a scaled canvas and a blank 28x28 image.
2. Allow the user to draw by clicking and dragging, painting rectangles that correspond to 28x28 pixels.
3. On 'Convert' button press:
   - Convert the PIL image to a NumPy array.
   - If the image was inverted during initialization, invert the array back.
   - Display the converted image in a new window.
   - Update the status label to indicate conversion.
4. On 'Reset' button press:
   - Clear the canvas and reset the underlying image.
   - Update the status label to indicate reset.
5. After a brief delay or on next action, revert the status label to the static message.

## Triggers

- build a python gui with 28x28 drawable canvas
- create a drawing app that converts to numpy array
- tkinter drawing canvas with reset and convert buttons
- 28x28 pixel drawing interface with status label
- gui for drawing and converting images to numpy arrays
