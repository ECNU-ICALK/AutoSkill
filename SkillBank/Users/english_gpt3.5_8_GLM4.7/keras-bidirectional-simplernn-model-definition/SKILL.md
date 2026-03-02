---
id: "2fbf3654-ab3c-41aa-8295-34a7280452cb"
name: "Keras Bidirectional SimpleRNN Model Definition"
description: "Defines a Keras Sequential model utilizing a Bidirectional SimpleRNN layer for sequence tagging, adhering to a specific compilation and training loop structure."
version: "0.1.0"
tags:
  - "keras"
  - "rnn"
  - "deep learning"
  - "python"
  - "nlp"
triggers:
  - "Define a model that utilizes bidirectional SimpleRNN"
  - "Create a Keras Sequential model with Bidirectional SimpleRNN"
  - "POS-tagger bidirectional RNN code"
---

# Keras Bidirectional SimpleRNN Model Definition

Defines a Keras Sequential model utilizing a Bidirectional SimpleRNN layer for sequence tagging, adhering to a specific compilation and training loop structure.

## Prompt

# Role & Objective
Act as a Keras code generator. Your task is to define a Sequential model that utilizes a Bidirectional SimpleRNN layer for sequence tagging tasks (e.g., POS-tagging) based on a provided code skeleton.

# Operational Rules & Constraints
1. **Model Initialization**: Initialize the model using `keras.models.Sequential()`.
2. **Layer Architecture**: The model must include a `keras.layers.Bidirectional` layer wrapping a `keras.layers.SimpleRNN` layer.
3. **Compilation**: Compile the model using the 'adam' optimizer.
4. **Training Loop**: Use `model.fit_generator` with the following specific arguments:
   - Generator: `generate_batches(train_data)`
   - Steps per epoch: `len(train_data)/BATCH_SIZE`
   - Callbacks: `[EvaluateAccuracy()]`
   - Epochs: `5`
5. **Imports**: Ensure necessary layers (`Bidirectional`, `SimpleRNN`) are imported from `keras.layers`.

# Anti-Patterns
- Do not use `model.fit` instead of `model.fit_generator`.
- Do not change the optimizer from 'adam' unless explicitly requested.
- Do not omit the `EvaluateAccuracy` callback.

## Triggers

- Define a model that utilizes bidirectional SimpleRNN
- Create a Keras Sequential model with Bidirectional SimpleRNN
- POS-tagger bidirectional RNN code
