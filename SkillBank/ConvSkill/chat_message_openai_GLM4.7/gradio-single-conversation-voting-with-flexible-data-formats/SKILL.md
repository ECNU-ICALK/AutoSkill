---
id: "2095a787-5c64-4b0a-b03d-84b89ec4b299"
name: "Gradio Single Conversation Voting with Flexible Data Formats"
description: "Modify a Gradio voting app to handle single conversations (upvote/downvote) instead of pairs, supporting flat single-turn, nested single-turn, and multi-turn JSON structures."
version: "0.1.0"
tags:
  - "gradio"
  - "python"
  - "voting-app"
  - "data-parsing"
  - "json-handling"
triggers:
  - "modify gradio app for single conversation voting"
  - "support multiple conversation data formats in gradio"
  - "change voting from pairs to single item"
  - "handle flat and nested json conversations in gradio"
---

# Gradio Single Conversation Voting with Flexible Data Formats

Modify a Gradio voting app to handle single conversations (upvote/downvote) instead of pairs, supporting flat single-turn, nested single-turn, and multi-turn JSON structures.

## Prompt

# Role & Objective
Act as a Python/Gradio developer. Modify a Gradio voting application to handle single conversations instead of conversation pairs. The app must support upvoting and downvoting.

# Operational Rules & Constraints
1. **Data Format Support**: The `update_chatbot` function must handle the following three data formats for each conversation item:
   - **Format 1 (Flat Single-turn)**: Question and answer are direct keys of the item (e.g., `conversation[question_key]` and `conversation[answer_key]`).
   - **Format 2 (Nested Single-turn)**: Question and answer are nested under a specific key (e.g., `conversation[conversation_keys[0]][question_key]`).
   - **Format 3 (Multi-turn)**: The conversation is a list of dictionaries under a specific key (e.g., `conversation[conversation_keys[0]]` containing `[{"role": "user", "content": "xxx"}, ...]`).

2. **Function Preservation**: Retain the original helper function `<TOKEN>` (used for formatting single-turn conversations) and adapt `update_chatbot` to utilize it or handle the list directly.

3. **UI Changes**: Replace the "Left/Right/Tie" voting buttons with "Upvote/Downvote" buttons. Keep "Flag" and "Skip" buttons.

4. **State Management**: Ensure the app handles a single conversation index and updates the single chatbot component upon voting.

# Anti-Patterns
- Do not remove the logic for handling `conversation_keys`.
- Do not assume the data is always a list; check if it is a dictionary or list before processing.

## Triggers

- modify gradio app for single conversation voting
- support multiple conversation data formats in gradio
- change voting from pairs to single item
- handle flat and nested json conversations in gradio
