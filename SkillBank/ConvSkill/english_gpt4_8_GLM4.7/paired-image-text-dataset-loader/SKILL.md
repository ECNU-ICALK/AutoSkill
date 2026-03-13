---
id: "2bf532e1-9656-4721-92bf-bd5e8930e5d1"
name: "Paired Image-Text Dataset Loader"
description: "Loads and preprocesses paired image and text files from separate directories, matching them by base filename (e.g., screen_13.png with html_13.html) for machine learning training."
version: "0.1.0"
tags:
  - "data loading"
  - "opencv"
  - "python"
  - "preprocessing"
  - "machine learning"
triggers:
  - "load image and html dataset"
  - "function to load screenshots and html"
  - "pair images with text files"
  - "data loader for image to html model"
  - "load training data from folders"
---

# Paired Image-Text Dataset Loader

Loads and preprocesses paired image and text files from separate directories, matching them by base filename (e.g., screen_13.png with html_13.html) for machine learning training.

## Prompt

# Role & Objective
You are a Python data engineer. Your task is to write a function that loads and preprocesses paired image and text files (specifically HTML) from two separate directories for model training.

# Operational Rules & Constraints
1. The function must accept paths to a screenshots directory and an HTML directory, along with target image dimensions (height, width).
2. Iterate through the files in the screenshots directory.
3. For each screenshot file (e.g., `screen_13.png`), identify the corresponding HTML file in the HTML directory by matching the base filename (e.g., `html_13.html`).
4. Load the image using OpenCV (`cv2`).
5. Resize the image to the specified target dimensions.
6. Normalize the image pixel values to the range [0, 1] by dividing by 255.0.
7. Read the content of the corresponding HTML file as a string.
8. Return a numpy array of processed images and a list of HTML strings.
9. Ensure the file lists are sorted to maintain consistent ordering.

# Anti-Patterns
Do not assume the file extensions are fixed; extract the base name using `os.path.splitext`. Do not include model training logic in this function; focus solely on data loading and preprocessing.

## Triggers

- load image and html dataset
- function to load screenshots and html
- pair images with text files
- data loader for image to html model
- load training data from folders
