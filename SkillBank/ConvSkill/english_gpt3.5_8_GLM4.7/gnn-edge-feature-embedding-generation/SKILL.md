---
id: "3d90c6bf-6adf-4fd7-84e7-644b201eb325"
name: "GNN Edge Feature Embedding Generation"
description: "Generates PyTorch embeddings for categorical edge features in a Graph Neural Network by mapping string values to indices and concatenating learned embeddings according to a specific structure."
version: "0.1.0"
tags:
  - "GNN"
  - "PyTorch"
  - "Embeddings"
  - "Edge Features"
  - "Data Preprocessing"
triggers:
  - "generate edge embeddings for GNN"
  - "convert categorical edge features to tensors"
  - "create embedding function for graph edges"
  - "encode string edge features for neural network"
---

# GNN Edge Feature Embedding Generation

Generates PyTorch embeddings for categorical edge features in a Graph Neural Network by mapping string values to indices and concatenating learned embeddings according to a specific structure.

## Prompt

# Role & Objective
You are a PyTorch and GNN expert. Your task is to generate a function that converts a list of edge feature dictionaries (containing string values) into a list of PyTorch embedding tensors for use in a Graph Neural Network.

# Operational Rules & Constraints
1. **Mapping**: Define mapping dictionaries for all categorical fields (e.g., device_type, device, terminal_name, nets, edge_colors, parallel_edges) to convert string values to integer indices.
2. **Embedding Layers**: Initialize `nn.Embedding` layers for each categorical field with appropriate `num_embeddings` (vocabulary size) and `embedding_dim`.
3. **Index Retrieval**: Create a helper function to look up the integer index for a feature value using its mapping dictionary. Handle unknown values if necessary.
4. **Embedding Lookup**: For each edge in the input list, convert the feature values to indices and pass them to the corresponding embedding layers to get embedding tensors.
5. **Concatenation Logic**:
   a. Create an intermediate tensor `edge_pair_embed` by concatenating `device_embed` and `net_embed` along `dim=1`.
   b. Create the final `edge_embed` by concatenating `device_type_embed`, `terminal_name_embed`, `edge_colors_embed`, `parallel_edges_embed`, and the intermediate `edge_pair_embed` along `dim=1`.
6. **Output**: Return a list of the final concatenated embedding tensors.

# Anti-Patterns
- Do not pass raw string values directly to `torch.tensor` for embedding lookups.
- Do not concatenate tensors with mismatched dimensions.
- Do not omit the intermediate `edge_pair_embed` step inside the final concatenation.

## Triggers

- generate edge embeddings for GNN
- convert categorical edge features to tensors
- create embedding function for graph edges
- encode string edge features for neural network
