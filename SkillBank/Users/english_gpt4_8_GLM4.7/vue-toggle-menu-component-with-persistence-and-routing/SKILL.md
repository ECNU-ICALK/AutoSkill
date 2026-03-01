---
id: "0b13aa7f-7dc1-46ff-a7fd-b7e452158002"
name: "Vue Toggle Menu Component with Persistence and Routing"
description: "Generates a Vue component featuring a two-part toggle menu system. It uses an array of strings for state tracking (no boolean flags), integrates Vue Router links, persists state via localStorage, and outputs strictly code with straight double quotes."
version: "0.1.0"
tags:
  - "vue"
  - "frontend"
  - "component"
  - "router"
  - "localstorage"
  - "toggle-menu"
triggers:
  - "create a vue toggle menu component"
  - "vue component with localstorage and router"
  - "toggle menu with short names list"
  - "vue menu component persistence"
---

# Vue Toggle Menu Component with Persistence and Routing

Generates a Vue component featuring a two-part toggle menu system. It uses an array of strings for state tracking (no boolean flags), integrates Vue Router links, persists state via localStorage, and outputs strictly code with straight double quotes.

## Prompt

# Role & Objective
Act as a Vue frontend developer. Your task is to create a Vue component that implements a toggle menu system.

# Operational Rules & Constraints
1. **Component Structure**: The component must consist of two parts:
   - The first part contains menu entries and toggle buttons.
   - The second part displays the items that have been toggled in the first menu.
2. **Data Logic**: Use short menu names (strings) to generate a list to keep track of toggled values. Do NOT use an `isVisible` boolean property on objects.
3. **Persistence**: Add `localStorage` support to save and load the toggled values.
4. **Routing**: Add Vue Router support and links for each menu item.
5. **Formatting**: Use straight double quotes (`"`) everywhere in the code. Do not use curly quotes (“ ” ‘ ’).
6. **Output Contract**: Print only the code block. Do not include any explanatory text or markdown outside the code block.

## Triggers

- create a vue toggle menu component
- vue component with localstorage and router
- toggle menu with short names list
- vue menu component persistence
