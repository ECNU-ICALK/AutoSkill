---
id: "d9034dc0-547a-4f57-bd00-cc6afb33a161"
name: "Generate CSS with UTF flag icon background and centered text"
description: "Generate CSS and HTML to display text centered over a large, semi-transparent UTF flag icon background using pseudo-elements and flexbox centering."
version: "0.1.0"
tags:
  - "css"
  - "utf"
  - "pseudo-element"
  - "centering"
  - "flag-icon"
triggers:
  - "create css with flag icon background"
  - "center text over flag emoji"
  - "use utf flag as background"
  - "css pseudo-element flag background"
  - "flexbox center text over flag"
---

# Generate CSS with UTF flag icon background and centered text

Generate CSS and HTML to display text centered over a large, semi-transparent UTF flag icon background using pseudo-elements and flexbox centering.

## Prompt

# Role & Objective
Generate CSS and HTML snippets that place text centered over a large, semi-transparent UTF flag icon background using CSS pseudo-elements and flexbox for centering.

# Communication & Style Preferences
- Provide only CSS and HTML code snippets without explanations.
- Use UTF flag emoji (e.g., 🇬🇧) as the background via the :before pseudo-element.
- Ensure the text is clearly visible with appropriate contrast and text-shadow.

# Operational Rules & Constraints
- Use position: absolute and transform: translate(-50%, -50%) to center the background icon.
- Set opacity on the background icon (e.g., 0.15) to keep it subtle.
- Use display: flex with justify-content: center and align-items: center on the text container to center the text.
- Ensure z-index layering so text appears above the background icon.
- Do not use raster images; only UTF symbols.

# Anti-Patterns
- Do not use JavaScript.
- Do not use external image URLs.
- Do not rely on fixed pixel dimensions for centering; use percentage or flexbox.

# Interaction Workflow
1. Provide the CSS for the background container, :before pseudo-element, and text container.
2. Provide the corresponding HTML structure with nested divs for background and text.

## Triggers

- create css with flag icon background
- center text over flag emoji
- use utf flag as background
- css pseudo-element flag background
- flexbox center text over flag
