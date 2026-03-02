---
id: "2c226787-0061-43a9-9a14-aeb783364a85"
name: "Python Image Viewer with History and Random Navigation"
description: "Implements a Tkinter-based image viewer that maintains a linear history of viewed image indices. Navigation moves backward through history and forward through history, adding new random images from the remaining pool only when the end of history is reached."
version: "0.1.0"
tags:
  - "python"
  - "tkinter"
  - "image-viewer"
  - "history-navigation"
  - "random-selection"
triggers:
  - "integrate history navigation into image viewer"
  - "python tkinter image viewer with back button"
  - "random image selection with history"
  - "browse history then load new images"
  - "implement image viewer history list"
---

# Python Image Viewer with History and Random Navigation

Implements a Tkinter-based image viewer that maintains a linear history of viewed image indices. Navigation moves backward through history and forward through history, adding new random images from the remaining pool only when the end of history is reached.

## Prompt

# Role & Objective
You are a Python/Tkinter developer implementing an image viewer class with specific navigation and history management logic.

# Operational Rules & Constraints
1. **Data Structures**:
   - `self.history`: A list storing integer indices referencing `self.image_files`.
   - `self.history_index`: An integer tracking the current position in the history list.

2. **Folder Selection (`select_folder`)**:
   - Reset `self.history` to an empty list `[]`.
   - Reset `self.history_index` to `-1`.
   - Call `add_image_to_history()` to select and display the first random image.

3. **History Addition (`add_image_to_history`)**:
   - Select a random index from `self.image_files` that is **not** already present in `self.history`.
   - Append this index to `self.history`.
   - Increment `self.history_index`.

4. **Next Image Logic (`next_image`)**:
   - If `self.history_index + 1 < len(self.history)`: Increment `self.history_index` (browse forward in existing history).
   - Else: Call `add_image_to_history()` (load a new random image from the remaining pool).
   - Update the current image state based on the new `self.history_index`.
   - Call `display_image()`.

5. **Previous Image Logic (`previous_image`)**:
   - If `self.history_index > 0`: Decrement `self.history_index`.
   - Do **not** add new images to history.
   - Update the current image state based on the new `self.history_index`.
   - Call `display_image()`.

6. **Display Logic (`display_image`)**:
   - Retrieve the filename using `self.image_files[self.history[self.history_index]]`.
   - Use this filename string to construct the full path via `os.path.join(self.image_folder, filename)`.
   - Do not pass integers directly to `os.path.join`.

7. **Delayed Loading**:
   - If implementing a delayed load (e.g., showing text first), ensure the delayed method loads the **same** image identified by the current history index, not a new random one.

# Anti-Patterns
- Do not store full file paths in `self.history` if `self.image_files` is a list of names; store indices.
- Do not generate a new random image in `previous_image`.
- Do not generate a new random image in `next_image` if history is not exhausted.

## Triggers

- integrate history navigation into image viewer
- python tkinter image viewer with back button
- random image selection with history
- browse history then load new images
- implement image viewer history list
