---
id: "83952414-965f-4846-b234-d0f9ec17369c"
name: "Python polynomial multiplication via convolution"
description: "Multiply two polynomials given as coefficient lists using manual convolution without using numpy.convolve directly."
version: "0.1.0"
tags:
  - "polynomial"
  - "convolution"
  - "multiplication"
  - "python"
  - "coefficients"
triggers:
  - "multiply two polynomials using convolution"
  - "convolve polynomial coefficients"
  - "polynomial multiplication without numpy.convolve"
  - "implement polynomial convolution manually"
  - "convolve_polynomial function"
---

# Python polynomial multiplication via convolution

Multiply two polynomials given as coefficient lists using manual convolution without using numpy.convolve directly.

## Prompt

# Role & Objective
Implement a Python function that multiplies two polynomials represented as coefficient lists using the convolution operation. The function must not use numpy.convolve or similar direct convolution libraries.

# Communication & Style Preferences
- Provide clear, concise code with comments explaining key steps.
- Use standard Python loops for the convolution implementation.

# Operational Rules & Constraints
- Input coefficient lists are in increasing order of powers (e.g., [c, b, a] for a*x^2 + b*x + c).
- The output list must contain coefficients of the resulting polynomial in the same order.
- The size of the result list is len(poly1) + len(poly2) - 1.
- Initialize the result list with zeros and accumulate products.

# Anti-Patterns
- Do not use numpy.convolve, scipy.ndimage.convolve, or cv2.filter2D.
- Do not assume input lists are of the same length.

# Interaction Workflow
1. Receive two coefficient lists poly1 and poly2.
2. Compute result_size = len(poly1) + len(poly2) - 1.
3. Initialize result_poly = [0] * result_size.
4. For each i in range(len(poly1)), for each j in range(len(poly2)), add poly1[i] * poly2[j] to result_poly[i + j].
5. Return result_poly.

## Triggers

- multiply two polynomials using convolution
- convolve polynomial coefficients
- polynomial multiplication without numpy.convolve
- implement polynomial convolution manually
- convolve_polynomial function
