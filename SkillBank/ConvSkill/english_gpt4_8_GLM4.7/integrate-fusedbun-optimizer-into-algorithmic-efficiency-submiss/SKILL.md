---
id: "e0fc8131-29a0-448d-9d91-5d19e0606596"
name: "Integrate Fusedbun Optimizer into Algorithmic Efficiency Submission"
description: "Replaces the AdamW optimizer in a PyTorch submission file with the custom Fusedbun optimizer, mapping specific hyperparameters and removing the warmup phase from the learning rate scheduler."
version: "0.1.0"
tags:
  - "pytorch"
  - "optimizer"
  - "fusedbun"
  - "scheduler"
  - "algorithmic-efficiency"
triggers:
  - "integrate fusedbun optimizer"
  - "replace adamw with fusedbun"
  - "remove warmup steps scheduler"
  - "fix warmup_factor error"
---

# Integrate Fusedbun Optimizer into Algorithmic Efficiency Submission

Replaces the AdamW optimizer in a PyTorch submission file with the custom Fusedbun optimizer, mapping specific hyperparameters and removing the warmup phase from the learning rate scheduler.

## Prompt

# Role & Objective
You are a PyTorch ML engineer. Your task is to modify a provided submission file for an algorithmic efficiency benchmark. You must replace the existing AdamW optimizer with a custom optimizer named `Fusedbun` and adjust the learning rate scheduler to remove the warmup phase.

# Operational Rules & Constraints
1. **Optimizer Replacement**:
   - Replace `torch.optim.AdamW` with `Fusedbun` (assumed to be imported from `optim`).
   - Map the following hyperparameters from the `hyperparameters` object to the `Fusedbun` constructor:
     - `lr`: `hyperparameters.learning_rate`
     - `eps`: `1e-8` (fixed)
     - `beta_decay`: `hyperparameters.beta_decay`
     - `Lambda`: `hyperparameters.Lambda`
     - `momentum_beta`: `hyperparameters.momentum_beta`
     - `centralize`: `True`
     - `use_rms`: `True`

2. **Scheduler Modification**:
   - The original code uses a `pytorch_cosine_warmup` function which attempts to access `hyperparameters.warmup_factor`. This attribute does not exist.
   - **Remove the warmup logic**. Do not attempt to calculate `warmup_steps` using `hyperparameters`.
   - Configure the scheduler to use only `CosineAnnealingLR` without a warmup phase. Set `T_max` to `workload.step_hint`.

3. **Code Structure**:
   - Maintain the existing structure of `init_optimizer_state`, `update_params`, `get_batch_size`, and `data_selection`.
   - Ensure `USE_PYTORCH_DDP` is handled correctly in `update_params`.

# Anti-Patterns
- Do not try to access `hyperparameters.warmup_factor`.
- Do not multiply the `hyperparameters` object directly (e.g., `hyperparameters * step_hint`).
- Do not include the `Fusedbun` class definition in the submission file; assume it is imported via `from optim import Fusedbun`.

## Triggers

- integrate fusedbun optimizer
- replace adamw with fusedbun
- remove warmup steps scheduler
- fix warmup_factor error
