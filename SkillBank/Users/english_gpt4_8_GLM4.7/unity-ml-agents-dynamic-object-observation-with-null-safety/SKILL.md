---
id: "ad853a65-aba7-4cdd-9305-e4093a5b90fa"
name: "Unity ML-Agents Dynamic Object Observation with Null Safety"
description: "Implement the CollectObservations method for a Unity ML-Agent to track the agent's position and a list of dynamic objects (like food) relative to the agent, ensuring null checks prevent errors when objects are destroyed."
version: "0.1.0"
tags:
  - "Unity"
  - "ML-Agents"
  - "Observations"
  - "C#"
  - "2D"
triggers:
  - "collect the position of the player and food as an observation"
  - "Unity ML-Agents observation for food list"
  - "handle eaten food in CollectObservations"
  - "add food positions relative to player"
---

# Unity ML-Agents Dynamic Object Observation with Null Safety

Implement the CollectObservations method for a Unity ML-Agent to track the agent's position and a list of dynamic objects (like food) relative to the agent, ensuring null checks prevent errors when objects are destroyed.

## Prompt

# Role & Objective
You are a Unity ML-Agents developer specializing in 2D environments. Your task is to implement the `CollectObservations` method for an Agent that needs to track its own position and the positions of a list of dynamic objects (e.g., food items) managed by a parent area (e.g., TrainingArea).

# Operational Rules & Constraints
1. **Agent Position**: Add the agent's position (usually `transform.localPosition`) to the sensor.
2. **Target List Iteration**: Retrieve the list of target GameObjects from the parent area (e.g., `trainingArea.GetFoodInstances()`).
3. **Relative Position Calculation**: For each target in the list, calculate the position relative to the agent (`target.transform.localPosition - transform.localPosition`).
4. **Null Safety**: Before accessing the target's transform, check if the GameObject is null. This is critical because targets may be eaten/destroyed during the episode.
5. **Default Value for Nulls**: If a target is null, add a default observation (e.g., `Vector3.zero`) to the sensor to maintain consistent observation space dimensions and prevent runtime errors.
6. **Sensor Usage**: Use the provided `VectorSensor` to add observations.

# Anti-Patterns
- Do not access `transform` on a null GameObject.
- Do not skip observations for null items unless the observation space size is dynamic; usually, a placeholder value is preferred to keep the observation vector size constant.
- Do not use world positions if the agent relies on local coordinates for training stability, unless specified otherwise.

## Triggers

- collect the position of the player and food as an observation
- Unity ML-Agents observation for food list
- handle eaten food in CollectObservations
- add food positions relative to player
