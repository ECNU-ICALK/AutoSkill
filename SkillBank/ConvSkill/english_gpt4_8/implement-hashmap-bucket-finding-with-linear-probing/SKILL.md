---
id: "78e5959c-59c4-4098-8dd9-ab793bc2c878"
name: "Implement HashMap bucket finding with linear probing"
description: "Implement a method to find the next available bucket in a hash map using linear probing, handling collisions and wrap-around, without scanning the entire array."
version: "0.1.0"
tags:
  - "hashmap"
  - "linear probing"
  - "bucket finding"
  - "collision handling"
  - "C#"
triggers:
  - "Find bucket for key using linear probing"
  - "Implement hash map bucket method with linear probing"
  - "Create method to locate next available bucket"
  - "Handle collisions with linear probing in hash map"
  - "Return bucket index for key or next empty slot"
---

# Implement HashMap bucket finding with linear probing

Implement a method to find the next available bucket in a hash map using linear probing, handling collisions and wrap-around, without scanning the entire array.

## Prompt

# Role & Objective
You are implementing a hash map bucket-finding method. The method must locate the appropriate bucket for a given key using linear probing, returning the bucket index if the key exists or the next available slot.

# Communication & Style Preferences
- Use C# syntax consistent with the provided HashMap class.
- Do not loop from index 0 to array length; start probing from the computed start position.

# Operational Rules & Constraints
- Compute start bucket as Math.Abs(key.GetHashCode()) % this.Capacity.
- Probe linearly: for i from 0 to Capacity-1, bucket = (startPosition + i) % Capacity.
- Return bucket if Table[bucket] is null OR Table[bucket].Key.Equals(key).
- Throw an exception with message "No available bucket found." if no bucket is found after full cycle.
- Do not iterate through every entry from 0 to array length.

# Anti-Patterns
- Avoid scanning the entire table from index 0.
- Do not use separate chaining logic in this method; focus on linear probing.

# Interaction Workflow
1. Validate key is not null.
2. Compute start bucket.
3. Probe linearly with wrap-around.
4. Return appropriate bucket index or throw exception.

## Triggers

- Find bucket for key using linear probing
- Implement hash map bucket method with linear probing
- Create method to locate next available bucket
- Handle collisions with linear probing in hash map
- Return bucket index for key or next empty slot
