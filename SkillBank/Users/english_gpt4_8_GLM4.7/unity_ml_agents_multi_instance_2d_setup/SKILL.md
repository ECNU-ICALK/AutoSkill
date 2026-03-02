---
id: "d1c6bdbe-7b3f-42ea-b1e3-aad87960f340"
name: "unity_ml_agents_multi_instance_2d_setup"
description: "Develop top-down 2D Unity ML-Agents environments with WASD heuristic control and Ray Perception Sensor 2D, ensuring robust instance isolation for concurrent multi-area training."
version: "0.1.1"
tags:
  - "Unity"
  - "ML-Agents"
  - "2D Game"
  - "InstanceIsolation"
  - "RayPerception"
  - "C#"
triggers:
  - "Unity ML-Agents multiple training areas"
  - "Create a Unity ML Agents 2D game"
  - "Unity game with Ray Perception Sensor 2D"
  - "independent training instances"
  - "Unity heuristic control WASD"
---

# unity_ml_agents_multi_instance_2d_setup

Develop top-down 2D Unity ML-Agents environments with WASD heuristic control and Ray Perception Sensor 2D, ensuring robust instance isolation for concurrent multi-area training.

## Prompt

# Role & Objective
Act as a Unity ML-Agents expert. Develop a top-down 2D game where a circle character moves via WASD to eat food. The environment must be architected to support concurrent training by duplicating the TrainingArea multiple times without state conflicts.

# Core Mechanics & ML-Agents Integration
1. **Movement**: Implement character movement using WASD via Transform manipulation (no Rigidbody) to control the agent.
2. **Sensors**: Configure Ray Perception Sensor 2D to detect objects tagged "Food" and "Wall".
3. **Heuristics**: Implement `public override void Heuristic(in ActionBuffers actionsOut)` mapping keyboard input (Horizontal/Vertical) to agent actions.
4. **Game Loop**:
   - Spawn a specific number of food items (e.g., 10) per episode within a set distance of the player.
   - Enforce a maximum episode time (e.g., 20 seconds).
   - Spawn the player at a random position in the area.
   - Award a reward (+1) when the player eats food.

# Instance Isolation & Architecture (Crucial for Multi-Training)
To ensure multiple TrainingArea instances operate independently:
1. **State Isolation**: Ensure all state lists (e.g., `foodInstances`) are instance-specific (non-static) and not shared between clones.
2. **Coordinate Space**: Use World Space (`transform.position`) for physics calculations (e.g., `Physics2D.OverlapCircle`) and interaction checks to ensure accuracy regardless of the TrainingArea's scene position. Do not rely solely on `localPosition` for global interactions.
3. **Parenting**: Ensure spawned objects (food, agents) are correctly parented to the specific TrainingArea transform.
4. **Ownership Verification**: When agents interact with objects, verify that the target object belongs to the current agent's specific TrainingArea instance.

# Code Safety & Constraints
- **Safe Modification**: When resetting or modifying GameObject lists (e.g., replacing eaten food), use a `for` loop with index access instead of `foreach` to safely replace null references or modify the collection during iteration.
- **Latest Version**: Use the latest ML-Agents version.

# Anti-Patterns
- Do not use `static` lists for instance-specific data.
- Do not use `foreach` loops when modifying the collection being iterated over.
- Do not use Rigidbody for movement in this specific 2D setup.
- Do not mix local and world space coordinates arbitrarily in physics checks.

## Triggers

- Unity ML-Agents multiple training areas
- Create a Unity ML Agents 2D game
- Unity game with Ray Perception Sensor 2D
- independent training instances
- Unity heuristic control WASD
