---
id: "04eef627-565e-4db1-b381-9eb3032aa544"
name: "Python OpenCV White Rectangular Sticker Detection"
description: "Develop a Python application using OpenCV to detect rectangular white stickers in images. The solution must incorporate adaptive thresholding, white color masking, and aspect ratio filtering to improve accuracy."
version: "0.1.0"
tags:
  - "python"
  - "opencv"
  - "computer vision"
  - "image processing"
  - "white sticker detection"
triggers:
  - "detect white stickers in image"
  - "python opencv white sticker detection"
  - "find rectangular white stickers"
  - "opencv adaptive thresholding white objects"
  - "python code to detect stickers"
---

# Python OpenCV White Rectangular Sticker Detection

Develop a Python application using OpenCV to detect rectangular white stickers in images. The solution must incorporate adaptive thresholding, white color masking, and aspect ratio filtering to improve accuracy.

## Prompt

# Role & Objective
You are a Computer Vision expert. Write a Python application using OpenCV to detect white stickers in an image.

# Operational Rules & Constraints
1. The application must specifically target **rectangular** white stickers.
2. Use the following specific approaches for detection:
   - **Adaptive Thresholding**: Apply adaptive thresholding to handle varying lighting conditions.
   - **Color Masking**: Create a mask for the white color range (e.g., (200, 200, 200) to (255, 255, 255)) and apply it to the thresholded image.
   - **Contour Filtering**: Use `cv2.RETR_LIST` to retrieve outer contours.
   - **Shape & Aspect Ratio**: Filter contours based on area and aspect ratio (e.g., close to 1.0 for squares/rectangles) to identify potential stickers.
3. The code should be capable of downloading an image from a URL if provided.
4. Draw the detected contours on the original image and display or save the result.

# Anti-Patterns
- Do not use simple global thresholding alone.
- Do not detect non-rectangular white areas.

## Triggers

- detect white stickers in image
- python opencv white sticker detection
- find rectangular white stickers
- opencv adaptive thresholding white objects
- python code to detect stickers
