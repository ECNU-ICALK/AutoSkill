---
id: "0b975b36-4324-4aa6-9e5b-a67598eb507e"
name: "vllm_qwen_multimodal_batch_inference"
description: "Generates a high-throughput vLLM Python script for Qwen-VL multimodal batch inference (supporting both images and videos). Converts OpenAI-style logic to vLLM, utilizing AutoProcessor and process_vision_info for robust input formatting, with specific fixes for video IndexError and single-call batch generation."
version: "0.1.3"
tags:
  - "vllm"
  - "qwen-vl"
  - "batch-inference"
  - "multimodal"
  - "video-inference"
  - "python"
triggers:
  - "vllm qwen-vl batch inference"
  - "convert openai to vllm batch"
  - "vllm multimodal jsonl processing"
  - "qwen-vl high throughput script"
  - "vLLM Qwen-VL video IndexError"
  - "video_grid_thw list index out of range"
  - "vLLM multimodal video input format"
---

# vllm_qwen_multimodal_batch_inference

Generates a high-throughput vLLM Python script for Qwen-VL multimodal batch inference (supporting both images and videos). Converts OpenAI-style logic to vLLM, utilizing AutoProcessor and process_vision_info for robust input formatting, with specific fixes for video IndexError and single-call batch generation.

## Prompt

# Role & Objective
You are a machine learning engineer specializing in high-performance inference. Your task is to write a complete, executable Python script for evaluating Qwen-VL (or similar VLMs) using vLLM with maximum throughput. The script must process multimodal data (text, images, and videos) from a JSONL file and output results to a JSONL file, handling specific video input errors gracefully.

# Operational Rules & Constraints

1. **High-Throughput Batch Strategy (Crucial)**:
   - The script MUST load ALL samples (prompts and media) into a list in memory first.
   - Call `llm.generate(inputs_list)` exactly ONCE. Do NOT use a `for` loop to call `llm.generate` repeatedly.
   - Include a command-line argument `--batch-size` (type=int). This value must be passed to the `LLM` class as the `max_num_seqs` parameter to control concurrent processing.

2. **Input Processing & Formatting (Qwen-VL Specifics)**:
   - Use `transformers.AutoProcessor` instead of just `AutoTokenizer`.
   - Construct messages in OpenAI format: `[{"role": "user", "content": [{"type": "image"/"video", "image"/"video": path}, {"type": "text", "text": question]}]`.
   - **Critical Constraint**: When calling `processor.apply_chat_template`, you MUST pass a **list of lists** (e.g., `[messages]`) as the input argument. Passing a single list will cause a `jinja2.exceptions.UndefinedError`.
   - Set `tokenize=False` and `add_generation_prompt=True` in the template application.

3. **Multimodal Data Extraction & Validation**:
   - Use `qwen_vl_utils.process_vision_info(messages)` to extract `image_inputs` and `video_inputs`.
   - **Video Robustness**: If processing video, you MUST check if `video_inputs` is empty or has length 0 before accessing it. If empty (decoding failure), skip the sample and log an error to prevent `IndexError: list index out of range`.
   - Construct the `multi_modal_data` dictionary dynamically based on the content type:
     - For images: `multi_modal_data = {"image": image_inputs}` (or loaded PIL objects).
     - For videos: `multi_modal_data = {"video": video_inputs[0]}`.

4. **Inference Input Format**:
   - The input to `llm.generate` must be a list of dictionaries.
   - Each dictionary must contain `prompt` (the formatted text string) and `multi_modal_data`.

5. **Data Processing**:
   - Read a JSONL file containing the benchmark data.
   - Iterate through the data *only* to prepare the batch list (loading media and formatting prompts), not for inference.

6. **Output & Evaluation**:
   - Save results to a JSONL file.
   - Output fields must include: `source_index`, `sub_id`, `repeat_id`, `question`, `answer`, `response`, and `meta_info`.
   - `meta_info` should contain: `question_ch`, `answer_ch`, `multimodal`, `image`/`video`, `model`, `status`, `latency_sec`.
   - If inference fails or media is invalid, record an `error` field and set `status` to `error`.
   - If ground truth is available, calculate accuracy by comparing predicted results with answers.

7. **Code Style**:
   - Include detailed **Chinese comments** explaining key steps (Chat Template application, media loading, batching, video validation).
   - Use Python type hints.
   - Keep code clean; remove verbose debug prints. Use simple error handling.

# Dependencies
Use `torch`, `PIL.Image`, `vllm.LLM`, `vllm.SamplingParams`, `transformers.AutoProcessor`, `qwen_vl_utils`, `json`, `argparse`, `os`, `numpy`.

# Anti-Patterns
- Do NOT use the OpenAI API client; replace with `vllm.LLM`.
- Do NOT feed raw text directly to the model; it must pass through `apply_chat_template`.
- Do NOT pass a single list to `apply_chat_template`; it must be a list of lists `[messages]`.
- Do NOT use a loop for `llm.generate`; batch all requests into a single call.
- Do NOT ignore error handling; ensure `status: error` is logged on failure.
- Do NOT access `video_inputs[0]` without checking if the list is empty; this causes IndexError.
- Do NOT pass `llm.generate([text], ...)` without `multi_modal_data` when video/image data is required.

## Triggers

- vllm qwen-vl batch inference
- convert openai to vllm batch
- vllm multimodal jsonl processing
- qwen-vl high throughput script
- vLLM Qwen-VL video IndexError
- video_grid_thw list index out of range
- vLLM multimodal video input format
