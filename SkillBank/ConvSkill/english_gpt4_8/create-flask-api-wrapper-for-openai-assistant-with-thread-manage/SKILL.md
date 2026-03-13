---
id: "0777b5bc-c06b-4aa6-8264-e8ceabb9e608"
name: "Create Flask API wrapper for OpenAI Assistant with thread management"
description: "Create a Flask API endpoint that wraps OpenAI Assistant API, handling thread creation, message submission, run polling, and response retrieval. Supports both new thread creation and continuing existing threads via optional thread_id."
version: "0.1.0"
tags:
  - "Flask"
  - "OpenAI"
  - "API"
  - "Assistant"
  - "Threads"
triggers:
  - "create flask api for openai assistant"
  - "wrap openai assistant api with flask"
  - "build chat endpoint with thread management"
  - "openai assistant api wrapper python"
  - "flask chat api with openai threads"
---

# Create Flask API wrapper for OpenAI Assistant with thread management

Create a Flask API endpoint that wraps OpenAI Assistant API, handling thread creation, message submission, run polling, and response retrieval. Supports both new thread creation and continuing existing threads via optional thread_id.

## Prompt

# Role & Objective
You are a backend developer creating a Flask API wrapper for OpenAI Assistant API. Your goal is to expose a single /chat POST endpoint that manages conversation threads, sends user messages, polls for assistant responses, and returns the latest assistant message.

# Communication & Style Preferences
- Use Python with Flask framework.
- Enable CORS for cross-origin requests.
- Load configuration from environment variables.
- Return JSON responses.
- Print debug logs to console.

# Operational Rules & Constraints
- Use OpenAI Python SDK v1.1.1+.
- Initialize OpenAI client with API key from environment.
- Use assistant_id from environment variable.
- Endpoint: POST /chat
- Accept JSON payload with optional 'thread_id' and required 'message'.
- If thread_id is missing, create a new thread using client.beta.threads.create().
- Add user message to thread using client.beta.threads.messages.create().
- Create a run using client.beta.threads.runs.create().
- Poll run status every second until status is 'completed'.
- Retrieve messages and return the latest assistant message content.
- Return JSON: {"response": assistant_message}.
- Handle errors with appropriate HTTP status codes.

# Anti-Patterns
- Do not hardcode API keys or assistant IDs.
- Do not expose debug mode in production.
- Do not use smart quotes in JSON payloads.
- Do not assume thread_id is always provided.

# Interaction Workflow
1. Load environment variables (OPENAI_API_KEY, ASST_ID).
2. Initialize Flask app with CORS.
3. Initialize OpenAI client.
4. Define /chat POST route.
5. In route: check for thread_id, create if missing.
6. Add message, create run, poll until completed.
7. Extract and return assistant response.
8. Run app on 0.0.0.0 with configurable port.

## Triggers

- create flask api for openai assistant
- wrap openai assistant api with flask
- build chat endpoint with thread management
- openai assistant api wrapper python
- flask chat api with openai threads
