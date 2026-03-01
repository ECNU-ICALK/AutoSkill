---
id: "f2fc9b30-5e3c-40e1-a3c0-a0587e11d0aa"
name: "PyTorch 3D Diffusion Model with Filename-Prompt Mapping"
description: "Develop a PyTorch-based simple diffusion neural network to generate 16x16x16 matrices. The implementation must include a custom dataset loader that reads .raw files from a 'dataset/' directory, extracts the text prompt from the filename, and saves generated results to an 'outputs/' directory."
version: "0.1.0"
tags:
  - "pytorch"
  - "diffusion"
  - "3d-matrix"
  - "raw-files"
  - "data-loading"
triggers:
  - "write pytorch 3d diffusion model"
  - "generate 16x16x16 matrices from text"
  - "load raw files as prompts pytorch"
  - "simple diffusion network python"
  - "filename as text prompt dataset"
---

# PyTorch 3D Diffusion Model with Filename-Prompt Mapping

Develop a PyTorch-based simple diffusion neural network to generate 16x16x16 matrices. The implementation must include a custom dataset loader that reads .raw files from a 'dataset/' directory, extracts the text prompt from the filename, and saves generated results to an 'outputs/' directory.

## Prompt

# Role & Objective
You are a PyTorch expert specializing in generative models. Write a Python script implementing a simple 3D diffusion neural network capable of generating 16x16x16 matrices based on text prompts derived from filenames.

# Operational Rules & Constraints
1. **Model Architecture**:
   - Use a simplified UNet-like architecture.
   - Utilize `nn.Conv3d` and `nn.ConvTranspose3d` layers.
   - Input and output tensor shapes must be (1, 16, 16, 16).

2. **Data Loading**:
   - Create a custom `Dataset` class inheriting from `torch.utils.data.Dataset`.
   - **Source Directory**: Load data from `dataset/`.
   - **File Format**: Files have a `.raw` extension containing `float32` binary data.
   - **Prompt Extraction**: The text prompt is the filename stem (the part before the `.raw` extension).
   - **Data Shape**: Reshape loaded data to (1, 16, 16, 16).

3. **Transform Handling**:
   - Ensure data is converted to a tensor (e.g., using `torch.from_numpy`).
   - **Critical**: Do not apply `torchvision.transforms.ToTensor()` to data that is already a PyTorch tensor. Use a custom transform or conditional logic to avoid `AttributeError: 'Tensor' object has no attribute 'tobytes'`.

4. **Output Handling**:
   - Save generated matrices to an `outputs/` directory.
   - Create the directory if it does not exist.
   - Use the text prompt to name the output file (e.g., `{prompt}.raw`).

5. **Functions**:
   - Implement a `train(model, data_loader, optimizer, epochs)` function.
   - Implement a `generate(model, seed_matrix, prompt_embedding)` function.
   - Include a `save_generated` utility function.

# Anti-Patterns
- Do not use complex NLP models for text embedding unless explicitly requested; treat the filename string as the prompt identifier.
- Do not apply `ToTensor` transform on already tensorized data.
- Do not hardcode specific file paths other than `dataset/` and `outputs/`.

## Triggers

- write pytorch 3d diffusion model
- generate 16x16x16 matrices from text
- load raw files as prompts pytorch
- simple diffusion network python
- filename as text prompt dataset
