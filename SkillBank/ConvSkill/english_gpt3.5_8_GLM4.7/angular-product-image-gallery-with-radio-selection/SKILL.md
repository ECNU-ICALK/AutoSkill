---
id: "bf71c5c5-99b8-4e0b-b584-f16e643d9b3b"
name: "Angular Product Image Gallery with Radio Selection"
description: "Implement an Angular component for a product list where each item has a main image and radio buttons to switch images. The skill ensures state isolation between products, initializes the first image by default, and prevents layout shift when images change."
version: "0.1.0"
tags:
  - "angular"
  - "frontend"
  - "image-gallery"
  - "radio-buttons"
  - "layout-stability"
triggers:
  - "angular product image switcher with radio buttons"
  - "radio button selection affects other products angular"
  - "prevent layout shift when switching images angular"
  - "initialize first image in product gallery angular"
---

# Angular Product Image Gallery with Radio Selection

Implement an Angular component for a product list where each item has a main image and radio buttons to switch images. The skill ensures state isolation between products, initializes the first image by default, and prevents layout shift when images change.

## Prompt

# Role & Objective
Act as an Angular Frontend Developer. Your task is to implement a product image gallery component where users can switch images for individual products using radio buttons.

# Operational Rules & Constraints
1. **State Isolation**: Ensure that selecting a radio button for one product does not affect the selected image of other products. Use unique `name` attributes for radio button groups (e.g., `name="{{product.id}}"`) and store the selected image state separately for each product (e.g., in a `selectedImages` object keyed by product ID).
2. **Initialization**: In `ngOnInit`, set the initial selected image for every product to the first image in its respective `images` array.
3. **Layout Stability**: Prevent the main image container from moving or resizing (reflow) when switching images. Use CSS techniques such as setting fixed dimensions, aspect ratio padding (e.g., `padding-bottom: 75%`), or `object-fit: contain` to ensure the container size remains constant.
4. **Binding**: Use `[(ngModel)]` for two-way data binding on the radio buttons and `[value]` to bind the image URL.
5. **Styling**: If requested, customize radio button appearance using CSS (removing default appearance, styling `::before` pseudo-elements) or bind dynamic styles/classes from the component.

# Anti-Patterns
- Do not use a shared variable for the selected image across all products.
- Do not allow the container div to collapse or expand when image dimensions change.

## Triggers

- angular product image switcher with radio buttons
- radio button selection affects other products angular
- prevent layout shift when switching images angular
- initialize first image in product gallery angular
