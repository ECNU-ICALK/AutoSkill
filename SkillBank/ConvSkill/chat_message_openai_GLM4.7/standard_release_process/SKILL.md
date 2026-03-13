---
id: "f240a45b-df34-414f-af5c-20b59feb31b5"
name: "standard_release_process"
description: "Comprehensive SOP for release processes covering cluster setup (Ray), data synchronization (rsync), and pattern execution (controller)."
version: "0.1.2"
tags:
  - "dict"
  - "if"
  - "str"
  - "echo"
  - "router"
  - "model"
  - "pid"
  - "taskrunner"
  - "1139809"
triggers:
  - "Use when the user asks for a process or checklist."
  - "Use when you want to reuse a previously mentioned method/SOP."
examples:
  - input: "Break this into best-practice, executable steps."
---

# standard_release_process

Comprehensive SOP for release processes covering cluster setup (Ray), data synchronization (rsync), and pattern execution (controller).

## Prompt

Follow this SOP (replace specifics with placeholders like <PROJECT>/<ENV>/<VERSION>):

## Phase 0: Cluster & Environment Setup
1) Start a local ray head (node-local) on each node to avoid cross-node scheduling.
2) Configure Ray environment variables:
   - `RAY_PORT="${RAY_PORT:-6379}"`
   - `READY_TIMEOUT_SEC="${READY_TIMEOUT_SEC:-240}"`
   - `READY_POLL_INTERVAL_SEC="${READY_POLL_INTERVAL_SEC:-2}"`
3) Perform healthcheck.
4) Generate derived config.
5) Validate hardware configuration:
   - Check if `(( NPROC_PER_NODE % ENGINE_TP != 0 ))`
   - If true, echo "[FATAL] NPROC_PER_NODE=${NPROC_PER_NODE} must be divisible by ENGINE_TP=${ENGINE_TP}" and exit 1.

## Phase 1: Data Synchronization (Shared /nvme)
6) Avoid concurrent rsync writes on shared /nvme.
7) Strategy: Wait if another task is copying (lock occupied).
8) Wait for `.cargoflow_complete` to avoid duplicate rsync.
9) Only attempt takeover (lock snatching) after timeout.
10) Verify directory availability: `config.json` + `.cargoflow_complete` must exist.
11) Define environment variables:
   - `COMPLETE_MARK="$NVME_MODEL_PATH/.cargoflow_complete"`
   - `COPYING_MARK="$NVME_MODEL_PATH/.cargoflow_copying"`
   - `NVME_COPY_WAIT_TIMEOUT="${NVME_COPY_WAIT_TIMEOUT:-60}"` (seconds)
   - `NVME_COPY_WAIT_INTERVAL="${NVME_COPY_WAIT_INTERVAL:-1}"` (seconds)
   - `LOCK_DIR="/nvme/.cargoflow_locks"`

## Phase 2: Execution Workflow
12) List[List[episode]]
13) Run only one pattern at a time.
14) Write the pattern's 1D `initial_flat.json` to `output_dir/pattern_xxxxx/_work`.
15) Set `OPENEOLVE_INITIAL_PATH` to point to that file.
16) (Optional) Set pattern-specific `OPENEOLVE_DUMP_DIR` to avoid prompt dump confusion.
17) Start `ProcessParallelController` (worker inherits env).
18) Stop after completion, then proceed to the next pattern.

## Phase 3: Metadata & Fixes
19) Enable Checkpoint support.
20) Apply Key fixes.
21) During seeding, save the Bootcamp original long prompt (`template_input.messages[0].content`) to `metadata["bootcamp_user_prompt"]`.

For each step, include: action, checks, and failure rollback/fallback plan.
Output format: for each step number, provide status/result and what to do next.

## Triggers

- Use when the user asks for a process or checklist.
- Use when you want to reuse a previously mentioned method/SOP.

## Examples

### Example 1

Input:

  Break this into best-practice, executable steps.
