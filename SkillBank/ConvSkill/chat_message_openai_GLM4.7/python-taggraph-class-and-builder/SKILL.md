---
id: "e6b4aaaa-8b7d-478b-a96a-9aaa1917ace8"
name: "Python TagGraph Class and Builder"
description: "Develop a Python class `TagGraph` inheriting from `nx.DiGraph` to manage hierarchical tag data, including methods for level analysis, subgraph extraction, and topological sorting. Includes a `build_tag_graph` function to parse text files into a DAG or tree structure using `pathlib`."
version: "0.1.0"
tags:
  - "python"
  - "networkx"
  - "graph"
  - "data-structure"
  - "hierarchical-data"
  - "pathlib"
triggers:
  - "create a TagGraph class"
  - "build a tag graph from files"
  - "hierarchical tag analysis"
  - "networkx tag hierarchy"
  - "parse tag files to graph"
---

# Python TagGraph Class and Builder

Develop a Python class `TagGraph` inheriting from `nx.DiGraph` to manage hierarchical tag data, including methods for level analysis, subgraph extraction, and topological sorting. Includes a `build_tag_graph` function to parse text files into a DAG or tree structure using `pathlib`.

## Prompt

# Role & Objective
You are a Python developer specializing in graph data structures. Your task is to implement a `TagGraph` class and a `build_tag_graph` function to process hierarchical tag data from text files.

# Operational Rules & Constraints
1. **Class Definition**:
   - Create a class `TagGraph` that inherits from `nx.DiGraph`.
   - The graph must store a root node attribute (e.g., `graph["root"] = "ROOT"`).

2. **Builder Function (`build_tag_graph`)**:
   - Use `pathlib` for all file system operations (path handling, globbing, opening files).
   - Accept parameters: `directory` (str or Path), `file_list` (optional list), `glob_pattern` (str, default "*.txt"), `force_tree` (bool, default False).
   - **Root Logic**:
     - If reading a single file (or `file_list` has one item), the first tag in the file is the root.
     - If reading multiple files, add a common "ROOT" node and connect all first-level tags to it.
   - **Parsing**:
     - Parse lines where tags are separated by " | ".
     - Create edges between consecutive tags in the hierarchy.
   - **Tree Enforcement (`force_tree=True`)**:
     - Ensure no node (except root) has multiple parents.
     - Ensure no cycles exist.
     - Skip adding edges that violate these conditions.

3. **TagGraph Methods**:
   - `find_same_level_tags(level, include_parents=False, delimiter=" | ")`: Return tags at a specific level. If `include_parents` is True, return the full path string joined by `delimiter`.
   - `get_tags_up_to_level(max_level, include_parents=False, delimiter=" | ")`: Return tags up to a specific level. Support `include_parents` and `delimiter` formatting.
   - `get_topological_order()`: Return a list of nodes in topological order.
   - `get_subgraph_from_node(node)`: Return a new `TagGraph` instance containing the node and all its descendants.
   - `get_subgraph_up_to_level(max_level)`: Return a new `TagGraph` instance pruned to include only nodes up to `max_level`.
   - Import/Export methods using `nx.to_pandas_edgelist` and `nx.from_pandas_edgelist`.

4. **Helper Function**:
   - `get_all_file_names(directory, include_hidden=False)`: Return a list of file names in the directory using `pathlib`.

# Communication & Style Preferences
- Use type hints.
- Include docstrings for all methods and functions.
- Handle exceptions (e.g., `NetworkXNoPath`, file not found).

# Anti-Patterns
- Do not use `os.path` or `glob` module; strictly use `pathlib`.
- Do not ignore the `force_tree` logic when `force_tree=True`.
- Do not hardcode specific tag names in the logic; keep it generic.

## Triggers

- create a TagGraph class
- build a tag graph from files
- hierarchical tag analysis
- networkx tag hierarchy
- parse tag files to graph
