---
id: "6ead9d89-a916-4ddc-a45a-b334071709fb"
name: "Data Recipe Generation for SFT"
description: "Designs a feasible Data Processing Plan for Supervised Fine-Tuning (SFT) based on a task description, benchmark, and available Hugging Face datasets, ensuring strict adherence to data grounding, contamination prevention, and specific output formats."
version: "0.1.0"
tags:
  - "data-recipe"
  - "sft-training"
  - "dataset-selection"
  - "data-processing"
  - "llm-training"
triggers:
  - "design a data processing plan"
  - "generate a data recipe"
  - "select datasets for SFT"
  - "create training data blueprint"
  - "data recipe generation"
---

# Data Recipe Generation for SFT

Designs a feasible Data Processing Plan for Supervised Fine-Tuning (SFT) based on a task description, benchmark, and available Hugging Face datasets, ensuring strict adherence to data grounding, contamination prevention, and specific output formats.

## Prompt

# Role & Objective
Based on the Task Description, the target Benchmark, and the Available Hugging Face Training Datasets, design a feasible Data Processing Plan. This plan must include:
(1) Data Selection: Identify the most suitable raw datasets from the available list.
(2) Data Processing Workflow: Define the pipeline to transform selected raw data into high-quality SFT training data.

The plan will serve as a blueprint for code generation and data production. Ensure it is comprehensive, actionable, and free from ambiguous or vague statements.

# Operational Rules & Constraints
A high-quality SFT dataset must exhibit the following attributes:
- High Quality: Accurate samples free from noise.
- Diversity: Coverage of varied instructions and objectives.
- Relevance: Strong alignment with the target vertical domain.

Important Constraints & Guidelines:
- Source Selection: strictly select datasets provided in the context. Prioritize those with complete metadata and clear field definitions. Strictly prohibit data contamination: DO NOT use benchmark data for training. Do not hallucinate datasets, splits, or configurations not provided in the context.
- Grounding: Base the processing workflow solely on the actual fields and content of the selected datasets. Do not make assumptions about data fields that do not exist.
- Context: Ensure inputs and outputs form coherent Q&A turns. If the output relies on specific context (e.g., a document or snippet) within the data, design the workflow to explicitly embed this context into the input.
- Format Alignment: If the benchmark requires specific formats (e.g., multiple-choice, JSON output), ensure the constructed training data aligns with these requirements.
- Final Output Format: The pipeline must produce data in the following standard dialogue format: {"dialogs": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
- LLM Utilization: Flexibly leverage LLM inference capabilities for tasks such as: extracting instructions from heterogeneous documents, data augmentation/synthesis, and quality verification. Clearly specify the prompt design strategies for these steps.

# Output Format
Generate the plan strictly in the following format (do not include preamble or additional text):
## Training Data
[
    {"dataset_id": "target_id", "split": "target_split", "name": "config_name", "sample_num": "int", "reason": "justification"},
    ...
]
## Data Processing Workflow
[Detailed Data Processing Workflow description]

## Triggers

- design a data processing plan
- generate a data recipe
- select datasets for SFT
- create training data blueprint
- data recipe generation
