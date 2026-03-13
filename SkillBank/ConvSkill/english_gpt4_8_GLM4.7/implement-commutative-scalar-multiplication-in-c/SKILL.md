---
id: "12826ea8-4e23-4662-a19f-d9df1b2dc148"
name: "Implement Commutative Scalar Multiplication in C++"
description: "Implements scalar multiplication for a custom C++ class to support both `Object * Scalar` and `Scalar * Object` syntax by defining a member function and a non-member friend function."
version: "0.1.0"
tags:
  - "c++"
  - "operator-overloading"
  - "scalar-multiplication"
  - "commutativity"
triggers:
  - "implement universal operator*"
  - "commutative scalar multiplication"
  - "make operator* work both ways"
  - "scalar * object syntax"
---

# Implement Commutative Scalar Multiplication in C++

Implements scalar multiplication for a custom C++ class to support both `Object * Scalar` and `Scalar * Object` syntax by defining a member function and a non-member friend function.

## Prompt

# Role & Objective
You are a C++ developer. Your task is to implement commutative scalar multiplication for a custom class. This means the multiplication operation should work regardless of whether the class instance or the scalar value is on the left-hand side of the operator.

# Operational Rules & Constraints
1. **Member Function**: Implement a member function `operator*(ScalarType)` within the class definition. This handles the case `Object * Scalar`.
2. **Non-Member Function**: Implement a non-member function `operator*(ScalarType, const Class&)` outside the class definition (usually in the same header file). This handles the case `Scalar * Object`.
3. **Delegation**: The non-member function should typically delegate to the member function (e.g., `return arr * num;`) to ensure consistent behavior and avoid code duplication, assuming the operation is commutative.
4. **Scope**: Ensure the non-member function is declared in the same scope as the class to allow Argument-Dependent Lookup (ADL).
5. **Const Correctness**: Ensure the member function is marked `const` if it does not modify the object.

# Anti-Patterns
- Do not rely on implicit conversions that might cause ambiguity.
- Do not implement the non-member function as a friend unless necessary for access to private members (though delegation to public member operator is preferred).

## Triggers

- implement universal operator*
- commutative scalar multiplication
- make operator* work both ways
- scalar * object syntax
