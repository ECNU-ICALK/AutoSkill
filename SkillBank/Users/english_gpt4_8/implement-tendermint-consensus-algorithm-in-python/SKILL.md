---
id: "28f1cd9a-11d7-43c1-a193-26f56d81a8b0"
name: "Implement Tendermint consensus algorithm in Python"
description: "Create a Python implementation of the Tendermint consensus algorithm with two files: node.py containing Node class with whenStarting, whenReceiving, whenTimeout methods, and simulator.py to run the simulation. Use a secure message queue for communication, implement proper prevote/precommit logic with 2/3+ majority checks, and ensure nodes do not access each other's objects directly."
version: "0.1.0"
tags:
  - "tendermint"
  - "consensus"
  - "blockchain"
  - "python"
  - "distributed systems"
  - "message queue"
triggers:
  - "implement tendermint consensus in python"
  - "create node.py and simulator.py for tendermint"
  - "write tendermint algorithm with message queue"
  - "implement secure tendermint nodes without direct access"
  - "create tendermint simulation with prevote precommit"
---

# Implement Tendermint consensus algorithm in Python

Create a Python implementation of the Tendermint consensus algorithm with two files: node.py containing Node class with whenStarting, whenReceiving, whenTimeout methods, and simulator.py to run the simulation. Use a secure message queue for communication, implement proper prevote/precommit logic with 2/3+ majority checks, and ensure nodes do not access each other's objects directly.

## Prompt

# Role & Objective
You are implementing the Tendermint consensus algorithm in Python. Create two files: node.py and simulator.py. The node.py file contains a Node class that runs on every node with three main functions: whenStarting, whenReceiving, and whenTimeout. The simulator.py file runs the consensus simulation across multiple nodes.

# Communication & Style Preferences
- Use clear print statements for debugging and tracing node states.
- Follow the Tendermint protocol terminology: proposals, prevotes, and precommits.
- Ensure secure communication without direct node object access.

# Operational Rules & Constraints
1. Node class must have exactly three main functions: whenStarting, whenReceiving, whenTimeout.
2. Use a central MessageQueue for inter-node communication to avoid direct object access.
3. Implement proper state transitions: propose -> prevote -> precommit -> finished.
4. Nodes must transition to prevote upon receiving a valid proposal, not just on timeout.
5. Only prevotes and precommits exist; there is no generic 'vote'.
6. Consensus requires 2/3+ majority of total nodes for both prevote and precommit thresholds.
7. Each node must know the total number of nodes but not have direct access to other node objects.
8. Initialize votes_received dictionary properly to avoid None keys.
9. Message format: 'message_type|sender_id|content|vote_type' (vote_type optional).
10. Process messages in a loop until all nodes finish or max iterations reached.

# Anti-Patterns
- Do not use direct node object references for communication.
- Do not implement generic 'vote' function; use separate prevote and precommit functions.
- Do not use fixed thresholds (e.g., >2); always use 2/3+ of total nodes.
- Do not allow None proposals in votes_received dictionary.
- Do not stop simulation after first proposal reception; continue until consensus or timeout.

# Interaction Workflow
1. Initialize MessageQueue and Node objects with total_nodes parameter.
2. Call whenStarting for each node to begin consensus.
3. Process messages from queue in loop until all nodes finish or max iterations.
4. Handle timeouts appropriately to progress consensus.
5. Ensure proper state transitions based on received messages and thresholds.

## Triggers

- implement tendermint consensus in python
- create node.py and simulator.py for tendermint
- write tendermint algorithm with message queue
- implement secure tendermint nodes without direct access
- create tendermint simulation with prevote precommit
