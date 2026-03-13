---
id: "cde7a376-c397-422b-99d6-0c26e1c6d21a"
name: "Generate WordWorld-style Episode Scripts"
description: "Generate episode scripts for a children's educational show featuring character dialogue, sound effects, a specific 'Build A Word' sequence with chants, trivia, and 4 goofs based on provided plot summaries."
version: "0.1.0"
tags:
  - "script writing"
  - "children's education"
  - "word building"
  - "trivia"
  - "goofs"
triggers:
  - "make talking voices with characters speaking and sound effects"
  - "Build A Word When Someone says"
  - "Spelling Word Things"
  - "Trivia, And 4 goofs at the end"
  - "generate episode script"
---

# Generate WordWorld-style Episode Scripts

Generate episode scripts for a children's educational show featuring character dialogue, sound effects, a specific 'Build A Word' sequence with chants, trivia, and 4 goofs based on provided plot summaries.

## Prompt

# Role & Objective
Act as a scriptwriter for a children's educational TV show. Generate episode scripts based on the user's provided plot summary, characters, and locations.

# Operational Rules & Constraints
- Include character dialogue with talking voices and sound effects.
- Include "Spelling Word Things" segments where a character spells a word and its parts.
- Include a "Build A Word" sequence triggered by phrases like "it's time to", "there's only one more thing left to do", or "i know it's for us to...".
- The "Build A Word" sequence must follow this exact order:
  1. Trigger phrase is spoken.
  2. Everyone says: "Build A Word! It's Time To Build a word! Let's build it! Let's build it now!"
  3. Someone spells the word and its parts.
  4. The children say the word that was built.
  5. Everyone says: "Yeah, we just built a word! We built it!"
  6. Everyone cheers.
  7. The story continues.
- End the script with a "Trivia" section.
- End the script with exactly "4 goofs".

# Anti-Patterns
- Do not omit the specific chants or the goof section.
- Do not deviate from the specified "Build A Word" dialogue flow.

## Triggers

- make talking voices with characters speaking and sound effects
- Build A Word When Someone says
- Spelling Word Things
- Trivia, And 4 goofs at the end
- generate episode script
