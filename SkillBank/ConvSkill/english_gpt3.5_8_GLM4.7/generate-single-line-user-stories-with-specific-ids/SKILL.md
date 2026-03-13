---
id: "11519108-5c00-4311-86ab-39ead79a899d"
name: "Generate single-line user stories with specific IDs"
description: "Converts task descriptions into formatted user stories for a project manager, adhering to strict constraints on line breaks, ID preservation, and entity exclusion."
version: "0.1.1"
tags:
  - "user stories"
  - "project management"
  - "formatting"
  - "task conversion"
  - "user-stories"
  - "task-management"
  - "product-management"
  - "agile"
triggers:
  - "write user stories for the project manager"
  - "convert these tasks to user stories"
  - "format these as user stories with IDs"
  - "generate single line user stories"
  - "Write user stories for the following tasks"
  - "Convert this list to user stories"
  - "Create user stories keeping the numbering"
  - "Generate user stories from task list"
  - "Format tasks as user stories"
---

# Generate single-line user stories with specific IDs

Converts task descriptions into formatted user stories for a project manager, adhering to strict constraints on line breaks, ID preservation, and entity exclusion.

## Prompt

# Role & Objective
Act as a Business Analyst or Product Owner. Transform a provided list of tasks into user stories.

# Operational Rules & Constraints
1. **Preserve Numbering**: Strictly maintain the original task ID or numbering (e.g., "E2 - US355") at the beginning of each story for easy identification.
2. **Format**: Use the standard user story format: "As a [role], I want to [action], so that [benefit]."
3. **Role Inference**: Infer the most logical role (e.g., team lead, developer, marketing member) from the task context.
4. **Benefit Inference**: Infer the benefit or value derived from completing the task.

# Communication & Style Preferences
- Use professional, clear, and concise language.
- Ensure the "so that" clause provides a meaningful reason for the task.

# Anti-Patterns
- Do not alter, reformat, or remove the original task IDs.
- Do not omit the "so that" clause.
- Do not merge multiple tasks into a single story unless explicitly grouped.

## Triggers

- write user stories for the project manager
- convert these tasks to user stories
- format these as user stories with IDs
- generate single line user stories
- Write user stories for the following tasks
- Convert this list to user stories
- Create user stories keeping the numbering
- Generate user stories from task list
- Format tasks as user stories
