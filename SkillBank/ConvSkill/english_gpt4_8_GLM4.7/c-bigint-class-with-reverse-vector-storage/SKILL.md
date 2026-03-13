---
id: "eb42a6f3-fd49-4c7f-9532-3b89d9750687"
name: "C++ BigInt Class with Reverse Vector Storage"
description: "Implement a C++ BigInt class for arbitrarily large integers using a vector of digits stored in reverse order (least significant digit first). The class must support construction from string, conversion to string, and addition."
version: "0.1.0"
tags:
  - "c++"
  - "bigint"
  - "vector"
  - "data-structures"
  - "algorithms"
triggers:
  - "create a BigInt class in C++"
  - "implement big integer using vector"
  - "C++ reverse vector number storage"
  - "BigInt addition with carry"
---

# C++ BigInt Class with Reverse Vector Storage

Implement a C++ BigInt class for arbitrarily large integers using a vector of digits stored in reverse order (least significant digit first). The class must support construction from string, conversion to string, and addition.

## Prompt

# Role & Objective
You are a C++ developer tasked with implementing a BigInt class to handle arbitrarily large integers that exceed standard type limits.

# Operational Rules & Constraints
1. **Data Structure**: Use `std::vector<int>` to store individual digits of the number.
2. **Storage Order**: Store digits in **reverse order** (least significant digit at index 0). For example, the integer 321 must be stored as `{1, 2, 3}`.
3. **Class Interface**: You must implement the class with the following specific structure:
   ```cpp
   class BigInt {
   public:
       BigInt(std::string s); // convert string to BigInt
       std::string to_string() const; // get string representation
       void add(BigInt b); // add another BigInt to this one
   private:
       std::vector<int> digits;
   };
   ```
4. **Constructor Logic**: In `BigInt(std::string s)`, iterate through the input string from the last character to the first. Convert each character to an integer digit using `static_cast<int>(s[i] - '0')` and push it into the `digits` vector.
5. **String Conversion Logic**: In `to_string() const`, iterate through the `digits` vector in reverse (using reverse iterators `rbegin` and `rend`) to construct the output string so the most significant digit appears first.
6. **Addition Logic**: Implement the `add(BigInt b)` method to perform long addition. Handle carry propagation correctly. Ensure the `digits` vector grows if a final carry remains after processing the most significant digit.

# Anti-Patterns
- Do not store digits in standard order (most significant digit first).
- Do not use standard integer types (int, long long) to store the full number value.
- Do not omit the `const` qualifier on the `to_string` method.

## Triggers

- create a BigInt class in C++
- implement big integer using vector
- C++ reverse vector number storage
- BigInt addition with carry
