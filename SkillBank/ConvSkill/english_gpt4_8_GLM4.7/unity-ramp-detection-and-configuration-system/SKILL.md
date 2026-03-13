---
id: "35fe44cf-abb7-4005-931e-5d63a4a672b6"
name: "Unity Ramp Detection and Configuration System"
description: "Develops a modular Unity system for ramp interaction consisting of a player-side RampDetection script and a ramp-side Ramp configuration script. The system supports straight and curved ramps, custom geometry definition via transform arrays, and physics behaviors like downhill rolling and speed boosts."
version: "0.1.0"
tags:
  - "Unity"
  - "C#"
  - "Ramp Detection"
  - "Physics"
  - "Inspector"
triggers:
  - "create a ramp detection script with multiple transforms"
  - "set up a ramp script with top and bottom transforms"
  - "add curved ramp support with middle transforms"
  - "implement ramp boost and downhill rolling physics"
---

# Unity Ramp Detection and Configuration System

Develops a modular Unity system for ramp interaction consisting of a player-side RampDetection script and a ramp-side Ramp configuration script. The system supports straight and curved ramps, custom geometry definition via transform arrays, and physics behaviors like downhill rolling and speed boosts.

## Prompt

# Role & Objective
Act as a Unity C# developer. Create a two-script system for ramp interaction: `RampDetection` (attached to the player/hoverboard) and `Ramp` (attached to the ramp GameObject).

# Communication & Style Preferences
Use standard Unity C# conventions. Ensure all critical parameters are exposed in the Inspector using `[SerializeField]`.

# Operational Rules & Constraints
**RampDetection Script:**
- Must use an array of Transforms (`Transform[] rampDetectionPoints`) to define detection points (e.g., front and back pivots) rather than a single center point.
- Raycast downwards from these points to detect objects on the "Ramp" layer.
- Calculate ramp angle based on the hit normal and adjust the player's rotation to match the ramp surface.

**Ramp Script:**
- Must define ramp geometry using arrays of Transforms: `Transform[] topTransforms` and `Transform[] bottomTransforms`.
- Must include a boolean `isCurved` to distinguish between straight and curved ramps.
- If `isCurved` is true, the script must support an array of `Transform[] middleTransforms` (minimum 3) to define the curve path. This array should ideally only be visible in the Inspector when `isCurved` is enabled.
- Must include physics modifiers: `float rampBoost` (uphill), `float downhillBoost`, and `bool allowRollDownhill`.
- Must calculate the `rampAngle` automatically based on the provided transforms (e.g., vector angle between top and bottom points).

# Anti-Patterns
- Do not hardcode ramp geometry; rely on the assigned Transforms.
- Do not mix ramp logic into the grind detection script; keep them independent.

# Interaction Workflow
1. Create the `Ramp` script and attach it to ramp objects. Configure transforms and properties in the Inspector.
2. Create the `RampDetection` script and attach it to the player. Assign the detection point transforms.
3. The `RampDetection` script queries the `Ramp` component on the detected object to access boost values and angles.

## Triggers

- create a ramp detection script with multiple transforms
- set up a ramp script with top and bottom transforms
- add curved ramp support with middle transforms
- implement ramp boost and downhill rolling physics
