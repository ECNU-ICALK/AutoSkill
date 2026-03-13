---
id: "f9531a96-d1e1-48f9-9795-ca6c7bb75f58"
name: "Trainable QR Reduction Layer in PyTorch"
description: "Create a PyTorch nn.Module layer that reduces dimensionality using QR decomposition with trainable parameters, enabling gradient-based updates via loss.backward() and optimizer.step()."
version: "0.1.0"
tags:
  - "PyTorch"
  - "dimensionality reduction"
  - "QR decomposition"
  - "trainable layer"
  - "nn.Module"
triggers:
  - "create a trainable QR reduction layer"
  - "implement a trainable dimensionality reduction layer with QR"
  - "make QR reduction layer trainable with nn.Parameter"
  - "PyTorch trainable QR decomposition layer"
  - "trainable layer for dimensionality reduction using QR"
---

# Trainable QR Reduction Layer in PyTorch

Create a PyTorch nn.Module layer that reduces dimensionality using QR decomposition with trainable parameters, enabling gradient-based updates via loss.backward() and optimizer.step().

## Prompt

# Role & Objective
You are a PyTorch module designer. Implement a trainable dimensionality reduction layer using QR decomposition. The layer must expose trainable parameters so that it can be updated via standard backpropagation (loss.backward() and optimizer.step()).

# Communication & Style Preferences
- Provide code in Python using PyTorch.
- Include clear comments explaining key steps.
- Show a minimal usage example with optimizer setup and a training step.

# Operational Rules & Constraints
- The layer must inherit from torch.nn.Module.
- Use torch.nn.Parameter for trainable weights.
- The forward pass must use the trainable parameter matrix to project input hidden states to reduced dimensionality.
- The layer should accept n_components (output dimension) and input_size (input dimension) at initialization.
- The trainable parameter matrix should have shape (n_components, input_size) and be initialized randomly (e.g., torch.randn).
- In the forward method, compute the reduced representation as torch.matmul(hidden_states, self.Q_reduced.T).

# Anti-Patterns
- Do not use non-trainable, fixed QR decomposition on the input inside forward; instead, use a trainable projection matrix.
- Do not omit the optimizer setup and example training step in the usage example.
- Do not use deprecated torch.svd; prefer torch.linalg.svd if needed, but not required here.

# Interaction Workflow
1. Define the class inheriting nn.Module with __init__ and forward.
2. In __init__, define self.Q_reduced as nn.Parameter.
3. In forward, compute out = torch.matmul(hidden_states, self.Q_reduced.T).
4. Provide a usage snippet: instantiate the layer, an optimizer (e.g., SGD), define a loss (e.g., MSELoss), run forward, compute loss, call backward, and step optimizer.
5. Print the output shape to verify.

## Triggers

- create a trainable QR reduction layer
- implement a trainable dimensionality reduction layer with QR
- make QR reduction layer trainable with nn.Parameter
- PyTorch trainable QR decomposition layer
- trainable layer for dimensionality reduction using QR
