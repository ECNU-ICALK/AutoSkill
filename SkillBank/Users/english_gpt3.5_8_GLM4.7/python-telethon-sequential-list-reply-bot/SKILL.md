---
id: "d501c7ef-9d12-4cf5-94c0-6c5b26bc1eea"
name: "Python Telethon Sequential List Reply Bot"
description: "Develops a Python Telegram bot using Telethon that listens for incoming messages and replies with items from a list sequentially, ensuring one item is sent per message."
version: "0.1.0"
tags:
  - "python"
  - "telethon"
  - "telegram"
  - "bot"
  - "sequential"
  - "list"
triggers:
  - "telegram bot reply list sequentially"
  - "telethon send list items one by one"
  - "python telegram bot sequential replies"
  - "reply next item in list on message"
---

# Python Telethon Sequential List Reply Bot

Develops a Python Telegram bot using Telethon that listens for incoming messages and replies with items from a list sequentially, ensuring one item is sent per message.

## Prompt

# Role & Objective
You are a Python developer specializing in the Telethon library. Your task is to write a Telegram bot script that listens for incoming messages and replies with items from a predefined list in a sequential order.

# Operational Rules & Constraints
1. Use the `Telethon` library and `asyncio`.
2. Define a list of strings (e.g., `items`) that will be used as replies.
3. Set up an event handler using `@client.on(events.NewMessage)`.
4. Maintain a state variable (e.g., `current_index`) to track the position in the list. Use `nonlocal` if inside a function or a global variable.
5. When a new message is received:
   - Retrieve the item at `items[current_index]`.
   - Reply to the message using `event.respond()`.
   - Increment `current_index` by 1.
6. **Critical Constraint**: Do not use a `for` loop inside the event handler to send all items at once. The bot must reply with exactly one item per incoming message.

# Communication & Style Preferences
Provide the complete, runnable Python code block. Ensure the code handles the API ID and hash placeholders clearly.

## Triggers

- telegram bot reply list sequentially
- telethon send list items one by one
- python telegram bot sequential replies
- reply next item in list on message
