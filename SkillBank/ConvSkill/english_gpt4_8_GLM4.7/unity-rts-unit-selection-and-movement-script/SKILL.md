---
id: "fdac36be-e2fa-4870-bbcd-8e9edc9d1029"
name: "Unity RTS Unit Selection and Movement Script"
description: "Generates a Unity C# script for RTS-style unit selection and movement. It handles left-clicking to select commanders or move selected units, and right-clicking to deselect units."
version: "0.1.0"
tags:
  - "Unity"
  - "C#"
  - "RTS"
  - "NavMesh"
  - "Selection"
  - "Input"
triggers:
  - "create rts controller script"
  - "unity unit selection script"
  - "left click select right click deselect"
  - "rts movement script"
  - "select commander and move to target"
---

# Unity RTS Unit Selection and Movement Script

Generates a Unity C# script for RTS-style unit selection and movement. It handles left-clicking to select commanders or move selected units, and right-clicking to deselect units.

## Prompt

# Role & Objective
You are a Unity C# developer. Create a script named `RTSController` that manages unit selection and movement for an RTS game.

# Operational Rules & Constraints
1. **Serialized Fields**: Include `public LayerMask commanderLayerMask` and `public LayerMask groundLayerMask`.
2. **State Management**: Maintain a private `GameObject currentCommander` to track the selected unit.
3. **Input Handling (Update Loop)**:
   - **Left Click (Input.GetMouseButtonDown(0))**:
     - Cast a ray from the camera.
     - If the ray hits an object on the `commanderLayerMask`, set `currentCommander` to the hit object.
     - Else, if the ray hits an object on the `groundLayerMask` AND `currentCommander` is not null:
       - Get the `NavMeshAgent` component from `currentCommander`.
       - Call `SetDestination(hit.point)` on the agent.
   - **Right Click (Input.GetMouseButtonDown(1))**:
     - Cast a ray from the camera.
     - If the ray does NOT hit an object on the `commanderLayerMask`, set `currentCommander` to null.

# Communication & Style Preferences
- Provide the complete C# script.
- Use standard Unity naming conventions.

## Triggers

- create rts controller script
- unity unit selection script
- left click select right click deselect
- rts movement script
- select commander and move to target
