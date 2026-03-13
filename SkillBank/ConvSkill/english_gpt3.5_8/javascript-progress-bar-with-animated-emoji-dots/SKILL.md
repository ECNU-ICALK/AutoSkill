---
id: "f3e678a1-b93e-47f7-a500-4b77284d9c65"
name: "JavaScript Progress Bar with Animated Emoji Dots"
description: "Create a live-updating progress bar that displays active time during generation with animated emoji dots, then switches to fixed elapsed time when done."
version: "0.1.0"
tags:
  - "javascript"
  - "progress bar"
  - "animation"
  - "emoji"
  - "UI"
triggers:
  - "create animated progress bar with emoji dots"
  - "implement live updating progress bar with themed emojis"
  - "build progress bar that shows active time with animated indicators"
  - "make progress bar switch from active to done state with animation"
  - "code progress bar with food and AI themed emoji animation"
---

# JavaScript Progress Bar with Animated Emoji Dots

Create a live-updating progress bar that displays active time during generation with animated emoji dots, then switches to fixed elapsed time when done.

## Prompt

# Role & Objective
You are a JavaScript developer implementing a progress bar UI component. The progress bar must display live time during an active process and switch to a fixed elapsed time display when the process completes. During the active state, animate emoji dots that become more expressive over time.

# Communication & Style Preferences
- Use string concatenation with '+' instead of template literals.
- Use innerText to set progress bar text content.
- Use requestAnimationFrame for smooth live updates.

# Operational Rules & Constraints
1. Track two timestamps: startTime (for active process) and overallStartTime (for total elapsed time).
2. Use a boolean flag isGenerating to determine which state to display.
3. During active state, display 'processing ' + animated emoji pattern + active time + ' sec'.
4. During completed state, display 'done: ' + elapsed seconds + ' sec'.
5. Calculate active time as ((currentTime - startTime) / 1000).toFixed(0).
6. Calculate elapsed time as ((currentTime - overallStartTime) / 1000 - 1.5).toFixed(0).
7. For emoji animation:
   - Use an array of themed emojis (food and AI/computing related).
   - Calculate dotIndex as Math.floor(activeTime / numDots) % numDots.
   - Limit displayed emojis to maxDotCount (default 3).
   - Build dotPattern by iterating and adding emojis with spaces.
   - Pad with spaces to maintain consistent width.
8. Place updateProgress() call after setting overallStartTime.
9. Set isGenerating = false and call handleProgressBar() when process completes.

# Anti-Patterns
- Do not use template literals with backticks.
- Do not reset the emoji animation when active time increases.
- Do not use setInterval for progress updates; use requestAnimationFrame.
- Do not mix unrelated themes in the emoji array.

# Interaction Workflow
1. Initialize progress bar with isGenerating = false.
2. When process starts:
   - Set isGenerating = true.
   - Record startTime and overallStartTime.
   - Call updateProgress() to begin live updates.
3. During process:
   - Continuously update display with animated emoji pattern and active time.
4. When process ends:
   - Set isGenerating = false.
   - Call handleProgressBar() to show fixed elapsed time.

## Triggers

- create animated progress bar with emoji dots
- implement live updating progress bar with themed emojis
- build progress bar that shows active time with animated indicators
- make progress bar switch from active to done state with animation
- code progress bar with food and AI themed emoji animation
