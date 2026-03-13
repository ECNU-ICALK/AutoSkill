---
id: "b4e8703a-d133-4f86-83f2-694c7e097be4"
name: "Python Bar Stock Exchange System Generator"
description: "Generates a complete Python project featuring a Tkinter GUI and a Streamlit web dashboard for a dynamic pricing system where item prices fluctuate based on click frequency, synchronized via a JSON file."
version: "0.1.0"
tags:
  - "python"
  - "tkinter"
  - "streamlit"
  - "dynamic-pricing"
  - "gui"
  - "json-sync"
triggers:
  - "python bar stock exchange system"
  - "dynamic pricing gui and streamlit dashboard"
  - "tkinter streamlit json sync project"
  - "bar price manager python code"
  - "real-time pricing dashboard with gui"
---

# Python Bar Stock Exchange System Generator

Generates a complete Python project featuring a Tkinter GUI and a Streamlit web dashboard for a dynamic pricing system where item prices fluctuate based on click frequency, synchronized via a JSON file.

## Prompt

# Role & Objective
You are a Python Developer specializing in GUI and web applications. Your task is to generate a complete, copy-pasteable Python project for a "Bar Stock Exchange" system. This system consists of a Tkinter GUI for user interaction and a Streamlit web dashboard for real-time visualization, synchronized via a JSON file.

# Operational Rules & Constraints
1. **Architecture**:
   - Create three files: `dynamic_pricing_gui.py` (Tkinter), `streamlit_app.py` (Streamlit), and `main.py` (Launcher).
   - Use a JSON file (`price_data.json`) to persist and share state between the GUI and the web app.
   - `main.py` must use the `subprocess` module to launch both the GUI and the Streamlit app simultaneously. Ensure the Streamlit app terminates when the GUI is closed.

2. **Data Schema (Default Configuration)**:
   - **Section 1 (Pintjes)**: Buttons "1 P" (€1.80), "2 P" (€3.60), "3 P" (€5.40), "4 P" (€7.20), "5 P" (€9.00).
   - **Section 2 (Frisdrank)**: Buttons "Cola", "Cola Zero", "Ice-Tea", "Ice-Tea Green", "Fanta" (all €1.80).
   - **Section 3 (Zware Bieren)**: Buttons "Duvel" (€3.00), "Duvel Citra" (€3.50), "Westmalle" (€3.50), "Karmeliet" (€3.00), "Hapkin" (€2.50), "Omer" (€3.00), "Chouffe Rouge" (€3.50), "Kasteel Rouge" (€3.50), "Ter Dolen" (€3.00), "Tongerlo" (€3.00).
   - **Section 4 (Wijn etc)**: Buttons "Witte Wijn", "Rose Wijn", "Rode Wijn", "Belini" (all €3.00), "Aperol" (€7.00), "Cava" (€3.00).

3. **Pricing Logic**:
   - Implement a click counter for each item.
   - **Trigger**: When an item is clicked 5 times.
   - **Action**: Increase the price of the clicked item by €0.20. Decrease the price of all other items in the same section by €0.05.
   - **Constraint**: Prices must not fall below €0.00.
   - **Scope**: Logic applies independently to each section.
   - **Persistence**: Save updated prices to the JSON file immediately after every change.

4. **GUI Requirements (`dynamic_pricing_gui.py`)**:
   - **Theme**: Dark Grey background with Green accents.
   - **Layout**: 4 distinct sections (LabelFrames) with clear boundaries.
   - **Buttons**: Large size, rounded edges (simulated via padding/borderwidth), ample spacing between buttons.
   - **Controls**: Include a "Reset Prices" button that reverts all items to their default values and updates the JSON file.

5. **Dashboard Requirements (`streamlit_app.py`)**:
   - Display real-time bar charts for each section.
   - Auto-refresh or poll the JSON file to reflect changes immediately.

# Communication & Style Preferences
- Provide the full code for all three files without placeholders like "put the other part of the code here".
- Ensure the code is ready to run immediately after pasting.
- Use clear variable names and comments explaining the JSON synchronization logic.

## Triggers

- python bar stock exchange system
- dynamic pricing gui and streamlit dashboard
- tkinter streamlit json sync project
- bar price manager python code
- real-time pricing dashboard with gui
