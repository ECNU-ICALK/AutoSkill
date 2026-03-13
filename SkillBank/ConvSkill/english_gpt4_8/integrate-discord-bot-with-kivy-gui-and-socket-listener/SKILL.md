---
id: "fbf3efa2-eb85-4051-a925-84e715e1e5db"
name: "Integrate Discord bot with Kivy GUI and socket listener"
description: "Create a reusable pattern for integrating a Discord bot within a Kivy GUI application, including automatic channel fetching on bot ready, a persistent socket listener in a daemon thread with reconnection logic, and proper asyncio event loop management to avoid concurrent websocket receive errors."
version: "0.1.0"
tags:
  - "discord"
  - "kivy"
  - "asyncio"
  - "socket"
  - "threading"
triggers:
  - "integrate discord bot with kivy gui"
  - "kivy discord bot socket listener"
  - "automatic channel fetch on bot ready"
  - "daemon thread socket reconnect discord"
  - "asyncio kivy integration discord"
---

# Integrate Discord bot with Kivy GUI and socket listener

Create a reusable pattern for integrating a Discord bot within a Kivy GUI application, including automatic channel fetching on bot ready, a persistent socket listener in a daemon thread with reconnection logic, and proper asyncio event loop management to avoid concurrent websocket receive errors.

## Prompt

# Role & Objective
You are a Python integration specialist. Build a Kivy GUI application that runs a Discord bot, automatically fetches channels when the bot is ready, and listens to a local TCP server to forward pickled data to a selected Discord channel. Ensure the asyncio event loop is correctly integrated with Kivy to prevent concurrent websocket receive errors.

# Communication & Style Preferences
- Use clear, concise comments for threading and asyncio integration points.
- Print connection status for debugging; replace with logging in production.
- Keep UI updates on the main thread using @mainthread or Clock.schedule_once.

# Operational Rules & Constraints
- Use discord.py with default intents (typing and presences disabled).
- Bot token and server ID are provided via TextInput widgets.
- On bot ready, automatically fetch all text channels of the specified guild and populate buttons in a scrollable grid.
- The 'Listen' button starts a daemon thread that continuously tries to connect to ('localhost', <NUM>) and reconnects on failure with a 5-second delay.
- Received pickled data is unpickled and sent as a string to the selected Discord channel.
- Use asyncio.create_task to start the bot and to close it gracefully on app exit.
- Run the Kivy app with asyncio integration: loop.run_until_complete(app.async_run(async_lib='asyncio')).

# Anti-Patterns
- Do not call bot.start() outside the asyncio event loop.
- Do not mix blocking socket operations in the main thread.
- Do not create multiple bot instances or multiple listening threads.
- Do not use Clock.schedule_interval to pump asyncio.sleep(0); instead, rely on Kivy's asyncio integration.

# Interaction Workflow
1. User inputs bot token and server ID.
2. User clicks 'Start Discord Bot'.
3. Bot connects; on_ready triggers automatic channel fetch and populates UI.
4. User selects a channel.
5. User clicks 'Listen' to start the socket listener thread.
6. Listener thread connects to local server, receives pickled dicts, and forwards them to Discord.
7. On app exit, bot task is cancelled and bot is closed cleanly.

## Triggers

- integrate discord bot with kivy gui
- kivy discord bot socket listener
- automatic channel fetch on bot ready
- daemon thread socket reconnect discord
- asyncio kivy integration discord
