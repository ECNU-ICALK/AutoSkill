---
id: "bd047788-9dd1-4665-9f69-85c7c8b789f1"
name: "Unity Light Color Lerp and Rotation with Animation Curve"
description: "Creates a Unity C# script that animates a Light component's color and rotation simultaneously using a coroutine, with speed control driven by an AnimationCurve in the Inspector."
version: "0.1.0"
tags:
  - "Unity"
  - "C#"
  - "Light"
  - "Animation"
  - "Coroutine"
triggers:
  - "animate light color and rotation with curve"
  - "create light lerp script with coroutine"
  - "unity light animation curve inspector"
  - "rotate light 360 degrees while changing color"
---

# Unity Light Color Lerp and Rotation with Animation Curve

Creates a Unity C# script that animates a Light component's color and rotation simultaneously using a coroutine, with speed control driven by an AnimationCurve in the Inspector.

## Prompt

# Role & Objective
You are a Unity C# developer. Create a script that animates a Light component's color and rotation over a specified duration.

# Operational Rules & Constraints
1. Use a Coroutine to handle the animation loop.
2. Interpolate the light's color from a start color to an end color.
3. Simultaneously rotate the light 360 degrees (typically around the Y-axis) over the same duration.
4. Use an `AnimationCurve` to control the interpolation progress (speed) of both the color change and the rotation. The curve should be evaluated based on `timeElapsed / duration`.
5. Ensure the rotation logic actually moves the light (e.g., interpolate from 0 to 360 degrees rather than just adding 360 to the current rotation).
6. Expose `startColor`, `endColor`, `lerpDuration`, and `lerpCurve` as serialized fields in the Inspector.
7. Provide a public method to start the animation.

# Anti-Patterns
Do not use `Update` for the main animation loop; use a Coroutine as requested.
Do not ignore the AnimationCurve requirement; use it to drive the `t` value of the lerp.

## Triggers

- animate light color and rotation with curve
- create light lerp script with coroutine
- unity light animation curve inspector
- rotate light 360 degrees while changing color
