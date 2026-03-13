---
id: "a13e839f-3799-4050-b679-f64222dcd35c"
name: "data_processing_sop"
description: "General SOP for data processing, filtering, model inference, and segmentation tasks, including Huggingface dataset loading, script generation, and concurrent execution."
version: "0.1.6"
tags:
  - "data"
  - "filtering"
  - "concurrent"
  - "visual"
  - "reasoning"
  - "sop"
  - "huggingface"
  - "seg"
  - "mask"
triggers:
  - "Use when the user asks for a data processing or filtering process"
  - "Use when implementing concurrent model inference"
  - "Use when preparing visual or reasoning task prompts"
  - "Use when generating data processing scripts from Huggingface datasets"
  - "Use when handling segmentation or mask-related tasks"
  - "Use when you want to reuse a previously mentioned method/SOP"
examples:
  - input: "Break this into best-practice, executable steps."
  - input: "Break this into best-practice, executable steps for processing image data."
    output: "1) Data Filtering & Preparation\n   - background过滤\n   - 规则过滤\n   - VLM精细过滤\n   Status: Complete\n   Next: Environment Setup"
    notes: "Example of first step output"
  - input: "Generate a script to process this dataset, but only check 20 samples first."
    output: "1) Data Loading & Preparation\n   - Config: dataset_id='example', split='train', name='default'\n   - Action: Call load_remote_dataset with limit=20.\n   Status: Complete\n   Next: Environment Setup"
    notes: "Example of applying the 20-sample constraint"
---

# data_processing_sop

General SOP for data processing, filtering, model inference, and segmentation tasks, including Huggingface dataset loading, script generation, and concurrent execution.

## Prompt

Follow this SOP for data processing, filtering, model inference, and segmentation tasks (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):

1) Data Loading & Preparation
   - Define dataset configuration: `dataset_id`, `split`, `name` (config_name), `sample_num`, and `reason`.
   - Use `load_remote_dataset` to load data, ensuring correct `name` and `split` parameters are passed.
   - **Efficiency Constraint:** For feasibility verification, initially load only 20 samples to ensure script efficiency.
   - Apply filtering stages: Background filtering, Rule-based filtering, VLM fine-grained filtering.
   - Prepare data sources with proper JSON structure.

2) Environment Setup
   - import json, os, base64
   - from typing import List, Optional, Dict, Any, Tuple
   - import requests, re, tempfile, pandas as pd
   - from functools import partial
   - from tqdm import tqdm
   - from pathlib import Path
   - from .image_base import ImageBaseDataset
   - from .utils import build_judge, DEBUG_MESSAGE
   - from ..smp import *

3) Script Generation & Logic
   - Based on available Huggingface training data, the processing plan, and tool information, generate the executable data processing script.
   - **Segmentation Specifics:** If the task involves segmentation:
     - Generate reasoning for each mask (including 'all' and specific objects).
     - For single labels: Use simplified prompts to generate natural descriptions.
     - For multi-labels: Maintain original v2 logic.
   - **Language Requirement:** Output the script in English.
   - The script must clearly articulate the data processing logic and the logic for invoking tools.

4) Task-Specific Prompt Engineering
   - For visual tasks: Add "You may show your reasoning steps, but you must put ONLY your final answer within <answer></answer>" at the end of the prompt.
   - For reasoning tasks: Add "Please put your thinking and analysis procedure within <thinking></thinking> tags. Put ONLY your final answer within <answer></answer>".

5) Concurrent Processing Implementation
   - Modify code to support concurrent model calls.
   - Implement proper batching and parallel processing.

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a data processing or filtering process
- Use when implementing concurrent model inference
- Use when preparing visual or reasoning task prompts
- Use when generating data processing scripts from Huggingface datasets
- Use when handling segmentation or mask-related tasks
- Use when you want to reuse a previously mentioned method/SOP

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.

### Example 2

Input:

  Break this into best-practice, executable steps for processing image data.

Output:

  1) Data Filtering & Preparation
     - background过滤
     - 规则过滤
     - VLM精细过滤
     Status: Complete
     Next: Environment Setup

Notes:

  Example of first step output

### Example 3

Input:

  Generate a script to process this dataset, but only check 20 samples first.

Output:

  1) Data Loading & Preparation
     - Config: dataset_id='example', split='train', name='default'
     - Action: Call load_remote_dataset with limit=20.
     Status: Complete
     Next: Environment Setup

Notes:

  Example of applying the 20-sample constraint
