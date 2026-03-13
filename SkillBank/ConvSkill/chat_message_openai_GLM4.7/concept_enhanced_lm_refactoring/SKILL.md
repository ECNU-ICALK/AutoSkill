---
id: "607053f2-a8d8-412e-bd63-36992e6362e4"
name: "concept_enhanced_lm_refactoring"
description: "Refactor Hugging Face multimodal models (e.g., LLaVA) into concept-enhanced language models by replacing vision encoders with sentence encoders (e.g., SONAR) and updating token processing logic."
version: "0.1.1"
tags:
  - "CDD"
  - "concept embedding"
  - "SONAR"
  - "huggingface"
  - "transformers"
  - "PyTorch"
  - "model refactoring"
  - "token replacement"
triggers:
  - "implement CDD model"
  - "create CDD model"
  - "refactor multimodal model to concept model"
  - "replace vision encoder with concept encoder"
  - "generate modeling file"
  - "concept-driven decoder"
examples:
  - input: "[concept1_text] [concept2_text] ... [conceptN_text] [concept_token] [concept_token] ...]"
    output: "[concept1_text] [concept2_text] ... [conceptN_text] [concept_feat1] [concept_feat2] ...]"
---

# concept_enhanced_lm_refactoring

Refactor Hugging Face multimodal models (e.g., LLaVA) into concept-enhanced language models by replacing vision encoders with sentence encoders (e.g., SONAR) and updating token processing logic.

## Prompt

# Role & Objective
You are an expert in Hugging Face Transformers architecture. Your task is to generate a new concept-enhanced language model file (e.g., `modeling_cdd.py`) based on a provided multimodal model template (such as LLaVA).

# Constraints & Style
- Use standard Hugging Face Transformers code style and naming conventions.
- Maintain a clear code structure, including necessary imports, output class definitions, helper functions, and the model class.
- Retain existing diffusion training logic (e.g., `add_noise_for_packed_bd`, `block_diff_mask`).

# Core Workflow
1. **Component Renaming & Replacement**:
   - Replace `vision_tower` with `concept_encoder` (e.g., using a SONAR model).
   - Replace `multi_modal_projector` with `concept_projector`.
   - Replace `image_token_id` with `concept_token_id`.
   - Replace `image_hidden_states` / `video_hidden_states` with `concept_hidden_states`.
   - Remove the `LlavaOnevisionPooler` class.

2. **Input/Output Modifications**:
   - Remove input parameters related to the original modality (images/videos), such as `pixel_values`, `image_sizes`, `pixel_values_videos`, `image_sizes_videos`.
   - Add input parameters for the new modality, such as `concept_input_ids`, `concept_attention_mask`.
   - In the `forward` method, process inputs using the new modality's encoder, project them, and use `masked_scatter` to replace tokens at `concept_token_id` positions with the projected embeddings.

3. **Code Cleanup**:
   - Remove methods specific to the old modality (e.g., `pack_image_features`, `get_image_features`, `get_video_features`, `unpad_image`, `apply_pooling`, `get_num_patches`).
   - Retain shared logic (e.g., diffusion training helpers `add_noise_for_packed_bd`, `block_diff_mask`, `block_attn_mask`, `calculate_token_nums`, `prepare_for_bd_training`).
   - Retain position ID processing logic (e.g., `update_packed_position_ids`).

4. **Configuration Assumptions**:
   - Assume the existence of `NewModelConfig`, which includes `concept_config` and `text_config`.
   - Assume `concept_config` includes `hidden_size` and `model_name`.

5. **Output Structure**:
   - Maintain the standard Hugging Face structure: `NewModelPreTrainedModel`, `NewModel`, `NewModelForConditionalGeneration`.
   - Update output dataclasses (`BaseModelOutputWithPast` and `CausalLMOutput`) to reflect `concept_hidden_states`.

# Anti-Patterns
- Do not retain any logic related to image resolution, grid points, or video frames.
- Do not hardcode specific model names (like "CDD" or "LLaVA") in the prompt unless used as examples.
- Ensure all calls to `select_best_resolution` are removed.

## Triggers

- implement CDD model
- create CDD model
- refactor multimodal model to concept model
- replace vision encoder with concept encoder
- generate modeling file
- concept-driven decoder

## Examples

### Example 1

Input:

  [concept1_text] [concept2_text] ... [conceptN_text] [concept_token] [concept_token] ...]

Output:

  [concept1_text] [concept2_text] ... [conceptN_text] [concept_feat1] [concept_feat2] ...]
