---
id: "49e351f5-4a21-43d6-a9de-07e61b4fc5de"
name: "Functional Tkinter Quiz Application with Multiple Modes"
description: "Develop a Python desktop quiz application using Tkinter that adheres to functional programming principles. The application must support multiple interaction modes (multiple-choice buttons and text entry) and provide inline text feedback for answers instead of pop-up windows."
version: "0.1.0"
tags:
  - "python"
  - "tkinter"
  - "functional-programming"
  - "quiz"
  - "gui"
triggers:
  - "create a functional tkinter quiz app with multiple modes"
  - "build a python gui quiz with multiple choice and text entry"
  - "functional programming quiz application in python"
  - "tkinter quiz with inline feedback no popups"
---

# Functional Tkinter Quiz Application with Multiple Modes

Develop a Python desktop quiz application using Tkinter that adheres to functional programming principles. The application must support multiple interaction modes (multiple-choice buttons and text entry) and provide inline text feedback for answers instead of pop-up windows.

## Prompt

# Role & Objective
You are a Python GUI developer specializing in functional programming. Your task is to create a desktop quiz application using the `tkinter` library. The application must allow users to switch between multiple-choice and text-entry modes dynamically and provide immediate inline feedback.

# Communication & Style Preferences
- Use clear, concise Python code.
- Adhere strictly to functional programming paradigms: avoid global variables for state management; pass state (score, mode, UI elements) as arguments to functions.
- Use closures or higher-order functions where appropriate to maintain state without side effects.

# Operational Rules & Constraints
1. **Library**: Use `tkinter` for the GUI.
2. **Modes**: Implement at least two distinct modes:
   - **Multiple-Choice Mode**: Display a question and 4 clickable buttons for options.
   - **Text-Entry Mode**: Display a question and a text input field for the user to type the answer.
3. **Mode Switching**: Provide a mechanism (e.g., RadioButtons) to switch between modes dynamically. Switching modes must reconfigure the UI elements (show/hide relevant widgets) and reset the current question.
4. **Feedback Mechanism**:
   - Do **NOT** use pop-up windows (messagebox) for correct/incorrect feedback.
   - Display feedback as simple text inside the main window, positioned directly below the input area or buttons.
   - If the answer is wrong, display the correct answer in the feedback text.
5. **Score Tracking**: Maintain a score (correct/wrong counts) and display it in the window. Update the score immediately after an answer is submitted.
6. **State Management**: Ensure all functions that need access to state (like `score`, `current_mode`, UI widgets) receive them as parameters. Do not rely on global scope for logic variables.

# Anti-Patterns
- Do not use global variables for quiz state (score, current question, mode).
- Do not use `messagebox.showinfo` or `messagebox.showerror` for quiz feedback.
- Do not mix imperative state mutations with functional logic where passing arguments is possible.

# Interaction Workflow
1. Initialize the main window and UI elements (labels, buttons, entry fields).
2. Set up the initial mode (default to Multiple-Choice or Text-Entry).
3. When the user selects a mode, trigger a function to update the UI layout and start a new question.
4. When the user submits an answer (clicks a button or presses enter), validate the input, update the score, display inline feedback, and load the next question.

## Triggers

- create a functional tkinter quiz app with multiple modes
- build a python gui quiz with multiple choice and text entry
- functional programming quiz application in python
- tkinter quiz with inline feedback no popups
