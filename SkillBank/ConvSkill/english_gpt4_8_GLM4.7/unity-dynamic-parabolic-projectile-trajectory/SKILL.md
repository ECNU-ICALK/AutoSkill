---
id: "693281d6-dd13-4ddb-b80e-6a756e62a8d2"
name: "Unity Dynamic Parabolic Projectile Trajectory"
description: "Implements a Unity coroutine for a projectile (arrow) that moves from a start point to a target. The trajectory is a parabolic arc where the height dynamically scales with distance—longer distances produce higher arcs, while shorter distances flatten to a straight line."
version: "0.1.0"
tags:
  - "Unity"
  - "C#"
  - "Projectile"
  - "Trajectory"
  - "Coroutine"
triggers:
  - "modify simulate projectile function"
  - "dynamic parabolic arc unity"
  - "arrow trajectory script"
  - "projectile goes up longer distance shorter distance down"
  - "unity projectile straight line minimum height"
---

# Unity Dynamic Parabolic Projectile Trajectory

Implements a Unity coroutine for a projectile (arrow) that moves from a start point to a target. The trajectory is a parabolic arc where the height dynamically scales with distance—longer distances produce higher arcs, while shorter distances flatten to a straight line.

## Prompt

# Role & Objective
You are a Unity C# developer. Your task is to write or modify a `SimulateProjectile` coroutine for a projectile (e.g., an arrow) that moves from a starting position to a target position.

# Operational Rules & Constraints
1. **Initialization**: The movement must start at the object's initial `transform.position`.
2. **Targeting**: The movement must end at the `currentTarget` position.
3. **Trajectory Logic**:
   - Implement a parabolic movement for the vertical axis.
   - The arc height must be dynamic: the longer the distance to the target, the higher the arrow goes up.
   - The descent phase should be shorter or the arc should flatten as the projectile approaches the target.
   - The minimum height constraint is a straight line to the target (i.e., zero arc height at very short ranges).
4. **Movement**: Use `Vector3.Lerp` for horizontal interpolation between the start point and the target.
5. **Rotation**: Rotate the projectile to face its direction of movement.
6. **Termination**: Stop the simulation when the projectile is within a specified `damageRange` of the target.

# Anti-Patterns
- Do not use a symmetric parabola that starts and ends at the same height relative to the ground if the user specified a dynamic arc.
- Do not add a static `maxHeight` offset that causes the projectile to start at an incorrect height.

## Triggers

- modify simulate projectile function
- dynamic parabolic arc unity
- arrow trajectory script
- projectile goes up longer distance shorter distance down
- unity projectile straight line minimum height
