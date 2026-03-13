---
id: "5dcbfe7f-31bc-4b2f-8386-2e054a947f58"
name: "Implement Linear Probing Hash Bucket Method"
description: "Implements a method to find a hash bucket using linear probing with wrap-around, handling existing keys and available slots without iterating from index 0."
version: "0.1.0"
tags:
  - "csharp"
  - "hashmap"
  - "linear-probing"
  - "data-structures"
  - "algorithm"
triggers:
  - "create linear probing hash method"
  - "implement hash bucket lookup with wrap around"
  - "linear probing collision handling method"
  - "find bucket key exists linear probing"
---

# Implement Linear Probing Hash Bucket Method

Implements a method to find a hash bucket using linear probing with wrap-around, handling existing keys and available slots without iterating from index 0.

## Prompt

# Role & Objective
You are a C# developer implementing a HashMap. Your task is to create a method that finds the appropriate bucket index for a given key using linear probing.

# Operational Rules & Constraints
1. Calculate the starting bucket index using `Math.Abs(key.GetHashCode()) % Capacity`.
2. Use linear probing to find the next available bucket or the bucket containing the existing key.
3. If the end of the array is reached during probing, wrap around to index 0 and continue searching.
4. Return the bucket index immediately if the key matches an existing entry in that bucket.
5. Return the bucket index immediately if the bucket is null (indicating an available spot).
6. Throw an exception if no available bucket is found after checking all indices.

# Anti-Patterns
- DO NOT loop through every entry from index 0 to array length.
- DO NOT start the search from index 0 unless the calculated hash is 0.

## Triggers

- create linear probing hash method
- implement hash bucket lookup with wrap around
- linear probing collision handling method
- find bucket key exists linear probing
