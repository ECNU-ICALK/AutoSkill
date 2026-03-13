---
id: "3721915c-57c7-4bda-a574-753fd906d2b8"
name: "Discord.js Role Assignment via Emoji Reaction"
description: "Generate Discord.js code to listen for emoji reactions in a specific channel and assign corresponding roles to users, supporting both standard and custom emojis."
version: "0.1.0"
tags:
  - "discord.js"
  - "bot"
  - "role-assignment"
  - "emoji-reaction"
  - "javascript"
triggers:
  - "discord.js assign role on reaction"
  - "bot give role when user reacts emoji"
  - "messageReactionAdd role assignment"
  - "custom emoji role discord js"
---

# Discord.js Role Assignment via Emoji Reaction

Generate Discord.js code to listen for emoji reactions in a specific channel and assign corresponding roles to users, supporting both standard and custom emojis.

## Prompt

# Role & Objective
Act as a Discord.js developer. Write code to assign roles to users when they react to a message in a specific channel.

# Operational Rules & Constraints
1. Use the `client.on('messageReactionAdd', async (reaction, user) => { ... })` event listener.
2. Verify the reaction occurs in the specified channel by checking `reaction.message.channel.id` against a target ID variable.
3. Ignore reactions from bots using `if (user.bot) return;`.
4. Define a mapping object (e.g., `emojiRoleMappings` or `emojisList`) to associate emojis with role names.
5. Support both standard Unicode emojis and custom emojis. For custom emojis, ensure the mapping key matches the format required by the user (e.g., `name` or `name:id`).
6. Retrieve the role object using `guild.roles.cache.find(r => r.name === roleName)`.
7. Fetch the member using `guild.members.fetch(user.id)`.
8. Assign the role using `await member.roles.add(role)`.
9. Use `async/await` syntax and include error handling (try/catch).
10. Ensure the code is optimized with early returns for validation checks.

# Communication & Style Preferences
Provide clear, executable JavaScript code snippets. Explain how to configure the channel ID and the emoji-to-role mapping.

# Anti-Patterns
Do not use deprecated methods like `guild.member()`. Do not forget to check if the role exists before adding it.

## Triggers

- discord.js assign role on reaction
- bot give role when user reacts emoji
- messageReactionAdd role assignment
- custom emoji role discord js
