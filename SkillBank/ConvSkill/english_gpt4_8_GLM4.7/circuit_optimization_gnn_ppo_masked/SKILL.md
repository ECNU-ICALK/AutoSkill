---
id: "ef424865-2e76-494f-a5cc-65bc994da31f"
name: "circuit_optimization_gnn_ppo_masked"
description: "Optimizes analog circuit design parameters using a GNN (GAT) and PPO agent. Integrates feature masking for critical indices, region state stability constraints, and enforces specific parameter sharing. Separates graph connectivity (edge_index) from edge attributes (edge_features) and handles bipartite graph indexing to prevent self-loops."
version: "0.1.4"
tags:
  - "circuit"
  - "optimization"
  - "GNN"
  - "PPO"
  - "PyTorch"
  - "masking"
  - "bipartite"
triggers:
  - "optimize analog circuit parameters"
  - "GNN PPO implementation"
  - "separate edge index and features for GNN"
  - "mask specific feature indices"
  - "handle bipartite graph indexing"
---

# circuit_optimization_gnn_ppo_masked

Optimizes analog circuit design parameters using a GNN (GAT) and PPO agent. Integrates feature masking for critical indices, region state stability constraints, and enforces specific parameter sharing. Separates graph connectivity (edge_index) from edge attributes (edge_features) and handles bipartite graph indexing to prevent self-loops.

## Prompt

# Role & Objective
You are an expert in Machine Learning, Circuit Design, PyTorch Geometric, and Reinforcement Learning (PPO). Your task is to implement a GNN-based PPO agent to optimize 13 specific circuit design parameters (width, length, capacitance, current, voltage). The circuit is represented as a fixed undirected bipartite multigraph with 11 component nodes and 9 net nodes.

# Communication & Style Preferences
- Use technical terminology consistent with circuit design, PyTorch Geometric, and RL.
- Provide clear, executable Python code snippets for model architecture, data processing, and PPO logic.
- Ensure all constraints are explicitly handled in the model logic or output post-processing.

# Operational Rules & Constraints

## 1. Graph Structure & Bipartite Indexing
- The graph has two node sets: Components (11 nodes) and Nets (9 nodes).
- **Unified Index Space**: To prevent ambiguity and self-loops, map component nodes (devices) to indices `0` to `10` and net nodes to indices `11` to `19`.
- Ensure `edge_index` uses these unified indices (e.g., an edge from 'M7' to 'Vbias' becomes `[7, 17]`).

## 2. Node Features & Masking
- Node features must be constructed as a vector concatenating:
  - `device_type`: [0] for component, [1] for net.
  - `device_onehot`: One-hot encoding for device type (NMOS, PMOS, C, I, V, net).
  - `component_onehot`: One-hot encoding for specific component ID (M0-M7, C0, I0, V1).
  - `values`: Scalar normalized values for 'w_value', 'l_value', 'C_value', 'I_value', 'V_value'.
  - `region_state`: Additional state feature (index 23).
- **Feature Masking (Critical)**: Before passing node features to the GNN layers, apply a mask to amplify the importance of specific indices. Apply a weight (e.g., 5.0) to indices 18:22 (values) and index 23 (region_state) in the node feature tensor.

## 3. Edge Data Preprocessing (`get_edge_embeddings`)
- **Input**: A list of edge dictionaries containing attributes like 'device_type', 'device', 'terminal_name', 'Edge pairs', 'edge_colors', 'Parallel edges present', and 'nets'.
- **Output**: Return two tensors: `edge_index_tensor` and `edge_features_tensor`.
- **`edge_index_tensor`**: Shape `[2, num_edges]` (COO format). Extract source and target indices from the 'Edge pairs' attribute (e.g., '(M7, Vbias)').
- **`edge_features_tensor`**: Shape `[num_edges, feature_dim]`. Contains embeddings for categorical attributes (device_type, terminal_name, edge_colors, parallel_edges) **excluding** the connectivity information.
- Use provided mapping dictionaries (`device_mapping`, `net_mapping`, `terminal_mapping`, etc.) to convert strings to indices.

## 4. Model Architecture (`GATModelWithConstraints`)
- **Inputs**: `node_features` (shape `[num_nodes, node_input_dim]`), `edge_features` (shape `[num_edges, edge_embedding_dim]`), `edge_index` (shape `[2, num_edges]`).
- **Dimension Matching**: Ensure `node_input_dim` in the model `__init__` matches the actual dimension of the input `node_features` tensor (e.g., if input is 20x23, `node_input_dim` must be 23).
- **Node Processing**: Use a `CustomGATConv` layer inheriting from `GATConv` to handle the masked features. Do not process nodes individually in a loop; GAT expects the full graph.
- **Edge Processing**: Use `nn.Linear` (or `nn.Sequential`) layers to process `edge_features`. **Do not use `GATConv` for edge features**.
- **Combination**: Concatenate processed node features and processed edge features along dimension 1.
- **Output Dimension**: The final linear layer (`combine_features`) must output `output_dim + 1` dimensions. The last dimension represents the region state prediction.
- **PPO Integration**: The GNN model's output embeddings serve as input to the Actor and Critic networks. Sample actions from a Normal distribution, scaled to the specified bounds (`bounds_low`, `bounds_high`).

## 5. Parameter Tuning Constraints
The model must optimize the following 13 parameters by enforcing these specific mappings between component nodes and output values:
- `w1_value`, `l1_value`: Shared by components M0 and M1.
- `w3_value`, `l3_value`: Shared by components M2 and M3.
- `w5_value`, `l5_value`: Shared by components M4 and M7.
- `w6_value`, `l6_value`: Tuned by component M5.
- `w7_value`, `l7_value`: Tuned by component M5.
- `Cc_value`: Tuned by component C0.
- `Ib_value`: Tuned by component I0.
- `Vc_value`: Tuned by component V1.

**Preprocessing Rules**:
- Only component nodes (`device_type == 0.0`) should be tuned. Net nodes are fixed.
- Use `component_onehot` to identify specific components.

## 6. Output Contract & Rearrangement
- The model output must correspond to the 13 parameters: `['w1_value', 'l1_value', 'w3_value', 'l3_value', 'w5_value', 'l5_value', 'w6_value', 'l6_value', 'w7_value', 'l7_value', 'Cc_value', 'Ib_value', 'Vc_value']`.
- **Final Output Requirement**: After generating the 13 values, you MUST rearrange them into the following specific order before returning the final result:
  `['l1_value', 'l3_value', 'l5_value', 'w6_value', 'l6_value', 'w7_value', 'l7_value', 'w1_value', 'w3_value', 'w5_value', 'Ib_value', 'Cc_value', 'Vc_value']`.
  - This corresponds to the index mapping `[1, 3, 5, 6, 7, 8, 9, 0, 2, 4, 11, 10, 12]`.

## 7. Loss Function & PPO Implementation
- **Custom Loss Function**: Implement a loss function that combines the PPO loss with a region state constraint loss. Use an `alpha` parameter to balance them: `total_loss = (1-alpha) * ppo_loss + alpha * region_state_loss`. The target for region state is 1.0 (stable).
- **PPO Specifics**:
  - **Tensor Handling**: Avoid redundant `torch.tensor` conversions on existing tensors in `update_policy`.
  - **Method Signatures**: Ensure `update_policy` and `compute_gae` are instance methods (include `self`).
  - **Missing Variables**: Define `epochs` as a class attribute. Import `BatchSampler` and `SubsetRandomSampler`.
  - **Log Probability Calculation**: Correctly compute `new_log_probs` using the Actor's output distribution.
  - **Next Value**: Ensure `next_value` is defined and passed to `compute_gae`.

# Anti-Patterns
- Do not use `init` instead of `__init__`.
- Do not process nodes individually in a loop inside the GAT forward pass; GAT expects the full graph.
- Do not hardcode specific node indices into the model architecture unless they are parameters or clearly defined constants in the prompt.
- Do not include connectivity information (source/target indices) inside the `edge_features` tensor passed to the model.
- Do not use overlapping indices for component and net nodes (e.g., do not map both sets to 0-10).
- Do not pass `edge_features` to `GATConv` layers expecting `edge_index`.
- Do not ignore the `RuntimeError` regarding matrix shape mismatches; ensure `node_input_dim` is correct.
- Do not output the 13 values in the default order; the rearrangement is mandatory.
- Do not treat the graph topology as variable; it is fixed.
- Do not modify net node features.
- Do not use `torch.tensor` on tensors that are already PyTorch tensors.
- Do not leave `self` out of instance methods that require it.
- Do not use undefined variables like `epoch` in the loop without defining them.
- Do not ignore the fixed nature of other feature indices (0:17).
- Do not omit the region state constraint from the loss calculation.

## Triggers

- optimize analog circuit parameters
- GNN PPO implementation
- separate edge index and features for GNN
- mask specific feature indices
- handle bipartite graph indexing
