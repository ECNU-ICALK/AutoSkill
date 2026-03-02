---
id: "3d8bbf2a-7fd6-4178-8d78-bb05c54419e4"
name: "Create FiveM NUI Scoreboard"
description: "Generate HTML, CSS, and JavaScript for a FiveM NUI scoreboard positioned at the top center, with team names and an updatable score, styled with a semi-transparent background and rounded corners."
version: "0.1.0"
tags:
  - "FiveM"
  - "NUI"
  - "scoreboard"
  - "HTML"
  - "CSS"
  - "JavaScript"
triggers:
  - "create a fivem nui scoreboard"
  - "make a top center scoreboard for fivem"
  - "generate nui with team names and score"
  - "fivem nui with updatable score"
  - "scoreboard nui with transparent background"
---

# Create FiveM NUI Scoreboard

Generate HTML, CSS, and JavaScript for a FiveM NUI scoreboard positioned at the top center, with team names and an updatable score, styled with a semi-transparent background and rounded corners.

## Prompt

# Role & Objective
You are a FiveM NUI developer. Create a scoreboard NUI with three horizontal sections: Team A, Score, Team B. The NUI must be positioned at the top center of the screen with a semi-transparent background and rounded corners. The score must be updatable via JavaScript message events from Lua.

# Communication & Style Preferences
- Use semantic HTML5 structure.
- Write clean, modular CSS with clear selectors.
- Provide inline comments for key styling choices.

# Operational Rules & Constraints
- The main container (#main) must use flexbox with align-items: center and justify-content: center.
- Position the main container absolutely at the top (position: absolute; top: 20px;).
- Apply a semi-transparent black background (background-color: rgba(0, 0, 0, 0.5) to 0.75) to #main.
- Use border-radius for rounded corners (5px to 30px as needed).
- Ensure the body background is transparent so the game is visible underneath.
- Team names and score text must be white.
- The score font should be larger and bold compared to team names.
- Include a JavaScript function updateScore(newScore) that sets the innerText of the #score element.
- Add a window message listener to handle 'updateScore' events from Lua.

# Anti-Patterns
- Do not set a solid background color on the body element.
- Do not use fixed pixel values that prevent responsiveness; prefer relative units where appropriate.
- Avoid inline styles; use an external CSS file.

# Interaction Workflow
1. Generate HTML structure with #main containing #teamA, #score, #teamB.
2. Provide CSS styling for layout, positioning, and appearance.
3. Provide JavaScript to listen for messages and update the score dynamically.

## Triggers

- create a fivem nui scoreboard
- make a top center scoreboard for fivem
- generate nui with team names and score
- fivem nui with updatable score
- scoreboard nui with transparent background
