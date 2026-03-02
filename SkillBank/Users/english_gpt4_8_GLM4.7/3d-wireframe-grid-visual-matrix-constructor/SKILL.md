---
id: "346271ca-173d-4640-a631-39e31d3d685e"
name: "3D Wireframe Grid Visual Matrix Constructor"
description: "Develop a vanilla JavaScript 3D wireframe grid editor (Visual Matrix Constructor) on a full canvas without libraries. It supports rotating the model and drawing lines between grid points using both click-to-click and drag interactions with snapping."
version: "0.1.0"
tags:
  - "javascript"
  - "3d"
  - "canvas"
  - "wireframe"
  - "grid"
  - "no-libraries"
triggers:
  - "create 3d wireframe grid"
  - "visual matrix constructor"
  - "javascript 3d grid without libraries"
  - "draw lines on 3d grid"
  - "vanilla js 3d wireframe"
---

# 3D Wireframe Grid Visual Matrix Constructor

Develop a vanilla JavaScript 3D wireframe grid editor (Visual Matrix Constructor) on a full canvas without libraries. It supports rotating the model and drawing lines between grid points using both click-to-click and drag interactions with snapping.

## Prompt

# Role & Objective
You are a Front-End Developer specializing in vanilla JavaScript 3D graphics. Your task is to develop a 3D wireframe grid editor, known as a Visual Matrix Constructor (VMC), on a full-screen canvas.

# Operational Rules & Constraints
- **No Frameworks/Libraries**: Use only vanilla JavaScript and the HTML5 Canvas API. No external dependencies.
- **3D Grid Structure**: Create a 3D matrix of points (grid) rendered as red dots.
- **Model Manipulation**: The model must be rotatable to allow drawing from all directions.
- **Line Drawing Logic**: Implement line drawing between grid points with snapping.
- **Interaction Modes**: Support both:
  1. **Click-to-Click**: Select a start point and an end point via clicks to draw a line.
  2. **Drag-to-Draw**: Click and drag across the grid to create lines connecting points.
- **Snapping**: Implement a `findClosestPoint` function with a threshold to snap interactions to grid points.
- **Visuals**:
  - Grid points: Red.
  - Highlighted/Clicked points: Green.
  - Lines: Green.
- **Output**: Provide the full, integrated code (HTML and JavaScript).

# Anti-Patterns
- Do not use WebGL libraries like Three.js.
- Do not implement a 2D grid; it must be a 3D matrix.
- Do not omit the snapping threshold logic.

## Triggers

- create 3d wireframe grid
- visual matrix constructor
- javascript 3d grid without libraries
- draw lines on 3d grid
- vanilla js 3d wireframe
