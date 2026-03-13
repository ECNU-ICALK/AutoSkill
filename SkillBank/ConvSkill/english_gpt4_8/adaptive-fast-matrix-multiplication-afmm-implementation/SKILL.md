---
id: "c913f8d5-b4d2-4ab5-86c8-f74f4fd4a347"
name: "Adaptive Fast Matrix Multiplication (AFMM) Implementation"
description: "Implement an adaptive matrix multiplication framework that analyzes matrix properties, selects optimal algorithms, and optionally applies dimensionality reduction for performance optimization."
version: "0.1.0"
tags:
  - "matrix multiplication"
  - "algorithm selection"
  - "performance optimization"
  - "linear algebra"
  - "adaptive computing"
triggers:
  - "implement adaptive matrix multiplication"
  - "create AFMM framework"
  - "optimize matrix multiplication algorithm selection"
  - "build dynamic matrix multiplication system"
  - "implement should_reduce_dim function"
---

# Adaptive Fast Matrix Multiplication (AFMM) Implementation

Implement an adaptive matrix multiplication framework that analyzes matrix properties, selects optimal algorithms, and optionally applies dimensionality reduction for performance optimization.

## Prompt

# Role & Objective
You are implementing the Adaptive Fast Matrix Multiplication (AFMM) framework. Your goal is to create a modular system that analyzes input matrices, selects the most efficient multiplication algorithm based on their characteristics, and optionally applies dimensionality reduction when beneficial.

# Communication & Style Preferences
- Provide clear, well-commented Python code.
- Use NumPy for matrix operations and SciPy for sparse matrices when needed.
- Include docstrings for all functions explaining parameters and return values.

# Operational Rules & Constraints
1. analyze_matrices(A, B) must:
   - Calculate sparsity for both matrices (nonzero count / total elements)
   - Check if matrices are symmetric using np.allclose
   - Verify if matrices are square
   - Return a dictionary with keys: 'sparsity_A', 'sparsity_B', 'symmetric_A', 'symmetric_B', 'square'

2. select_algorithm(characteristics) must:
   - Use sparsity threshold of 0.1 to decide sparse vs dense
   - For sparse matrices (both sparsity < 0.1), return a sparse matrix multiplication function
   - For symmetric square matrices, return Strassen's algorithm
   - For dense square matrices, return Strassen's algorithm
   - Default to np.dot for other cases

3. should_reduce_dim(characteristics) must:
   - Use SIZE_THRESHOLD = 1000 for matrix size consideration
   - Use SPARSITY_THRESHOLD = 0.1
   - Return True only if matrices are large enough and not too sparse
   - Include size_A and size_B in characteristics (matrix element count)

4. AFMM(A, B) must:
   - Follow the 4-step workflow: analyze, select, optionally reduce, compute
   - Handle dimensionality reduction if should_reduce_dim returns True
   - Return the final matrix product

# Anti-Patterns
- Do not hardcode matrix values; keep functions generic
- Do not use external libraries beyond NumPy and SciPy
- Do not implement actual dimensionality reduction; leave as placeholder
- Do not assume matrix dimensions; work with any compatible sizes

# Interaction Workflow
1. First implement analyze_matrices
2. Then implement select_algorithm with appropriate algorithm selection logic
3. Then implement should_reduce_dim with size and sparsity checks
4. Finally implement AFMM that orchestrates these components

## Triggers

- implement adaptive matrix multiplication
- create AFMM framework
- optimize matrix multiplication algorithm selection
- build dynamic matrix multiplication system
- implement should_reduce_dim function
