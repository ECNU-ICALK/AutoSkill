---
id: "ea1fbad9-4b58-4541-b579-afce74c3d4f8"
name: "Redshift OSL Multi-Color Pulsing Shader"
description: "Generates a Cinema 4D Redshift OSL shader that cycles through up to 10 user-defined colors, skipping black inputs, based on a time cycle calculated from Frame and FPS. It outputs pulsing color, emission color, and emission weight."
version: "0.1.0"
tags:
  - "Redshift"
  - "OSL"
  - "Shader"
  - "Pulsing"
  - "Multi-Color"
triggers:
  - "multi color pulsing shader"
  - "cycle through colors"
  - "skip black colors"
  - "10 color inputs"
  - "emission weight output"
---

# Redshift OSL Multi-Color Pulsing Shader

Generates a Cinema 4D Redshift OSL shader that cycles through up to 10 user-defined colors, skipping black inputs, based on a time cycle calculated from Frame and FPS. It outputs pulsing color, emission color, and emission weight.

## Prompt

# Role & Objective
Create a Redshift OSL shader for a multi-color pulsing effect that cycles through user-defined colors over time.

# Communication & Style Preferences
Use standard OSL syntax compatible with Redshift (e.g., `vector` instead of `vector2`, `mod` instead of `frac`, `M_PI` for pi). Ensure the code compiles without syntax errors.

# Operational Rules & Constraints
- **Inputs:**
  - `float CycleTime`: Time in seconds for a complete cycle.
  - `float FPS`: Frames per second of the animation.
  - `int Frame`: Current frame number (to be animated externally).
  - `float UserIntensity`: User-defined intensity multiplier.
  - `color Color1` through `color Color10`: 10 color inputs, defaulting to black `color(0, 0, 0)`.

- **Logic:**
  1. Filter `Color1` through `Color10` into an `ActiveColors` array. Exclude any color equal to `color(0, 0, 0)`.
  2. If no active colors exist, default `PulsingColor` and `EmissionColor` to white `color(1, 1, 1)` and set `EmissionWeight` to `UserIntensity`.
  3. Calculate `current_time = Frame / FPS`.
  4. Calculate `cyclePos = mod(current_time, CycleTime) / CycleTime`.
  5. Map `cyclePos` to the `ActiveColors` array to determine the two colors to interpolate between.
  6. Interpolate between the two active colors using `mix()`.

- **Outputs:**
  - `output color PulsingColor`: The interpolated color.
  - `output color EmissionColor`: Set equal to `PulsingColor`.
  - `output float EmissionWeight`: Set equal to `UserIntensity`.

# Anti-Patterns
- Do not use `getattribute` to retrieve time or frame information.
- Do not use `frac` function; use `mod` for fractional parts.
- Do not use `vector2` type; use `vector`.
- Do not calculate `Intensity` internally; use the `UserIntensity` input.

## Triggers

- multi color pulsing shader
- cycle through colors
- skip black colors
- 10 color inputs
- emission weight output
