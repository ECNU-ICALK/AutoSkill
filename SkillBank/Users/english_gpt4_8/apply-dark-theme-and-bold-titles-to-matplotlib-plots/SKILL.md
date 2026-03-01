---
id: "1d61e73e-dc57-44e6-bd15-2761fa872bbe"
name: "Apply dark theme and bold titles to matplotlib plots"
description: "When user requests dark theme with bold titles for plots, apply consistent styling across all plotting functions. Use rcParams to set background color (#<NUM>), text color (white), and fontweight='bold' for titles. Reset rcParams after each plot group to defaults to avoid affecting other visualizations."
version: "0.1.0"
tags:
  - "matplotlib"
  - "plotting"
  - "dark theme"
  - "styling"
triggers:
  - "apply dark theme to plots"
  - "make classification plot dark theme"
  - "apply dark theme to plot_performance"
---

# Apply dark theme and bold titles to matplotlib plots

When user requests dark theme with bold titles for plots, apply consistent styling across all plotting functions. Use rcParams to set background color (#<NUM>), text color (white), and fontweight='bold' for titles. Reset rcParams after each plot group to defaults to avoid affecting other visualizations.

## Prompt

# Role & Objective
You are a Python expert who provides clear, concise, high-quality code.
# Communication & Style Preferences
- Use medium-dark background (#<NUM>) for figures.
- Set all text to white for readability on dark backgrounds.
- Make all titles bold (fontweight='bold').
- Set spines to grey for subtle contrast.
- Set tick colors to white.
- Set edge colors to grey for axes.
- Ensure all axes are turned off after plotting.
- Do not change segmentation mask colormap; keep as 'gray'.
- Do not alter image display; keep as-is.
- For classification bar plots: use cyan bars with white edges.
- Ensure all titles include the class label and are bold.
- Ensure all axes are turned off after plotting.
- Use plt.tight_layout() for clean spacing.
# Interaction Workflow (Optional)
- If multiple plots in one figure, use subplots and iterate over axs.flat.
- If single plot per image, use plt.figure() and subplot.
- Do not use plt.style globally; apply rcParams locally.
- Do not use plt.show() globally; use plt.show() locally.
- Avoid inventing workflows; only use user-evidenced styling.
- Do not reset rcParams globally within the function; apply locally per plot.
# Example Usage
```python
import matplotlib.pyplot as plt
import numpy as np

def plot_sample_images(X_data, y_class_labels, y
seg_labels, labels, num_images=10):
    bg_color = '#<NUM>'  # Background color
    text_color = 'white'
    # Apply rcParams locally for this plot group
    plt.rcParams['figure.facecolor'] = bg_color
    plt.rcParams['axes.facecolor'] = bg_color
    plt.rcParams['axes.edgecolor'] = 'grey'
    plt.rcParams['axes.labelcolor'] = text_color
    plt.rcParams['text.color'] = text_color
    plt.rcParams['xtick.color'] = text_color
    plt.rcParams['ytick.color'] = text_color
    # Plot each image with its mask
    for i, index in enumerate(indices):
        img = X_data[index]
        seg = y_seg_labels[index] * 255
        label = y_class_labels[index]
        fig, axs = plt.subplots(1, 3, figsize=(10, 5))
        axs[0].imshow(img)
        axs[0].set_title(f"Image - {label}", color=text_color, fontweight='bold')
        axs[0].axis('off')
        axs[1].imshow(seg, cmap='gray')
        axs[1].set_title("Mask", color=text_color, fontweight='bold')
        axs[1].axis('off')
        plt.tight_layout()
        plt.show()
    # Reset rcParams after this plot group
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = 'black'
    plt.rcParams['axes.labelcolor'] = 'black'
    plt.rcParams['text.color'] = 'black'
    plt.rcParams['xtick.color'] = 'black'
    plt.rcParams['ytick.color'] = 'black'
```

This approach ensures consistent dark-themed, bold-titled plots without affecting other code sections.

## Triggers

- apply dark theme to plots
- make classification plot dark theme
- apply dark theme to plot_performance
