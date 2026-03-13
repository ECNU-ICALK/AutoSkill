---
id: "77e710a3-3335-4a55-8158-936de4ff4144"
name: "Python Tkinter CCSDS Packet Viewer"
description: "Create a Python GUI using Tkinter to read and display CCSDS packet data from a file. The GUI must include a menu bar for file selection, a text widget for output, and display packet fields in columns using tabs."
version: "0.1.0"
tags:
  - "python"
  - "tkinter"
  - "gui"
  - "ccsds"
  - "file-viewer"
triggers:
  - "python tkinter ccsds packet viewer"
  - "create gui to display file contents in columns"
  - "tkinter file menu example"
  - "python code for ccsds data display"
  - "gui with file dialog and text widget"
---

# Python Tkinter CCSDS Packet Viewer

Create a Python GUI using Tkinter to read and display CCSDS packet data from a file. The GUI must include a menu bar for file selection, a text widget for output, and display packet fields in columns using tabs.

## Prompt

# Role & Objective
Act as a Python GUI developer. Write a complete, executable Python script using the `tkinter` library to create a file viewer application for CCSDS packets.

# Operational Rules & Constraints
1. **Class Structure**: Define a class `Application` inheriting from `tk.Frame`.
2. **Initialization**: Ensure the constructor is named `__init__` and calls `super().__init__`.
3. **Menu Bar**: Implement a menu bar with a "File" menu containing an "Open" command that triggers a file dialog (`filedialog.askopenfilename`).
4. **File Processing**: Read the selected file line by line. For each line (packet), split the content into fields (e.g., using `split()`) and display them in the output area separated by tabs (`\t`) to create columns.
5. **Output Display**: Use a `tk.Text` widget to display the formatted data. Pack the widget to fill the window (e.g., `side='bottom', expand=True, fill='both'`).
6. **Window Geometry**: Set the initial window size to '800x600' using `root.geometry()`.
7. **Menu Visibility**: Ensure the menu is attached to the master window using `self.master.config(menu=menubar)`.

# Anti-Patterns
- Do not use `name` instead of `__name__` in the main execution block.
- Do not forget to call `mainloop()`.
- Do not define the constructor as `init` instead of `__init__`.

## Triggers

- python tkinter ccsds packet viewer
- create gui to display file contents in columns
- tkinter file menu example
- python code for ccsds data display
- gui with file dialog and text widget
