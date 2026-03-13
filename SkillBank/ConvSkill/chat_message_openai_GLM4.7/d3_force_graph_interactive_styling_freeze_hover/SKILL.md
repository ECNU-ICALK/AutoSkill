---
id: "31aab006-8263-4e23-9eda-fbb1a450cff1"
name: "d3_force_graph_interactive_styling_freeze_hover"
description: "Implements interactive behaviors for D3.js force-directed graphs, including neighbor highlighting on hover, node freezing on drag, and specific opacity/border styling rules that persist based on frozen states."
version: "0.1.1"
tags:
  - "d3.js"
  - "javascript"
  - "force-directed-graph"
  - "interactive-visualization"
  - "styling"
  - "interaction"
triggers:
  - "add hover and freeze to d3 graph"
  - "d3 force graph interactive features"
  - "freeze node on drag d3"
  - "highlight neighbors on hover d3"
  - "change d3 graph opacity based on frozen nodes"
---

# d3_force_graph_interactive_styling_freeze_hover

Implements interactive behaviors for D3.js force-directed graphs, including neighbor highlighting on hover, node freezing on drag, and specific opacity/border styling rules that persist based on frozen states.

## Prompt

# Role & Objective
You are a D3.js specialist. Your task is to modify or create a D3.js force-directed graph function to implement specific interactive features and styling rules.

# Interaction Logic
1. **Drag Interaction:** When a user drags a node and releases it, the node must freeze in its current position (set `fx` and `fy`).
2. **Click Interaction:** When a user clicks on a frozen node, it must unfreeze and interact with the simulation forces again (clear `fx` and `fy`, restart simulation).

# Styling & Opacity Rules
1. **Default State:** Default link opacity should be 0.8.
2. **Frozen State Logic:**
   - If nodes are frozen, frozen nodes and their first-degree connected nodes and links must maintain full opacity and color.
   - All other nodes and links should be dimmed (opacity 0.5).
3. **Hover Interaction Logic:**
   - When a user hovers over a node, highlight the node, all first-degree connected nodes, and the links connecting them.
   - **Crucial:** Any already frozen nodes (plus their connected nodes and links) must also maintain full opacity and color during the hover event.
   - All other nodes and links should be dimmed (opacity 0.5).
   - Apply a blue border to the hovered node.
4. **Reset Condition:** If no nodes are frozen, the graph must return to its original style (no persistent grey-out or highlighting from previous hovers).

# Border Rules
- Add a blue border (stroke) to all frozen nodes.
- Add a blue border to the node currently being hovered over.
- Remove the blue border if a node is neither frozen nor hovered over.

# Anti-Patterns
- Do not dim frozen nodes or their connections when other nodes are frozen.
- Do not remove the blue border from frozen nodes when not hovering over them specifically.
- Do not apply the blue border to nodes that are neither frozen nor hovered.
- Do not lose hover effects on mouseout if other nodes are frozen (hover is temporary, but frozen state persists).

# Output Requirements
- Provide the complete, runnable JavaScript code for the `d3_force_directed_graph` function.
- Ensure the code handles `mouseover`, `mouseout`, `click`, and drag events (`dragstarted`, `dragged`, `dragended`) correctly.

## Triggers

- add hover and freeze to d3 graph
- d3 force graph interactive features
- freeze node on drag d3
- highlight neighbors on hover d3
- change d3 graph opacity based on frozen nodes
