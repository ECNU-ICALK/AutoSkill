---
id: "26cc6ddd-c279-4575-be5f-59d581a9ac57"
name: "standard_release_process"
description: "SOP for executing standard release and evaluation workflows, covering Bootcamp data extraction, reward computation, Verl/Taskrunner environment configuration, actor response dumping, KL penalty logic, gene/parameter structure handling, and specific ACS debugging environment setup."
version: "0.1.8"
tags:
  - "sop"
  - "release"
  - "evaluation"
  - "bootcamp"
  - "data_processing"
  - "reward_logic"
  - "pid"
  - "taskrunner"
  - "verl"
  - "dumping"
  - "gene_display"
  - "acs_debug"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
  - "Use when configuring environment variables for ACS or debugging."
examples:
  - input: "Break this into best-practice, executable steps."
---

# standard_release_process

SOP for executing standard release and evaluation workflows, covering Bootcamp data extraction, reward computation, Verl/Taskrunner environment configuration, actor response dumping, KL penalty logic, gene/parameter structure handling, and specific ACS debugging environment setup.

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):

# Prerequisites
import logging
import random
import json
import os

# Context & Evidence
1) Use the user questions below as the PRIMARY extraction evidence.
2) Use the full conversation below as SECONDARY context reference.
3) In the full conversation section, assistant/model replies are reference-only and not skill evidence.

# Environment Configuration (ACS/Debug Specifics)
If the context involves ACS evolution or specific debugging setups:
1) Enable prompt dumping but delegate directory control to `run_acs_evolution.py` (do not fix a global directory).
2) `export OPENEOLVE_DUMP_PROMPT=0` (Disable global default to allow script-level control).
3) `unset OPENEOLVE_DUMP_DIR` (Prevent mixing dumps from different patterns).
4) `unset OPENEOLVE_DUMP_PROMPT_ONCE` (Ensure dumping occurs on every iteration for debugging).
5) `export OPENEOLVE_OUTPUT_DIR="${OUTDIR}"` (Provide fallback dump location).
6) Optional: `export OPENEOLVE_ACS_DEBUG=1`.

# Core Workflow (Bootcamp/Evaluation)
1) Read program json.
2) **Handle initial.json Format**:
   - Determine if `initial.json` is 2D (List[List[episode]]) or 1D (List[episode]).
   - Extract `base_prompt_for_evolve` (canonical bootcamp_user_prompt).
   - Extract `initial_parameters` (canonical gene, never split).
3) **Gene Structure, Display & Parameter Updates**:
   - **Display Logic**: For all programs used for prompt display (top/diverse/inspirations/previous_programs), prioritize `program.metadata.gene` (or `_gene`/`gene` in code) over `program.code`. The prompt should show the gene trajectory, not a single variables dict.
   - **State Handling**: For `current_program`/`parent_program` (state json strings), if a gene field exists, prioritize displaying a gene summary (turn count, last round parameter example) in simplified views.
   - **Initial Program**: Keep `initial_program` as is (do not force gene injection if the initial JSON lacks it).
   - **Structure Alignment**: Ensure gene structure aligns with OpenEvolve parameter update architecture. Move `parameter_relation_code` into the `variables` field if it requires updates. Remove `idx` fields. Optionally retain `comment` fields.
4) Use initial.json's template_input/ground_truth to build Bootcamp dataset.jsonl.
5) Write "current parameter values" into the prompt text (format: top-level prompt, no exposed variables field).
6) Call internbootcamp.utils.run_evaluation.
7) Read back eval_results_*.jsonl.
8) Process score/res/extracted_output using the following specific logic:
   - Initialize `geo3k_judger_config = GEO3KJudgerConfig`.
   - Setup `judger_cfg = JudgerConfig(reward_judger_configs=[geo3k_judger_config])`.
   - Define `compute_reward(response: str, label: str, extra_info: Dict[str, Any]) -> Dict[str, float]`.
   - Extract parameters: `format_score = float(extra_info.get("format_score", 0.1))`, `use_boxed = bool(extra_info.get("use_boxed", True))`, `question_type = extra_info.get("question_type", "auto")`.
   - Calculate accuracy: `acc = acc_reward(response, label, use_boxed=use_boxed, question_type=question_type)`.
   - Calculate format: `fmt = format_reward(response, question_type=question_type, ground_truth=label)`.
   - **Critical Fix:** Calculate final score ensuring multiplication: `score = (1.0 - format_score) * acc + format_score * fmt`.
9) Return metrics to OpenEvolve.
10) Handle new additions.
11) If environment variable OPENEOLVE_DISABLE_EVAL_DUMP=1, write dataset/output_dir to a temporary directory.

# Configuration & Dumping Logic (Internal)
If the context involves actor response or prompt dumping configuration:
1) **Determine Dump Switches**:
   - Check `OPENEOLVE_DUMP_ACTOR_RESPONSE` env var (default "1"). Set `self.dump_actor_response` to False if value is in ("0", "", "false", "False").
   - Check `OPENEOLVE_DUMP_ACTOR_PROMPT` env var (default "1"). Set `self.dump_actor_prompt` to False if value is in ("0", "", "false", "False").
2) **Determine Dump Directory**:
   - Check `OPENEOLVE_ACTOR_DUMP_DIR` env var. If set and stripped, use as `dump_base`.
   - Else, check `self.config.log_dir`. If exists, use as `dump_base`.
   - Else, `dump_base` remains None (handle fallback).

# Training Loop Logic (KL Penalty)
If the context involves KL penalty application in the training loop:
1) **Reward Phase** (`algorithm.use_kl_in_reward`):
   - Add KL penalty directly to the reward before calculating advantage.
   - Call chain reference: `ray_trainer.py:1689` -> `apply_kl_penalty` -> `core_algos.kl_penalty`.
2) **Actor Loss Phase** (`actor.use_kl_loss`):
   - Add KL loss as an extra term to the total policy loss.
   - Call chain reference: `ray_trainer.py:1778` -> `_update_actor` -> `dp_actor.py:640`.

# Context-Specific Logic (Verl/Taskrunner)
If the context involves Verl or Taskrunner configurations:
1) Handle padding logic (determine size_divisor).
2) Check if `async_rollout_manager` is not None.
3) For async mode, get `num_workers` from the manager (`size_divisor = getattr(async_rollout_manager, 'num_workers', 8)`).
4) For sync mode, use `world_size` from worker group (`size_divisor = getattr(actor_rollout_wg, 'world_size', 8)`).

# Output Requirements
For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.
- Use when configuring environment variables for ACS or debugging.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
